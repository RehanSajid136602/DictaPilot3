import * as fs from 'fs';
import * as path from 'path';

let hasLoadedDesktopEnv = false;

function parseEnvFile(contents: string): Record<string, string> {
    const parsed: Record<string, string> = {};

    for (const rawLine of contents.split(/\r?\n/)) {
        const line = rawLine.trim();
        if (!line || line.startsWith('#')) {
            continue;
        }

        const separatorIndex = line.indexOf('=');
        if (separatorIndex <= 0) {
            continue;
        }

        const key = line.slice(0, separatorIndex).trim();
        let value = line.slice(separatorIndex + 1).trim();

        if (
            (value.startsWith('"') && value.endsWith('"')) ||
            (value.startsWith("'") && value.endsWith("'"))
        ) {
            value = value.slice(1, -1);
        }

        parsed[key] = value;
    }

    return parsed;
}

function getEnvCandidates(): string[] {
    const resourcesPath = (process as NodeJS.Process & { resourcesPath?: string }).resourcesPath;
    const candidates = [
        process.env.DICTAPILOT_ENV_PATH,
        resourcesPath ? path.join(resourcesPath, '.env') : undefined,
        resourcesPath ? path.join(resourcesPath, 'app.env') : undefined,
        process.execPath ? path.join(path.dirname(process.execPath), '.env') : undefined,
        process.cwd() ? path.join(process.cwd(), '.env') : undefined,
        path.resolve(__dirname, '../../.env'),
        path.resolve(__dirname, '../../../.env'),
        path.resolve(__dirname, '../../../../.env'),
    ];

    return Array.from(new Set(candidates.filter((value): value is string => Boolean(value))));
}

export function loadDesktopEnv(): void {
    if (hasLoadedDesktopEnv) {
        return;
    }
    hasLoadedDesktopEnv = true;

    for (const candidate of getEnvCandidates()) {
        if (!fs.existsSync(candidate)) {
            continue;
        }

        try {
            const parsed = parseEnvFile(fs.readFileSync(candidate, 'utf8'));
            for (const [key, value] of Object.entries(parsed)) {
                if (!process.env[key]) {
                    process.env[key] = value;
                }
            }
            console.log(`Loaded environment from ${candidate}`);
            return;
        } catch (error) {
            console.warn(`Failed to load environment from ${candidate}:`, error);
        }
    }
}
