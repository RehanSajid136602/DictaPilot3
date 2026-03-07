const mockCloudStoreService = {
  upsertSettings: jest.fn(),
  upsertSnippet: jest.fn(),
  tombstoneSnippet: jest.fn(),
  upsertDictionary: jest.fn(),
  tombstoneDictionary: jest.fn(),
  getSettings: jest.fn(),
  listSnippets: jest.fn(),
  listDictionary: jest.fn(),
};

const mockSettingsRepository = {
  getLocal: jest.fn(),
  applyRemote: jest.fn(),
};

const mockSnippetRepository = {
  listLocal: jest.fn(),
  replaceAll: jest.fn(),
};

const mockDictionaryRepository = {
  listLocal: jest.fn(),
  replaceAll: jest.fn(),
};

const mockSyncQueueStoreService = {
  getItems: jest.fn(),
  remove: jest.fn(),
  upsert: jest.fn(),
  getPendingCount: jest.fn(() => 0),
};

const mockAccountProfileService = {
  getProfile: jest.fn(() => null),
};

jest.mock('../backend/dist/services/cloudStoreService', () => ({
  cloudStoreService: mockCloudStoreService,
}));

jest.mock('../backend/dist/services/localRepositoryService', () => ({
  settingsRepository: mockSettingsRepository,
  snippetRepository: mockSnippetRepository,
  dictionaryRepository: mockDictionaryRepository,
}));

jest.mock('../backend/dist/services/storageService', () => ({
  accountProfileService: mockAccountProfileService,
  syncQueueStoreService: mockSyncQueueStoreService,
}));

const { SyncQueueService, chooseWinningMetadata } = require('../backend/dist/services/syncQueueService');

describe('SyncQueueService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockSyncQueueStoreService.getPendingCount.mockReturnValue(0);
    mockCloudStoreService.getSettings.mockResolvedValue(null);
    mockCloudStoreService.listSnippets.mockResolvedValue([]);
    mockCloudStoreService.listDictionary.mockResolvedValue([]);
    mockSnippetRepository.listLocal.mockReturnValue([]);
    mockDictionaryRepository.listLocal.mockReturnValue([]);
  });

  test('prefers the newest sync metadata and breaks ties with higher version', () => {
    const local = {
      id: 'snippet-1',
      updatedAt: '2026-03-07T10:00:00.000Z',
      deviceId: 'device-a',
      version: 2,
      deletedAt: null,
    };
    const remote = {
      id: 'snippet-1',
      updatedAt: '2026-03-07T10:00:00.000Z',
      deviceId: 'device-b',
      version: 3,
      deletedAt: null,
    };

    expect(chooseWinningMetadata(local, remote)).toEqual(remote);
  });

  test('keeps failed queue items with retry metadata for later replay', async () => {
    const service = new SyncQueueService();
    const queueItem = {
      id: 'queue-1',
      domain: 'snippets',
      operation: 'upsert',
      recordId: 'snippet-1',
      payload: {
        id: 'snippet-1',
        trigger: 'addr',
        content: '123 Main St',
      },
      attempts: 0,
      nextAttemptAt: null,
      errorMessage: null,
      metadata: {
        id: 'snippet-1',
        updatedAt: '2026-03-07T10:00:00.000Z',
        deviceId: 'device-a',
        version: 1,
        deletedAt: null,
      },
    };

    mockSyncQueueStoreService.getItems.mockReturnValue([queueItem]);
    mockCloudStoreService.upsertSnippet.mockRejectedValue(new Error('offline'));

    const status = await service.syncNow({ idToken: 'token' });

    expect(mockCloudStoreService.upsertSnippet).toHaveBeenCalled();
    expect(mockSyncQueueStoreService.remove).not.toHaveBeenCalled();
    expect(mockSyncQueueStoreService.upsert).toHaveBeenCalledWith(expect.objectContaining({
      id: 'queue-1',
      attempts: 1,
      errorMessage: 'offline',
      nextAttemptAt: expect.any(String),
    }));
    expect(status.status).toBe('error');
    expect(status.errorMessage).toBe('offline');
  });

  test('hydrates remote tombstones without resurrecting stale local snippets', async () => {
    const service = new SyncQueueService();
    const remoteDeletedSnippet = {
      id: 'snippet-1',
      trigger: '',
      content: '',
      category: '',
      metadata: {
        id: 'snippet-1',
        updatedAt: '2026-03-07T12:00:00.000Z',
        deviceId: 'device-b',
        version: 4,
        deletedAt: '2026-03-07T12:00:00.000Z',
      },
    };

    mockSettingsRepository.getLocal.mockReturnValue({
      id: 'default',
      values: { HOTKEY: 'F9' },
      metadata: {
        id: 'default',
        updatedAt: '2026-03-07T08:00:00.000Z',
        deviceId: 'device-a',
        version: 1,
        deletedAt: null,
      },
    });
    mockCloudStoreService.getSettings.mockResolvedValue({
      id: 'default',
      values: { HOTKEY: 'F10' },
      metadata: {
        id: 'default',
        updatedAt: '2026-03-07T09:00:00.000Z',
        deviceId: 'device-b',
        version: 2,
        deletedAt: null,
      },
    });
    mockSnippetRepository.listLocal.mockReturnValue([{
      id: 'snippet-1',
      trigger: 'addr',
      content: '123 Main St',
      category: 'personal',
      metadata: {
        id: 'snippet-1',
        updatedAt: '2026-03-07T10:00:00.000Z',
        deviceId: 'device-a',
        version: 2,
        deletedAt: null,
      },
    }]);
    mockCloudStoreService.listSnippets.mockResolvedValue([remoteDeletedSnippet]);

    await service.hydrateFromCloud({ idToken: 'token' });

    expect(mockSettingsRepository.applyRemote).toHaveBeenCalledWith(expect.objectContaining({
      values: { HOTKEY: 'F10' },
    }));

    const hydratedSnippets = mockSnippetRepository.replaceAll.mock.calls[0][0];
    expect(hydratedSnippets).toHaveLength(1);
    expect(hydratedSnippets[0]).toEqual(expect.objectContaining({
      id: 'snippet-1',
      metadata: expect.objectContaining({
        deletedAt: '2026-03-07T12:00:00.000Z',
        dirty: false,
      }),
    }));
  });
});
