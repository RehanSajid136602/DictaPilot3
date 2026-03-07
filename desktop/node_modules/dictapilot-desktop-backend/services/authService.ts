import { EventEmitter } from 'events';
import {
    DEFAULT_SYNC_PREFERENCES,
    SIGNED_OUT_AUTH_STATE,
    type AuthState,
    type SessionPayload,
    type SignInPayload,
    type SignUpPayload,
    type SyncPreferences,
    type UserIdentity,
} from 'dictapilot-desktop-shared';
import { validateFirebaseProviderConfig } from './firebaseConfigService';

interface FirebaseAuthErrorPayload {
    error?: {
        message?: string;
    };
}

export class AuthServiceError extends Error {
    constructor(public readonly code: string, message: string) {
        super(message);
        this.name = 'AuthServiceError';
    }
}

type AuthResult = {
    session: SessionPayload;
    authState: AuthState;
};

function buildSyncPreferences(): SyncPreferences {
    return { ...DEFAULT_SYNC_PREFERENCES };
}

function buildAuthenticatedState(user: UserIdentity): AuthState {
    return {
        status: 'authenticated',
        user,
        sync: buildSyncPreferences(),
        errorMessage: null,
    };
}

function normalizeTimestamp(expiresInSeconds: string | number): string {
    const ttl = typeof expiresInSeconds === 'string' ? Number.parseInt(expiresInSeconds, 10) : expiresInSeconds;
    return new Date(Date.now() + ttl * 1000).toISOString();
}

async function parseJson<T>(response: Response): Promise<T> {
    return await response.json() as T;
}

export class AuthService extends EventEmitter {
    private currentSession: SessionPayload | null = null;

    getCurrentSession(): SessionPayload | null {
        return this.currentSession;
    }

    getSignedOutState(errorMessage?: string | null): AuthState {
        return {
            ...SIGNED_OUT_AUTH_STATE,
            errorMessage: errorMessage ?? null,
        };
    }

    private getConfig(requireGoogle = false) {
        const validation = validateFirebaseProviderConfig({ requireGoogle });
        if (!validation.valid || !validation.config) {
            throw new AuthServiceError(
                'provider_config_missing',
                `Firebase configuration is incomplete. Missing: ${validation.missing.join(', ')}`
            );
        }
        return validation.config;
    }

    private mapError(code: string): AuthServiceError {
        const messages: Record<string, string> = {
            EMAIL_EXISTS: 'An account with that email already exists.',
            INVALID_EMAIL: 'Enter a valid email address.',
            INVALID_LOGIN_CREDENTIALS: 'Incorrect email or password.',
            MISSING_PASSWORD: 'Password is required.',
            EMAIL_NOT_FOUND: 'No account was found for that email address.',
            USER_DISABLED: 'This account has been disabled.',
            TOO_MANY_ATTEMPTS_TRY_LATER: 'Too many attempts. Try again later.',
            INVALID_IDP_RESPONSE: 'Google sign-in did not return a valid identity response.',
            INVALID_REFRESH_TOKEN: 'Your saved session expired. Sign in again.',
            TOKEN_EXPIRED: 'Your saved session expired. Sign in again.',
            USER_NOT_FOUND: 'This account no longer exists. Sign in again.',
            provider_config_missing: 'Firebase authentication is not configured correctly.',
            confirm_password_mismatch: 'Confirm password must match the password.',
            weak_password: 'Password must be at least 6 characters long.',
            invalid_refresh_token: 'Your saved session expired. Sign in again.',
        };

        return new AuthServiceError(code, messages[code] || 'Authentication failed.');
    }

    private async firebaseJsonRequest<T>(path: string, payload: Record<string, unknown>): Promise<T> {
        const { apiKey } = this.getConfig();
        const response = await fetch(`https://identitytoolkit.googleapis.com/v1/${path}?key=${apiKey}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            const errorPayload = await parseJson<FirebaseAuthErrorPayload>(response);
            throw this.mapError(errorPayload.error?.message || 'unknown_error');
        }

        return await parseJson<T>(response);
    }

    private async refreshRequest(refreshToken: string): Promise<{
        expires_in: string;
        id_token: string;
        refresh_token: string;
        user_id: string;
    }> {
        const { apiKey } = this.getConfig();
        const response = await fetch(`https://securetoken.googleapis.com/v1/token?key=${apiKey}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                grant_type: 'refresh_token',
                refresh_token: refreshToken,
            }),
        });

        if (!response.ok) {
            const errorPayload = await parseJson<FirebaseAuthErrorPayload>(response);
            throw this.mapError(errorPayload.error?.message || 'invalid_refresh_token');
        }

        return await parseJson(response);
    }

    private async lookupUser(idToken: string): Promise<UserIdentity> {
        const payload = await this.firebaseJsonRequest<{
            users: Array<{
                localId: string;
                email: string;
                displayName?: string;
                photoUrl?: string;
                emailVerified?: boolean;
                providerUserInfo?: Array<{ providerId?: string }>;
            }>;
        }>('accounts:lookup', { idToken });

        const user = payload.users?.[0];
        if (!user) {
            throw this.mapError('INVALID_LOGIN_CREDENTIALS');
        }

        const providerId = user.providerUserInfo?.find((item) => item.providerId)?.providerId;
        return {
            uid: user.localId,
            email: user.email,
            displayName: user.displayName,
            photoURL: user.photoUrl,
            provider: providerId === 'google.com' ? 'google' : 'password',
            emailVerified: Boolean(user.emailVerified),
        };
    }

    private finalizeSession(session: SessionPayload): AuthResult {
        this.currentSession = session;
        const authState = buildAuthenticatedState(session.user);
        this.emit('auth-state-changed', authState);
        return { session, authState };
    }

    async signUp(payload: SignUpPayload): Promise<AuthResult> {
        if (payload.password !== payload.confirmPassword) {
            throw this.mapError('confirm_password_mismatch');
        }
        if (payload.password.length < 6) {
            throw this.mapError('weak_password');
        }

        const result = await this.firebaseJsonRequest<{
            idToken: string;
            refreshToken: string;
            expiresIn: string;
        }>('accounts:signUp', {
            email: payload.email,
            password: payload.password,
            returnSecureToken: true,
        });

        let idToken = result.idToken;
        if (payload.displayName?.trim()) {
            const updated = await this.firebaseJsonRequest<{
                idToken: string;
                refreshToken: string;
                expiresIn: string;
            }>('accounts:update', {
                idToken,
                displayName: payload.displayName.trim(),
                returnSecureToken: true,
            });
            idToken = updated.idToken;
        }

        const user = await this.lookupUser(idToken);
        return this.finalizeSession({
            idToken,
            refreshToken: result.refreshToken,
            expiresAt: normalizeTimestamp(result.expiresIn),
            issuedAt: new Date().toISOString(),
            user,
        });
    }

    async signIn(payload: SignInPayload): Promise<AuthResult> {
        const result = await this.firebaseJsonRequest<{
            idToken: string;
            refreshToken: string;
            expiresIn: string;
        }>('accounts:signInWithPassword', {
            email: payload.email,
            password: payload.password,
            returnSecureToken: true,
        });

        const user = await this.lookupUser(result.idToken);
        return this.finalizeSession({
            idToken: result.idToken,
            refreshToken: result.refreshToken,
            expiresAt: normalizeTimestamp(result.expiresIn),
            issuedAt: new Date().toISOString(),
            user,
        });
    }

    async completeGoogleSignIn(tokens: { idToken: string; accessToken?: string }): Promise<AuthResult> {
        this.getConfig(true);
        const postBody = new URLSearchParams({
            id_token: tokens.idToken,
            providerId: 'google.com',
        });

        if (tokens.accessToken) {
            postBody.set('access_token', tokens.accessToken);
        }

        const result = await this.firebaseJsonRequest<{
            idToken: string;
            refreshToken: string;
            expiresIn: string;
        }>('accounts:signInWithIdp', {
            postBody: postBody.toString(),
            requestUri: 'http://localhost',
            returnIdpCredential: true,
            returnSecureToken: true,
        });

        const user = await this.lookupUser(result.idToken);
        return this.finalizeSession({
            idToken: result.idToken,
            refreshToken: result.refreshToken,
            expiresAt: normalizeTimestamp(result.expiresIn),
            issuedAt: new Date().toISOString(),
            user,
        });
    }

    async restoreSession(session: SessionPayload): Promise<AuthResult> {
        const expiresAt = new Date(session.expiresAt).getTime();
        if (Number.isNaN(expiresAt) || expiresAt <= Date.now() + 60_000) {
            return this.refreshSession(session.refreshToken);
        }

        try {
            const user = await this.lookupUser(session.idToken);
            return this.finalizeSession({
                ...session,
                user,
            });
        } catch {
            return this.refreshSession(session.refreshToken);
        }
    }

    async refreshSession(refreshToken: string): Promise<AuthResult> {
        const refreshed = await this.refreshRequest(refreshToken);
        const user = await this.lookupUser(refreshed.id_token);
        return this.finalizeSession({
            idToken: refreshed.id_token,
            refreshToken: refreshed.refresh_token,
            expiresAt: normalizeTimestamp(refreshed.expires_in),
            issuedAt: new Date().toISOString(),
            user,
        });
    }

    signOut(): AuthState {
        this.currentSession = null;
        const authState = this.getSignedOutState();
        this.emit('auth-state-changed', authState);
        return authState;
    }
}

export const authService = new AuthService();
