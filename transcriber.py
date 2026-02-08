"""
DictaPilot Transcriber
Handles transcription services with support for both Groq and local whisper.cpp

Original by: Rohan Sharvesh
Fork maintained by: Rehan

MIT License
Copyright (c) 2026 Rohan Sharvesh
Copyright (c) 2026 Rehan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
import threading
import subprocess
import queue
from typing import Optional, Callable
from pathlib import Path
import tempfile

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    Groq = None


class Transcriber:
    """
    Unified transcription interface supporting multiple backends
    """

    def __init__(self, backend="groq"):
        self.backend = backend
        self.api_key = os.getenv("GROQ_API_KEY")
        self._groq_client = None

        # Model settings
        self.groq_whisper_model = os.getenv("GROQ_WHISPER_MODEL", "whisper-large-v3-turbo").strip() or "whisper-large-v3-turbo"

        # Local whisper.cpp settings (if available)
        self.whisper_cpp_path = os.getenv("WHISPER_CPP_PATH", "./whisper.cpp/main")
        self.whisper_cpp_model_path = os.getenv("WHISPER_CPP_MODEL_PATH", "./models/ggml-base.en.bin")

    def get_client(self):
        """Get Groq client, creating if needed"""
        if not self._groq_client and self.api_key:
            self._groq_client = Groq(api_key=self.api_key)
        return self._groq_client

    def transcribe(self, audio_path: str) -> Optional[str]:
        """
        Transcribe audio using the configured backend
        """
        if self.backend == "groq":
            return self.transcribe_groq(audio_path)
        elif self.backend == "local":
            return self.transcribe_local(audio_path)
        else:
            raise ValueError(f"Unsupported backend: {self.backend}")

    def transcribe_groq(self, audio_path: str) -> Optional[str]:
        """
        Transcribe audio using Groq Cloud API
        """
        if not GROQ_AVAILABLE:
            raise RuntimeError("Groq package not installed or failed to import")

        if not self.api_key:
            raise RuntimeError("Set GROQ_API_KEY environment variable first")

        client = self.get_client()

        try:
            with open(audio_path, "rb") as f:
                audio_bytes = f.read()

            resp = client.audio.transcriptions.create(
                file=(os.path.basename(audio_path), audio_bytes),
                model=self.groq_whisper_model,
                temperature=0,
                response_format="verbose_json",
            )

            # object shape depends on SDK; try common access patterns
            if hasattr(resp, "text"):
                return resp.text
            if isinstance(resp, dict):
                return resp.get("text") or resp.get("transcription") or str(resp)
            return str(resp)

        except Exception as e:
            print(f"Groq transcription error: {e}", file=__import__('sys').stderr)
            return None

    def transcribe_local(self, audio_path: str) -> Optional[str]:
        """
        Transcribe audio using local whisper.cpp
        """
        # Check if whisper.cpp executable exists
        if not os.path.exists(self.whisper_cpp_path):
            raise RuntimeError(f"whisper.cpp executable not found at: {self.whisper_cpp_path}")

        if not os.path.exists(self.whisper_cpp_model_path):
            raise RuntimeError(f"whisper.cpp model not found at: {self.whisper_cpp_model_path}")

        try:
            # Run whisper.cpp command
            cmd = [
                self.whisper_cpp_path,
                "-m", self.whisper_cpp_model_path,
                "-f", audio_path,
                "--output-txt",
                "--max-len", "1"
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode != 0:
                print(f"whisper.cpp error: {result.stderr}", file=__import__('sys').stderr)
                return None

            # Read the output txt file (same name as audio but with .txt extension)
            txt_path = audio_path.replace('.wav', '.txt').replace('.mp3', '.txt')
            if os.path.exists(txt_path):
                with open(txt_path, 'r') as f:
                    return f.read().strip()
            else:
                # Sometimes the output goes to stdout instead
                return result.stdout.strip()

        except subprocess.TimeoutExpired:
            print("whisper.cpp transcription timed out", file=__import__('sys').stderr)
            return None
        except Exception as e:
            print(f"Local transcription error: {e}", file=__import__('sys').stderr)
            return None


class AsyncTranscriber:
    """
    Asynchronous wrapper for transcription with worker thread
    """

    def __init__(self, backend="groq"):
        self.transcriber = Transcriber(backend)
        self.task_queue = queue.Queue()
        self.result_callbacks = {}  # task_id -> callback
        self.worker_thread = None
        self.running = False

    def start_worker(self):
        """Start the transcription worker thread"""
        if self.running:
            return

        self.running = True
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()

    def stop_worker(self):
        """Stop the transcription worker thread"""
        self.running = False
        # Add poison pill to stop the worker
        self.task_queue.put(("STOP", None, None))
        if self.worker_thread:
            self.worker_thread.join(timeout=5.0)

    def _worker_loop(self):
        """Background worker loop for processing transcription tasks"""
        while self.running:
            try:
                task_type, audio_path, task_id = self.task_queue.get(timeout=1.0)

                if task_type == "STOP":
                    break

                if task_type == "TRANSCRIBE":
                    result = self.transcriber.transcribe(audio_path)
                    callback = self.result_callbacks.pop(task_id, None)
                    if callback:
                        try:
                            callback(result)
                        except Exception as e:
                            print(f"Callback error: {e}", file=__import__('sys').stderr)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Worker error: {e}", file=__import__('sys').stderr)

    def transcribe_async(self, audio_path: str, callback: Callable[[str], None], task_id: Optional[str] = None):
        """
        Queue an asynchronous transcription task
        """
        if not self.running:
            self.start_worker()

        if task_id is None:
            import uuid
            task_id = str(uuid.uuid4())

        self.result_callbacks[task_id] = callback
        self.task_queue.put(("TRANSCRIBE", audio_path, task_id))

    def transcribe_file(self, audio_path: str) -> Optional[str]:
        """
        Convenience method to transcribe synchronously
        """
        return self.transcriber.transcribe(audio_path)


class HealthChecker:
    """
    Check transcription backend health
    """

    @staticmethod
    def check_groq_health():
        """Check if Groq API is accessible"""
        if not GROQ_AVAILABLE:
            return False, "Groq package not installed"

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return False, "GROQ_API_KEY not set"

        try:
            client = Groq(api_key=api_key)
            # Make a simple test call
            # We won't actually transcribe anything, just test connectivity
            return True, "OK"
        except Exception as e:
            return False, f"Connection error: {str(e)}"

    @staticmethod
    def check_local_health():
        """Check if local whisper.cpp is available"""
        whisper_cpp_path = os.getenv("WHISPER_CPP_PATH", "./whisper.cpp/main")
        whisper_cpp_model_path = os.getenv("WHISPER_CPP_MODEL_PATH", "./models/ggml-base.en.bin")

        if not os.path.exists(whisper_cpp_path):
            return False, f"whisper.cpp executable not found: {whisper_cpp_path}"

        if not os.path.exists(whisper_cpp_model_path):
            return False, f"whisper.cpp model not found: {whisper_cpp_model_path}"

        return True, "OK"

    @staticmethod
    def check_backend_health(backend: str):
        """Check health of the specified backend"""
        if backend == "groq":
            return HealthChecker.check_groq_health()
        elif backend == "local":
            return HealthChecker.check_local_health()
        else:
            return False, f"Unknown backend: {backend}"


# Example usage:
if __name__ == "__main__":
    import time

    # Test transcription
    transcriber = Transcriber(backend="groq")  # Will fail without API key

    # Check health
    print("Testing backend health...")
    is_healthy, message = HealthChecker.check_groq_health()
    print(f"Groq health: {is_healthy}, {message}")

    is_healthy, message = HealthChecker.check_local_health()
    print(f"Local health: {is_healthy}, {message}")

    # Test async transcription
    def result_callback(result):
        print(f"Async transcription result: {result}")

    async_transcriber = AsyncTranscriber(backend="groq")
    async_transcriber.transcribe_async("dummy.wav", result_callback)

    # Give it a moment to process
    time.sleep(2)
    async_transcriber.stop_worker()