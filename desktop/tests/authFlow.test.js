const {
  getOnboardingFormConfig,
  isAuthenticatedState,
  resolveDesktopAuthGateView,
} = require('../shared/dist/authFlow');
const {
  LOADING_AUTH_STATE,
  SIGNED_OUT_AUTH_STATE,
} = require('../shared/dist/auth');

describe('authFlow', () => {
  test('routes first launch without a saved session to onboarding', () => {
    expect(resolveDesktopAuthGateView({ ...SIGNED_OUT_AUTH_STATE })).toBe('onboarding');
  });

  test('routes a restored authenticated session into the app shell', () => {
    expect(resolveDesktopAuthGateView({
      status: 'authenticated',
      user: {
        uid: 'user-123',
        email: 'person@example.com',
        provider: 'password',
        emailVerified: true,
      },
      sync: {
        enabled: true,
        status: 'idle',
        pendingOperations: 0,
        lastSyncedAt: null,
        errorMessage: null,
      },
      errorMessage: null,
    })).toBe('app');
  });

  test('keeps startup in a bootstrapping gate while auth restoration is in progress', () => {
    expect(resolveDesktopAuthGateView({ ...LOADING_AUTH_STATE })).toBe('bootstrapping');
  });

  test('routes sign-out and invalid-session recovery back to onboarding', () => {
    expect(resolveDesktopAuthGateView({
      ...SIGNED_OUT_AUTH_STATE,
      errorMessage: 'Your session expired. Sign in again.',
    })).toBe('onboarding');
  });

  test('returns sign-in form config for the onboarding sign-in path', () => {
    expect(getOnboardingFormConfig('sign-in')).toEqual(expect.objectContaining({
      submitLabel: 'Sign in',
      googleLabel: 'Continue with Google',
      showDisplayName: false,
      showConfirmPassword: false,
    }));
  });

  test('returns sign-up form config for the onboarding registration path', () => {
    expect(getOnboardingFormConfig('sign-up')).toEqual(expect.objectContaining({
      submitLabel: 'Create account',
      googleLabel: 'Continue with Google',
      showDisplayName: true,
      showConfirmPassword: true,
    }));
  });

  test('marks only authenticated auth states as app-ready', () => {
    expect(isAuthenticatedState({ status: 'authenticated' })).toBe(true);
    expect(isAuthenticatedState({ status: 'signed_out' })).toBe(false);
  });
});
