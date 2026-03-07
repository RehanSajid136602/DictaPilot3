import Groq from 'groq-sdk';
import { loadDesktopEnv } from 'dictapilot-desktop-shared';

loadDesktopEnv();

const SYSTEM_PROMPT = `
You are a smart dictation editor. Your task is to clean up transcripts and execute voice commands within them.
Rules:
1. Remove filler words (um, uh, ah).
2. Fix glaring grammatical errors.
3. If the user gives a command like "delete that", "new line", "comma", "period", interpret and apply it to the text, do not transcribe the command itself.
4. Output ONLY the final processed text, no explanations, no quotes around it, no extra whitespace.
5. If the text is empty or just noise, return an empty string.
`;

export class EditingService {
    // Basic synchronous heuristic processing for live preview
    process(text: string): string {
        let processed = text;

        const commands: Record<string, string> = {
            'period': '.',
            'comma': ',',
            'new line': '\n',
            'next paragraph': '\n\n',
            'question mark': '?'
        };

        Object.entries(commands).forEach(([command, replacement]) => {
            const regex = new RegExp(`\\s${command}(\\s|$)`, 'gi');
            processed = processed.replace(regex, replacement + ' ');
        });

        processed = processed.trim();
        if (processed.length > 0) {
            processed = processed.charAt(0).toUpperCase() + processed.slice(1);
        }

        return processed;
    }

    // Advanced LLM processing for final output
    async processSmart(text: string): Promise<string> {
        if (!text || text.trim().length === 0) return text;
        const apiKey = process.env.GROQ_API_KEY;
        if (!apiKey) {
            console.warn("GROQ_API_KEY not found, falling back to basic editing.");
            return this.process(text);
        }

        try {
            console.log("LLM Smart Edit starting...");
            const groq = new Groq({ apiKey });
            const chatModel = process.env.GROQ_CHAT_MODEL || 'openai/gpt-oss-120b';
            const completion = await groq.chat.completions.create({
                messages: [
                    { role: 'system', content: SYSTEM_PROMPT },
                    { role: 'user', content: text }
                ],
                model: chatModel,
                temperature: 0.1,
                max_tokens: 2048,
            });

            let result = completion.choices[0]?.message?.content || text;
            result = result.trim();
            console.log("LLM Smart Edit finished.");
            return result;
        } catch (error) {
            console.error("Smart editing failed:", error);
            return this.process(text); // fallback
        }
    }
}

export const editingService = new EditingService();

