import Groq from 'groq-sdk';
import { loadDesktopEnv } from 'dictapilot-desktop-shared';

loadDesktopEnv();

export type SmartEditAction = 'append' | 'undo' | 'undo_append' | 'clear' | 'ignore';

export interface SmartEditResult {
    previousText: string;
    updatedText: string;
    displayText: string;
    action: SmartEditAction;
}

interface TranscriptState {
    segments: string[];
    outputText: string;
}

const VALID_ACTIONS = new Set<SmartEditAction>(['append', 'undo', 'undo_append', 'clear', 'ignore']);

const QUESTION_STARTERS = new Set([
    'what', 'why', 'how', 'when', 'where', 'who', 'whom', 'whose', 'which',
    'is', 'are', 'am', 'do', 'does', 'did', 'can', 'could', 'would', 'should',
    'will', 'have', 'has', 'had'
]);

const EXCLAMATION_STARTERS = new Set(['wow', 'great', 'awesome', 'amazing', 'congrats', 'congratulations']);

const STOP_WORDS = new Set([
    'the', 'and', 'for', 'with', 'that', 'this', 'have', 'from', 'your', 'just',
    'really', 'very', 'like', 'then', 'there', 'here', 'what', 'when', 'where',
    'which', 'would', 'could', 'should', 'into', 'about', 'been', 'were', 'they',
    'them', 'their', 'you', 'we', 'he', 'she', 'it', 'my', 'our', 'his', 'her',
    'its', 'not'
]);

const COMMAND_PREFACE_RE = /^(?:(?:oh no|oops|please|hey|ok(?:ay)?|wait|well|uh|um|hmm)\b[\s,\-.:;]*)+/i;
const CONTENT_FILLER_RE = /^(?:(?:uh|um|erm|ah|hmm)\b[\s,\-.:;]*)+/i;
const UNDO_RE = /^(?:delete that|delete previous|undo(?: that)?|scratch that|remove that|remove previous|take that out|erase that|drop that|backspace that)\b(?<rest>.*)$/i;
const CLEAR_RE = /^(?:clear all|clear everything|reset(?: all)?|start over|wipe all|wipe everything|erase all)\b[\s,.!?:;-]*$/i;
const CLEAR_SIMPLE_RE = /^(?:clear|reset|wipe)\b[\s,.!?:;-]*$/i;
const IGNORE_RE = /^(?:don['’]?t include(?: that| this| it)?|do not include(?: that| this| it)?|don['’]?t add(?: that| this| it)?|do not add(?: that| this| it)?|ignore(?: that| this| it)?|skip(?: that| this| it)?|disregard(?: that| this| it)?|omit(?: that| this| it)?|leave (?:that|this|it) out|cancel that|never ?mind(?: that| this| it)?)\b.*$/i;
const IGNORE_TRAILING_RE = /^(?<before>.*?)\b(?:ignore(?: that| this| it)?|skip(?: that| this| it)?|disregard(?: that| this| it)?|omit(?: that| this| it)?|don't include(?: that| this| it)?|do not include(?: that| this| it)?|don't add(?: that| this| it)?|do not add(?: that| this| it)?|never ?mind(?: that| this| it)?)\s*$/i;
const INLINE_CORRECTION_RE = /^\s*(?:(?:oh|uh|um)\s+)*(?:no(?:\s*,?\s*no)*|nope|sorry|i mean|actually)\b[\s,:\-]*/i;
const USE_NOT_USE_INLINE_RE = /\b(?<lemma>use|using)\s+(?<wrong>[A-Za-z0-9][A-Za-z0-9+#.\-]*)\s*,?\s*not\s+\k<wrong>\s*,?\s*(?:(?:use|using|with)\s+)?(?<right>[A-Za-z0-9][A-Za-z0-9+#.\-]*)/gi;
const NEGATION_REPLACEMENT_RE = /^not\s+(?<wrong>[A-Za-z0-9][A-Za-z0-9+#.\-]*)\s*(?:,|\s)*(?:(?:use|using|with|but|instead|rather)\s+)?(?<right>[A-Za-z0-9][A-Za-z0-9+#.\-]*)[.?!]?$/i;
const FILLER_WORD_RE = /\b(?:uh+|um+|erm+|ah+|hmm+|mm+)\b/gi;
const FILLER_PHRASE_RE = /\b(?:you know|i mean|kind of|sort of)\b/gi;
const AGGRESSIVE_FILLER_RE = /\b(?:basically|literally|honestly|actually|like)\b/gi;
const REPEATED_WORD_RE = /\b(?<word>[A-Za-z][A-Za-z0-9']*)\b(?:\s+\k<word>\b)+/gi;
const REPEATED_PUNCT_RE = /([,.;:!?])\1+/g;
const REPLACE_RE = /^(?:replace|change|swap)\s+(?<target>.+?)\s+(?:with|to|for)\s+(?<replacement>.+)$/i;

const SPOKEN_PUNCTUATION: Array<{ pattern: RegExp; replacement: string }> = [
    { pattern: /\bcomma\b/gi, replacement: ',' },
    { pattern: /\bperiod\b/gi, replacement: '.' },
    { pattern: /\bfull stop\b/gi, replacement: '.' },
    { pattern: /\bquestion mark\b/gi, replacement: '?' },
    { pattern: /\bexclamation mark\b/gi, replacement: '!' },
    { pattern: /\bcolon\b/gi, replacement: ':' },
    { pattern: /\bsemicolon\b/gi, replacement: ';' },
];

const PROMPT_ACTIONS = 'append | undo | undo_append | clear | ignore';

const FEW_SHOT_EXAMPLES = [
    {
        currentTranscript: 'Hello world.',
        utterance: 'delete that',
        result: { updated_transcript: '', action: 'undo' as SmartEditAction },
    },
    {
        currentTranscript: 'This is a draft.',
        utterance: 'clear all',
        result: { updated_transcript: '', action: 'clear' as SmartEditAction },
    },
    {
        currentTranscript: 'Keep this sentence.',
        utterance: 'ignore that',
        result: { updated_transcript: 'Keep this sentence.', action: 'ignore' as SmartEditAction },
    },
    {
        currentTranscript: '',
        utterance: 'my name is Rehan. no, no, my name is Numan',
        result: { updated_transcript: 'My name is Numan.', action: 'append' as SmartEditAction },
    },
    {
        currentTranscript: 'Hello world.',
        utterance: 'replace hello with goodbye',
        result: { updated_transcript: 'Goodbye world.', action: 'undo_append' as SmartEditAction },
    },
    {
        currentTranscript: 'Use Twinkler for the GUI.',
        utterance: 'no, not Twinkler, use PyQt6',
        result: { updated_transcript: 'Use PyQt6 for the GUI.', action: 'undo_append' as SmartEditAction },
    },
] as const;

function normalizeSpaces(text: string): string {
    return (text || '').replace(/\s+/g, ' ').trim();
}

function buildPromptMessages(previousText: string, rawText: string) {
    const systemPrompt = [
        'Role and contract:',
        'You are DictaPilot Smart Editor.',
        `Return JSON only with exactly two keys: updated_transcript and action. Valid actions: ${PROMPT_ACTIONS}.`,
        '',
        'Command precedence:',
        'Apply commands in this order when the utterance implies one: clear > ignore > undo > replace > append.',
        'Treat destructive commands conservatively and keep the existing transcript unless the utterance clearly requests a change.',
        '',
        'Cleanup rules:',
        'Remove filler words, repeated words, and obvious dictation noise.',
        'Resolve self-corrections such as "no, no" or "not X, use Y".',
        'Add light punctuation and capitalization when confidence is high.',
        '',
        'Preservation rules:',
        'Preserve names, proper nouns, technical terms, product names, and existing transcript content unless explicitly changed by the utterance.',
        'Do not invent content. Do not summarize. Do not explain.',
        '',
        'Response schema:',
        '{"updated_transcript":"<full transcript after applying the utterance>","action":"append|undo|undo_append|clear|ignore"}',
    ].join('\n');

    const messages: Array<{ role: 'system' | 'user' | 'assistant'; content: string }> = [
        { role: 'system', content: systemPrompt },
    ];

    for (const example of FEW_SHOT_EXAMPLES) {
        messages.push({
            role: 'user',
            content: [
                'Current transcript:',
                '---',
                example.currentTranscript,
                '---',
                '',
                'New utterance:',
                '---',
                example.utterance,
                '---',
            ].join('\n'),
        });
        messages.push({
            role: 'assistant',
            content: JSON.stringify(example.result),
        });
    }

    messages.push({
        role: 'user',
        content: [
            'Current transcript:',
            '---',
            previousText,
            '---',
            '',
            'New utterance:',
            '---',
            rawText,
            '---',
        ].join('\n'),
    });

    return messages;
}

function envFlag(name: string, fallback: string): boolean {
    const value = (process.env[name] || fallback).trim().toLowerCase();
    return !['0', 'false', 'no', 'off'].includes(value);
}

function replaceLastCaseInsensitive(text: string, target: string, replacement: string): string {
    if (!text || !target) {
        return text;
    }

    const pattern = new RegExp(`\\b${escapeRegExp(target)}\\b`, 'gi');
    const matches = [...text.matchAll(pattern)];
    const last = matches[matches.length - 1];
    if (!last || last.index === undefined) {
        return text;
    }

    const start = last.index;
    const end = start + last[0].length;
    return `${text.slice(0, start)}${replacement}${text.slice(end)}`;
}

function stripCommandPreface(text: string): string {
    return normalizeSpaces(text).replace(COMMAND_PREFACE_RE, '').trim();
}

function terminalPunctuation(text: string): string {
    const firstMatch = text.match(/[A-Za-z']+/);
    const firstWord = firstMatch ? firstMatch[0].toLowerCase() : '';
    if (QUESTION_STARTERS.has(firstWord)) {
        return '?';
    }
    if (EXCLAMATION_STARTERS.has(firstWord)) {
        return '!';
    }
    return '.';
}

function capitalizeSentences(text: string): string {
    const chars = [...text];
    let capitalizeNext = true;

    for (let index = 0; index < chars.length; index += 1) {
        if (capitalizeNext && /[A-Za-z]/.test(chars[index])) {
            chars[index] = chars[index].toUpperCase();
            capitalizeNext = false;
        }
        if (['.', '!', '?'].includes(chars[index])) {
            capitalizeNext = true;
        }
    }

    return chars.join('');
}

function toTitleCase(value: string): string {
    return value
        .split(/\s+/)
        .filter(Boolean)
        .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
        .join(' ');
}

function applyProperNameHints(text: string): string {
    let updated = text;

    updated = updated.replace(
        /\b(my name is|this is|i am|i'm)\s+([a-z][a-z'-]*(?:\s+[a-z][a-z'-]*){0,2})\b/gi,
        (_match, intro: string, name: string) => `${intro} ${toTitleCase(name)}`
    );

    updated = updated.replace(
        /\bnot\s+([a-z][a-z'-]*(?:\s+[a-z][a-z'-]*){0,2})\b/gi,
        (_match, name: string) => `not ${toTitleCase(name)}`
    );

    return updated;
}

function applySpokenPunctuation(text: string): string {
    let result = normalizeSpaces(text);

    for (const { pattern, replacement } of SPOKEN_PUNCTUATION) {
        result = result.replace(pattern, replacement);
    }

    result = result.replace(/\s+([,.;:!?])/g, '$1');
    result = result.replace(/([,.;:!?])([^\s])/g, '$1 $2');
    return normalizeSpaces(result);
}

function polishPunctuation(text: string): string {
    let cleaned = applySpokenPunctuation(text);
    if (!cleaned) {
        return '';
    }

    cleaned = cleaned.replace(/\s+([,.;:!?])/g, '$1');
    cleaned = cleaned.replace(/([,.;:!?])([^\s])/g, '$1 $2');
    cleaned = applyProperNameHints(cleaned);
    cleaned = capitalizeSentences(cleaned);

    if (!/[.!?]$/.test(cleaned)) {
        cleaned += terminalPunctuation(cleaned);
    }

    return cleaned;
}

function dedupeRepeatedPhrases(text: string): string {
    return text.replace(
        /\b(?<phrase>\w+(?:\s+\w+){1,3})\b(?:\s+\k<phrase>\b)+/gi,
        (_match, _phrase, _offset, _input, groups: { phrase?: string }) => groups.phrase || ''
    );
}

function cleanupDisfluencies(text: string, aggressive = true): string {
    let cleaned = normalizeSpaces(text);
    if (!cleaned) {
        return '';
    }

    cleaned = cleaned.replace(FILLER_PHRASE_RE, ' ');
    cleaned = cleaned.replace(FILLER_WORD_RE, ' ');
    if (aggressive) {
        cleaned = cleaned.replace(AGGRESSIVE_FILLER_RE, ' ');
    }
    cleaned = cleaned.replace(REPEATED_WORD_RE, (_match, _word, _offset, _input, groups: { word?: string }) => groups.word || '');
    cleaned = cleaned.replace(REPEATED_PUNCT_RE, '$1');
    if (aggressive) {
        cleaned = dedupeRepeatedPhrases(cleaned);
    }

    cleaned = cleaned.replace(/\s+([,.;:!?])/g, '$1');
    cleaned = cleaned.replace(/([,.;:!?])([^\s])/g, '$1 $2');
    return normalizeSpaces(cleaned);
}

function normalizeSegment(text: string): string {
    let cleaned = normalizeSpaces(text);
    cleaned = cleaned.replace(CONTENT_FILLER_RE, '').trim();
    cleaned = cleanupDisfluencies(cleaned, true);
    return polishPunctuation(cleaned);
}

function normalizeInlinePhrase(text: string): string {
    let cleaned = normalizeSpaces(text);
    cleaned = cleaned.replace(CONTENT_FILLER_RE, '').trim();
    cleaned = cleanupDisfluencies(cleaned, true);
    cleaned = applySpokenPunctuation(cleaned);
    cleaned = applyProperNameHints(cleaned);
    return normalizeSpaces(cleaned);
}

function significantTokens(text: string): Set<string> {
    const tokens = (text.toLowerCase().match(/[a-zA-Z0-9']+/g) || [])
        .filter((token) => token.length > 2 && !STOP_WORDS.has(token));
    return new Set(tokens);
}

function rewriteNotUseInline(text: string): string {
    return text.replace(
        USE_NOT_USE_INLINE_RE,
        (_match, lemma: string, _wrong: string, right: string) => `${lemma} ${right}`
    );
}

function rewritePreviousClause(previous: string, correction: string): string | null {
    const match = normalizeSpaces(correction).match(NEGATION_REPLACEMENT_RE);
    if (!match?.groups) {
        return null;
    }

    const rewritten = replaceLastCaseInsensitive(previous, match.groups.wrong || '', match.groups.right || '');
    if (rewritten === previous) {
        return null;
    }

    return normalizeSpaces(rewritten);
}

function applyInlineCorrections(text: string): string {
    const normalized = rewriteNotUseInline(normalizeSpaces(text));
    const clauses = normalized.match(/[^.?!]+[.?!]?/g)?.map((part) => part.trim()).filter(Boolean) || [];
    if (clauses.length === 0) {
        return normalized;
    }

    const corrected: string[] = [];

    for (const clause of clauses) {
        const cleanedClause = normalizeSpaces(clause);
        const markerMatch = cleanedClause.match(INLINE_CORRECTION_RE);
        if (!markerMatch || corrected.length === 0) {
            corrected.push(cleanedClause);
            continue;
        }

        let remainder = normalizeSpaces(cleanedClause.slice(markerMatch[0].length));
        remainder = rewriteNotUseInline(remainder);
        if (!remainder) {
            continue;
        }

        const rewrittenPrevious = rewritePreviousClause(corrected[corrected.length - 1], remainder);
        if (rewrittenPrevious) {
            corrected[corrected.length - 1] = rewrittenPrevious;
            continue;
        }

        const previousTokens = significantTokens(corrected[corrected.length - 1]);
        const remainderTokens = significantTokens(remainder);
        const overlaps = [...remainderTokens].some((token) => previousTokens.has(token));

        if (overlaps) {
            const firstLetterIndex = [...remainder].findIndex((char) => /[A-Za-z]/.test(char));
            if (firstLetterIndex >= 0 && /[a-z]/.test(remainder[firstLetterIndex])) {
                remainder = `${remainder.slice(0, firstLetterIndex)}${remainder[firstLetterIndex].toUpperCase()}${remainder.slice(firstLetterIndex + 1)}`;
            }
            corrected[corrected.length - 1] = remainder;
            continue;
        }

        corrected.push(cleanedClause);
    }

    return normalizeSpaces(rewriteNotUseInline(corrected.join(' ')));
}

function dedupeOverlap(previousText: string, segment: string): string {
    const previousTokens = previousText.split(/\s+/).filter(Boolean);
    const segmentTokens = segment.split(/\s+/).filter(Boolean);
    const maxCheck = Math.min(3, previousTokens.length, segmentTokens.length);

    for (let size = maxCheck; size > 0; size -= 1) {
        const previousTail = previousTokens.slice(-size).join(' ');
        const segmentHead = segmentTokens.slice(0, size).join(' ');
        if (previousTail.toLowerCase() === segmentHead.toLowerCase()) {
            return segmentTokens.slice(size).join(' ').trim();
        }
    }

    return segment;
}

function cleanRemainder(text: string): string {
    let rest = normalizeSpaces(text);
    rest = rest.replace(/^[,.:;!\-\s]+/, '');
    rest = rest.replace(/^(?:and|then|instead)\b[\s,:-]*/i, '');
    rest = rest.replace(/^(?:and\s+)?(?:please\s+)?(?:write|say|type)\b[\s,:-]*/i, '');
    rest = rest.replace(/^(?:and|then)\b[\s,:-]*/i, '');
    return normalizeSegment(rest);
}

function escapeRegExp(text: string): string {
    return text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function extractJsonObject(raw: string): Record<string, unknown> | null {
    const trimmed = raw.trim();
    try {
        const parsed = JSON.parse(trimmed);
        return typeof parsed === 'object' && parsed !== null ? parsed as Record<string, unknown> : null;
    } catch {
        // Continue with substring extraction.
    }

    const start = trimmed.indexOf('{');
    if (start < 0) {
        return null;
    }

    let depth = 0;
    let end = -1;
    for (let index = start; index < trimmed.length; index += 1) {
        if (trimmed[index] === '{') {
            depth += 1;
        } else if (trimmed[index] === '}') {
            depth -= 1;
            if (depth === 0) {
                end = index;
                break;
            }
        }
    }

    if (end < 0) {
        return null;
    }

    try {
        const parsed = JSON.parse(trimmed.slice(start, end + 1));
        return typeof parsed === 'object' && parsed !== null ? parsed as Record<string, unknown> : null;
    } catch {
        return null;
    }
}

function inferAction(previousText: string, updatedText: string): SmartEditAction {
    if (!updatedText) {
        return previousText ? 'clear' : 'ignore';
    }
    if (updatedText === previousText) {
        return 'ignore';
    }
    if (previousText && updatedText.startsWith(previousText)) {
        return 'append';
    }
    if (previousText && previousText.startsWith(updatedText)) {
        return 'undo';
    }
    return 'undo_append';
}

function needsIntentHandling(utterance: string): boolean {
    const normalized = normalizeSpaces(utterance);
    if (!normalized) {
        return false;
    }

    const commandText = stripCommandPreface(normalized);
    return (
        CLEAR_RE.test(commandText) ||
        CLEAR_SIMPLE_RE.test(commandText) ||
        IGNORE_RE.test(commandText) ||
        IGNORE_TRAILING_RE.test(commandText) ||
        UNDO_RE.test(commandText) ||
        REPLACE_RE.test(commandText)
    );
}

function isDeterministicHeuristicCommand(utterance: string): boolean {
    const commandText = stripCommandPreface(utterance);
    return (
        CLEAR_RE.test(commandText) ||
        CLEAR_SIMPLE_RE.test(commandText) ||
        IGNORE_RE.test(commandText) ||
        IGNORE_TRAILING_RE.test(commandText) ||
        UNDO_RE.test(commandText) ||
        REPLACE_RE.test(commandText)
    );
}

export class EditingService {
    private readonly state: TranscriptState = {
        segments: [],
        outputText: '',
    };

    process(text: string): string {
        if (!text || !text.trim()) {
            return '';
        }

        const corrected = applyInlineCorrections(text);
        return normalizeSegment(corrected);
    }

    async processSmart(text: string): Promise<SmartEditResult> {
        const rawText = normalizeSpaces(text);
        const previousText = this.state.outputText;

        if (!rawText) {
            return this.createResult(previousText, previousText, 'ignore');
        }

        const smartEditEnabled = envFlag('SMART_EDIT', '1');
        if (smartEditEnabled && isDeterministicHeuristicCommand(rawText)) {
            return this.applyHeuristic(rawText, true);
        }

        const smartMode = (process.env.SMART_MODE || 'llm').trim().toLowerCase();
        const llmAlwaysClean = envFlag('LLM_ALWAYS_CLEAN', '1');
        const dictationMode = (process.env.DICTATION_MODE || 'accurate').trim().toLowerCase();
        const useLlm =
            smartEditEnabled &&
            smartMode === 'llm' &&
            dictationMode !== 'speed' &&
            !!process.env.GROQ_API_KEY &&
            (dictationMode === 'accurate' || llmAlwaysClean || needsIntentHandling(rawText));

        if (useLlm) {
            const llmResult = await this.processWithLlm(rawText);
            if (llmResult) {
                return llmResult;
            }
        }

        return this.applyHeuristic(rawText, smartEditEnabled);
    }

    private createResult(previousText: string, updatedText: string, action: SmartEditAction): SmartEditResult {
        return {
            previousText,
            updatedText,
            displayText: updatedText,
            action,
        };
    }

    private applyHeuristic(rawText: string, smartEditEnabled: boolean): SmartEditResult {
        const previousText = this.state.outputText;

        if (!smartEditEnabled) {
            const plainSegment = normalizeSegment(rawText);
            if (!plainSegment) {
                return this.createResult(previousText, previousText, 'ignore');
            }

            const dedupedSegment = dedupeOverlap(previousText, plainSegment);
            if (!dedupedSegment) {
                return this.createResult(previousText, previousText, 'ignore');
            }

            this.state.segments.push(dedupedSegment);
            this.state.outputText = normalizeSpaces(this.state.segments.join(' '));
            return this.createResult(previousText, this.state.outputText, 'append');
        }

        const commandText = stripCommandPreface(rawText);

        if (CLEAR_RE.test(commandText) || CLEAR_SIMPLE_RE.test(commandText)) {
            this.state.segments = [];
            this.state.outputText = '';
            return this.createResult(previousText, '', 'clear');
        }

        const replaceMatch = commandText.match(REPLACE_RE);
        if (replaceMatch?.groups) {
            const target = normalizeSpaces(replaceMatch.groups.target || '');
            const replacement = normalizeInlinePhrase(replaceMatch.groups.replacement || '');
            if (!target || !replacement || !this.state.outputText) {
                return this.createResult(previousText, previousText, 'ignore');
            }

            const updatedText = replaceLastCaseInsensitive(this.state.outputText, target, replacement);
            let normalizedUpdatedText = updatedText;
            if (!/[.!?]$/.test(replacement)) {
                const escapedReplacement = escapeRegExp(replacement);
                normalizedUpdatedText = normalizedUpdatedText.replace(
                    new RegExp(`\\b${escapedReplacement}([.!?])\\s+(?=[a-z])`, 'g'),
                    `${replacement} `
                );
            }
            normalizedUpdatedText = polishPunctuation(normalizedUpdatedText);

            if (normalizedUpdatedText === this.state.outputText) {
                return this.createResult(previousText, previousText, 'ignore');
            }

            this.syncSegmentsFromOutput(previousText, normalizedUpdatedText);
            return this.createResult(previousText, normalizedUpdatedText, 'undo_append');
        }

        if (IGNORE_TRAILING_RE.test(commandText) || IGNORE_RE.test(commandText)) {
            return this.createResult(previousText, previousText, 'ignore');
        }

        const undoMatch = commandText.match(UNDO_RE);
        if (undoMatch?.groups) {
            if (this.state.segments.length > 0) {
                this.state.segments.pop();
            }

            const remainder = cleanRemainder(undoMatch.groups.rest || '');
            let action: SmartEditAction = 'undo';
            if (remainder) {
                this.state.segments.push(remainder);
                action = 'undo_append';
            }

            this.state.outputText = normalizeSpaces(this.state.segments.join(' '));
            return this.createResult(previousText, this.state.outputText, action);
        }

        const corrected = applyInlineCorrections(rawText);
        const segment = dedupeOverlap(previousText, normalizeSegment(corrected));
        if (!segment) {
            return this.createResult(previousText, previousText, 'ignore');
        }

        this.state.segments.push(segment);
        this.state.outputText = normalizeSpaces(this.state.segments.join(' '));
        return this.createResult(previousText, this.state.outputText, 'append');
    }

    private syncSegmentsFromOutput(previousText: string, updatedText: string) {
        if (!updatedText) {
            this.state.segments = [];
            this.state.outputText = '';
            return;
        }

        const currentJoined = normalizeSpaces(this.state.segments.join(' '));
        if (currentJoined !== previousText) {
            this.state.segments = previousText ? [previousText] : [];
        }

        if (updatedText.startsWith(previousText)) {
            const inserted = normalizeSpaces(updatedText.slice(previousText.length));
            if (inserted) {
                this.state.segments.push(inserted);
            } else if (this.state.segments.length === 0) {
                this.state.segments = [updatedText];
            }
        } else if (previousText.startsWith(updatedText)) {
            while (this.state.segments.length > 0 && normalizeSpaces(this.state.segments.join(' ')) !== updatedText) {
                this.state.segments.pop();
            }
            if (normalizeSpaces(this.state.segments.join(' ')) !== updatedText) {
                this.state.segments = updatedText ? [updatedText] : [];
            }
        } else {
            this.state.segments = [updatedText];
        }

        this.state.outputText = updatedText;
    }

    private async processWithLlm(rawText: string): Promise<SmartEditResult | null> {
        const apiKey = (process.env.GROQ_API_KEY || '').trim();
        if (!apiKey) {
            return null;
        }

        try {
            const groq = new Groq({ apiKey });
            const chatModel = process.env.GROQ_CHAT_MODEL || 'openai/gpt-oss-120b';
            const previousText = this.state.outputText;
            const request = {
                messages: buildPromptMessages(previousText, rawText),
                model: chatModel,
                temperature: 0,
                response_format: { type: 'json_object' } as never,
                max_tokens: 1024,
            };

            let completion;
            try {
                completion = await groq.chat.completions.create(request);
            } catch (error) {
                const message = String(error || '');
                if (message.includes('json') || message.includes('format') || message.includes('400')) {
                    const fallbackRequest = { ...request };
                    delete (fallbackRequest as { response_format?: { type: string } }).response_format;
                    completion = await groq.chat.completions.create(fallbackRequest);
                } else {
                    throw error;
                }
            }

            const content = completion.choices[0]?.message?.content || '';
            const parsed = extractJsonObject(content);
            if (!parsed) {
                return null;
            }

            const updatedTranscript = typeof parsed.updated_transcript === 'string'
                ? normalizeSpaces(String(parsed.updated_transcript))
                : null;
            if (updatedTranscript === null) {
                return null;
            }

            let action = normalizeSpaces(String(parsed.action || '')).toLowerCase() as SmartEditAction;
            if (!VALID_ACTIONS.has(action)) {
                action = inferAction(previousText, updatedTranscript);
            }

            const normalizedUpdatedText = action === 'clear'
                ? ''
                : action === 'ignore'
                    ? previousText
                    : cleanupDisfluencies(updatedTranscript, true);

            this.syncSegmentsFromOutput(previousText, normalizedUpdatedText);
            return this.createResult(previousText, this.state.outputText, action);
        } catch (error) {
            console.error('Smart editing failed:', error);
            return null;
        }
    }
}

export const editingService = new EditingService();
