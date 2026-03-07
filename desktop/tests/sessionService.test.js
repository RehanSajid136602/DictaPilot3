const mockSafeStorage = {
  isEncryptionAvailable: jest.fn(() => true),
  encryptString: jest.fn((value) => Buffer.from(`encrypted:${value}`, 'utf8')),
  decryptString: jest.fn((buffer) => buffer.toString('utf8').replace(/^encrypted:/, '')),
};

const mockSessionStoreService = {
  envelope: null,
  getEnvelope: jest.fn(() => mockSessionStoreService.envelope),
  setEnvelope: jest.fn((value) => {
    mockSessionStoreService.envelope = value;
  }),
};

const mockAuthService = {
  restoreSession: jest.fn(),
};

jest.mock('electron', () => ({
  safeStorage: mockSafeStorage,
}));

jest.mock('../backend/dist/services/storageService', () => ({
  sessionStoreService: mockSessionStoreService,
}));

jest.mock('../backend/dist/services/authService', () => ({
  authService: mockAuthService,
}));

const { SessionService } = require('../backend/dist/services/sessionService');

const sampleSession = {
  idToken: 'id-token',
  refreshToken: 'refresh-token',
  expiresAt: '2030-01-01T00:00:00.000Z',
  issuedAt: '2026-03-07T00:00:00.000Z',
  user: {
    uid: 'user-123',
    email: 'person@example.com',
    provider: 'password',
    emailVerified: true,
  },
};

describe('SessionService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockSessionStoreService.envelope = null;
  });

  test('persists session material through safeStorage encryption', () => {
    const service = new SessionService();

    service.persist(sampleSession);

    expect(mockSafeStorage.encryptString).toHaveBeenCalled();
    expect(mockSessionStoreService.setEnvelope).toHaveBeenCalledWith(expect.objectContaining({
      encrypted: true,
      payload: expect.any(String),
    }));
  });

  test('clears invalid persisted sessions when restore fails', async () => {
    const service = new SessionService();

    mockSessionStoreService.envelope = {
      encrypted: false,
      payload: Buffer.from(JSON.stringify(sampleSession), 'utf8').toString('base64'),
    };
    mockAuthService.restoreSession.mockRejectedValue(new Error('revoked'));

    await expect(service.restore()).resolves.toBeNull();

    expect(mockAuthService.restoreSession).toHaveBeenCalledWith(sampleSession);
    expect(mockSessionStoreService.setEnvelope).toHaveBeenCalledWith(null);
  });

  test('sign-out clear removes the persisted session envelope', () => {
    const service = new SessionService();

    service.clear();

    expect(mockSessionStoreService.setEnvelope).toHaveBeenCalledWith(null);
  });
});
