import type { AuthState } from './auth';

export type AuthMode = 'sign-in' | 'sign-up';
export type DesktopAuthGateView = 'bootstrapping' | 'onboarding' | 'app';

export interface OnboardingFormConfig {
    title: string;
    description: string;
    submitLabel: string;
    googleLabel: string;
    showDisplayName: boolean;
    showConfirmPassword: boolean;
}

export function isAuthenticatedState(authState: Pick<AuthState, 'status'>): boolean {
    return authState.status === 'authenticated';
}

export function resolveDesktopAuthGateView(authState: Pick<AuthState, 'status'>): DesktopAuthGateView {
    if (authState.status === 'loading') {
        return 'bootstrapping';
    }

    return isAuthenticatedState(authState) ? 'app' : 'onboarding';
}

export function getOnboardingFormConfig(mode: AuthMode): OnboardingFormConfig {
    if (mode === 'sign-up') {
        return {
            title: 'Create your DictaPilot account',
            description: 'Register once to unlock desktop dictation, session restore, and your synced workspace.',
            submitLabel: 'Create account',
            googleLabel: 'Continue with Google',
            showDisplayName: true,
            showConfirmPassword: true,
        };
    }

    return {
        title: 'Sign in to DictaPilot',
        description: 'Use your existing account to resume desktop dictation and pull down your synced workspace.',
        submitLabel: 'Sign in',
        googleLabel: 'Continue with Google',
        showDisplayName: false,
        showConfirmPassword: false,
    };
}
