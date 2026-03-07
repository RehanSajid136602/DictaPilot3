import Store from 'electron-store';

const STORAGE_VERSION = '1.0.0';
const store = new Store({ name: 'dictapilot-data' }) as any;

// Migration stub
const currentVersion = store.get('schema_version', '0.0.0');
if (currentVersion !== STORAGE_VERSION) {
    console.log(`Migrating storage from ${currentVersion} to ${STORAGE_VERSION}`);
    store.set('schema_version', STORAGE_VERSION);
}

export class HistoryService {
    saveResult(text: string) {
        const history = store.get('history', []) as any[];
        history.unshift({
            id: Date.now().toString(),
            text,
            timestamp: new Date().toISOString()
        });
        store.set('history', history.slice(0, 100)); // Keep last 100
    }

    getHistory() {
        return store.get('history', []);
    }
}

export class SettingsService {
    getSettings() {
        return store.get('settings', { hotkey: 'F9', model: 'default' });
    }

    updateSettings(settings: any) {
        const current = this.getSettings();
        store.set('settings', { ...current, ...settings });
    }
}

export const historyService = new HistoryService();
export const settingsService = new SettingsService();
