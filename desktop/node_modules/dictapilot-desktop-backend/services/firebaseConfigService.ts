import { loadDesktopEnv } from 'dictapilot-desktop-shared';

loadDesktopEnv();

export interface FirebaseProviderConfig {
    apiKey: string;
    projectId: string;
    authDomain: string;
    googleClientId?: string;
}

export interface ProviderValidationResult {
    valid: boolean;
    config: FirebaseProviderConfig | null;
    missing: string[];
}

function readEnv(name: string): string {
    return (process.env[name] || '').trim();
}

export function getFirebaseProviderConfig(): FirebaseProviderConfig {
    return {
        apiKey: readEnv('FIREBASE_API_KEY'),
        projectId: readEnv('FIREBASE_PROJECT_ID'),
        authDomain: readEnv('FIREBASE_AUTH_DOMAIN'),
        googleClientId: readEnv('GOOGLE_OAUTH_CLIENT_ID') || undefined,
    };
}

export function validateFirebaseProviderConfig(options?: { requireGoogle?: boolean }): ProviderValidationResult {
    const config = getFirebaseProviderConfig();
    const missing = ['FIREBASE_API_KEY', 'FIREBASE_PROJECT_ID', 'FIREBASE_AUTH_DOMAIN']
        .filter((key) => !readEnv(key));

    if (options?.requireGoogle && !config.googleClientId) {
        missing.push('GOOGLE_OAUTH_CLIENT_ID');
    }

    return {
        valid: missing.length === 0,
        config: missing.length === 0 ? config : null,
        missing,
    };
}
