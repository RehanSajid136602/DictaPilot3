import { createHash, randomBytes } from 'crypto';
import { createServer } from 'http';
import type { AddressInfo } from 'net';
import { shell } from 'electron';
import { validateFirebaseProviderConfig } from 'dictapilot-desktop-backend';

function base64Url(input: Buffer): string {
    return input.toString('base64').replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/g, '');
}

function htmlResponse(title: string, description: string): string {
    return `<!doctype html><html><head><meta charset="utf-8"><title>${title}</title></head><body style="font-family:Segoe UI,sans-serif;background:#0f1115;color:#fff;padding:32px"><h1>${title}</h1><p>${description}</p><p>You can close this window and return to DictaPilot.</p></body></html>`;
}

export async function startGoogleOAuthPkce(timeoutMs = 120_000): Promise<{ idToken: string; accessToken?: string }> {
    const validation = validateFirebaseProviderConfig({ requireGoogle: true });
    if (!validation.valid || !validation.config?.googleClientId) {
        throw new Error(`Google sign-in is not configured. Missing: ${validation.missing.join(', ')}`);
    }

    const codeVerifier = base64Url(randomBytes(32));
    const codeChallenge = base64Url(createHash('sha256').update(codeVerifier).digest());
    const state = base64Url(randomBytes(16));

    const server = createServer();

    const callbackPromise = new Promise<{ code: string }>((resolve, reject) => {
        const timeout = setTimeout(() => {
            server.close();
            reject(new Error('Google sign-in timed out.'));
        }, timeoutMs);

        server.on('request', (request, response) => {
            try {
                const url = new URL(request.url || '/', 'http://127.0.0.1');
                const responseState = url.searchParams.get('state');
                const code = url.searchParams.get('code');
                const error = url.searchParams.get('error');

                if (error) {
                    response.writeHead(200, { 'Content-Type': 'text/html' });
                    response.end(htmlResponse('Sign-in cancelled', 'Google sign-in was cancelled or denied.'));
                    clearTimeout(timeout);
                    server.close();
                    reject(new Error(error));
                    return;
                }

                if (!code || responseState !== state) {
                    response.writeHead(400, { 'Content-Type': 'text/html' });
                    response.end(htmlResponse('Sign-in failed', 'The Google sign-in callback was invalid.'));
                    clearTimeout(timeout);
                    server.close();
                    reject(new Error('Invalid Google OAuth callback.'));
                    return;
                }

                response.writeHead(200, { 'Content-Type': 'text/html' });
                response.end(htmlResponse('Sign-in complete', 'Google sign-in succeeded.'));
                clearTimeout(timeout);
                server.close();
                resolve({ code });
            } catch (error) {
                clearTimeout(timeout);
                server.close();
                reject(error);
            }
        });
    });

    await new Promise<void>((resolve, reject) => {
        server.listen(0, '127.0.0.1', () => resolve());
        server.on('error', reject);
    });

    const address = server.address() as AddressInfo | null;
    if (!address) {
        throw new Error('Failed to start Google OAuth callback listener.');
    }

    const redirectUri = `http://127.0.0.1:${address.port}/oauth/google/callback`;
    const authUrl = new URL('https://accounts.google.com/o/oauth2/v2/auth');
    authUrl.searchParams.set('client_id', validation.config.googleClientId);
    authUrl.searchParams.set('redirect_uri', redirectUri);
    authUrl.searchParams.set('response_type', 'code');
    authUrl.searchParams.set('scope', 'openid email profile');
    authUrl.searchParams.set('state', state);
    authUrl.searchParams.set('code_challenge', codeChallenge);
    authUrl.searchParams.set('code_challenge_method', 'S256');
    authUrl.searchParams.set('access_type', 'offline');
    authUrl.searchParams.set('prompt', 'consent');

    await shell.openExternal(authUrl.toString());
    const callback = await callbackPromise;

    const tokenResponse = await fetch('https://oauth2.googleapis.com/token', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            client_id: validation.config.googleClientId,
            code: callback.code,
            code_verifier: codeVerifier,
            grant_type: 'authorization_code',
            redirect_uri: redirectUri,
        }),
    });

    if (!tokenResponse.ok) {
        throw new Error(await tokenResponse.text() || 'Failed to exchange Google OAuth code.');
    }

    const payload = await tokenResponse.json() as { id_token?: string; access_token?: string };
    if (!payload.id_token) {
        throw new Error('Google sign-in response did not include an ID token.');
    }

    return {
        idToken: payload.id_token,
        accessToken: payload.access_token,
    };
}
