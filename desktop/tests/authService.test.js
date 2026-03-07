const mockValidateFirebaseProviderConfig = jest.fn(() => ({
  valid: true,
  config: {
    apiKey: 'firebase-api-key',
    projectId: 'dictapilot-dev',
    authDomain: 'dictapilot-dev.firebaseapp.com',
    googleClientId: 'desktop-client-id',
  },
  missing: [],
}));

jest.mock('../backend/dist/services/firebaseConfigService', () => ({
  validateFirebaseProviderConfig: (...args) => mockValidateFirebaseProviderConfig(...args),
}));

const { AuthService, AuthServiceError } = require('../backend/dist/services/authService');

function jsonResponse(payload, ok = true) {
  return {
    ok,
    json: jest.fn().mockResolvedValue(payload),
    text: jest.fn().mockResolvedValue(JSON.stringify(payload)),
  };
}

describe('AuthService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    global.fetch = jest.fn();
  });

  afterEach(() => {
    delete global.fetch;
  });

  test('rejects mismatched confirm password before calling Firebase', async () => {
    const service = new AuthService();

    await expect(service.signUp({
      email: 'person@example.com',
      password: 'secret123',
      confirmPassword: 'different123',
      displayName: 'Person',
    })).rejects.toMatchObject({
      code: 'confirm_password_mismatch',
      message: 'Confirm password must match the password.',
    });

    expect(global.fetch).not.toHaveBeenCalled();
  });

  test('creates an authenticated session for valid email sign-in', async () => {
    const service = new AuthService();

    global.fetch
      .mockResolvedValueOnce(jsonResponse({
        idToken: 'id-token',
        refreshToken: 'refresh-token',
        expiresIn: '3600',
      }))
      .mockResolvedValueOnce(jsonResponse({
        users: [{
          localId: 'user-123',
          email: 'person@example.com',
          displayName: 'Person',
          emailVerified: true,
          providerUserInfo: [{ providerId: 'password' }],
        }],
      }));

    const result = await service.signIn({
      email: 'person@example.com',
      password: 'secret123',
    });

    expect(global.fetch).toHaveBeenCalledTimes(2);
    expect(result.session).toEqual(expect.objectContaining({
      idToken: 'id-token',
      refreshToken: 'refresh-token',
      user: expect.objectContaining({
        uid: 'user-123',
        email: 'person@example.com',
        provider: 'password',
        emailVerified: true,
      }),
    }));
    expect(result.authState.status).toBe('authenticated');
  });

  test('maps Firebase credential failures to actionable auth errors', async () => {
    const service = new AuthService();

    global.fetch.mockResolvedValueOnce(jsonResponse({
      error: { message: 'INVALID_LOGIN_CREDENTIALS' },
    }, false));

    await expect(service.signIn({
      email: 'person@example.com',
      password: 'wrong',
    })).rejects.toEqual(expect.objectContaining({
      code: 'INVALID_LOGIN_CREDENTIALS',
      message: 'Incorrect email or password.',
    }));
  });
});
