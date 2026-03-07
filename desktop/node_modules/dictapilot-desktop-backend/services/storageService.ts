import Store from 'electron-store';
import { DesktopSettings, getDefaultDesktopSettings, loadDesktopEnv } from 'dictapilot-desktop-shared';

const STORAGE_VERSION = '1.0.0';
const store = new Store({ name: 'dictapilot-data' }) as any;
loadDesktopEnv();

// Migration stub
const currentVersion = store.get('schema_version', '0.0.0');
if (currentVersion !== STORAGE_VERSION) {
    console.log(`Migrating storage from ${currentVersion} to ${STORAGE_VERSION}`);
    store.set('schema_version', STORAGE_VERSION);
}

function migrateLegacySettings(raw: Record<string, any>): DesktopSettings {
    const migrated = { ...raw } as DesktopSettings;

    if (typeof raw.hotkey === 'string' && !migrated.HOTKEY) {
        migrated.HOTKEY = raw.hotkey;
    }

    delete (migrated as Record<string, any>).hotkey;
    delete (migrated as Record<string, any>).model;

    return migrated;
}

function normalizeSettings(settings: Record<string, string | undefined>): DesktopSettings {
    const normalized: DesktopSettings = {};

    for (const [key, value] of Object.entries(settings)) {
        normalized[key] = value ?? '';
    }

    return normalized;
}

function applySettingsToEnv(settings: DesktopSettings) {
    for (const [key, value] of Object.entries(settings)) {
        if (value === '') {
            delete process.env[key];
            continue;
        }

        process.env[key] = value;
    }
}

function getMergedSettings(): DesktopSettings {
    const defaults = getDefaultDesktopSettings(process.env);
    const stored = migrateLegacySettings(store.get('settings', {}) as Record<string, any>);
    return { ...defaults, ...stored };
}

applySettingsToEnv(getMergedSettings());

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
    getSettings(): DesktopSettings {
        const settings = getMergedSettings();
        applySettingsToEnv(settings);
        return settings;
    }

    updateSettings(settings: Partial<DesktopSettings>) {
        const current = this.getSettings();
        const next = normalizeSettings({ ...current, ...settings });
        store.set('settings', next);
        applySettingsToEnv(next);
    }
}

export const historyService = new HistoryService();
export const settingsService = new SettingsService();
