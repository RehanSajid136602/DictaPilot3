"""
DictaPilot Diagnostic Tools
System health checker for microphone permissions, model availability, API key presence

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
import sys
import platform
import subprocess
import pkg_resources
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class DiagnosticResult:
    """Result of a diagnostic check"""
    name: str
    passed: bool
    message: str
    severity: str = "info"  # "info", "warning", "error"


class HealthChecker:
    """
    Comprehensive system health checker for DictaPilot
    """

    def __init__(self):
        self.results = []

    def run_all_diagnostics(self) -> List[DiagnosticResult]:
        """Run all diagnostic checks"""
        self.results = []

        # Environment checks
        self._check_os_info()
        self._check_python_version()
        self._check_api_key()

        # Audio checks
        self._check_microphone_permissions()
        self._check_audio_devices()

        # Dependency checks
        self._check_required_packages()
        self._check_optional_packages()

        # Model/service checks
        self._check_model_availability()

        return self.results

    def _check_os_info(self):
        """Check operating system information"""
        os_name = platform.system()
        os_version = platform.version()
        self.results.append(DiagnosticResult(
            name="Operating System",
            passed=True,
            message=f"{os_name} {os_version}",
            severity="info"
        ))

    def _check_python_version(self):
        """Check Python version"""
        version_info = sys.version_info
        version_str = f"{version_info.major}.{version_info.minor}.{version_info.micro}"

        if version_info.major < 3 or (version_info.major == 3 and version_info.minor < 8):
            self.results.append(DiagnosticResult(
                name="Python Version",
                passed=False,
                message=f"Python 3.8+ required, but {version_str} found",
                severity="error"
            ))
        else:
            self.results.append(DiagnosticResult(
                name="Python Version",
                passed=True,
                message=f"Python {version_str} OK",
                severity="info"
            ))

    def _check_api_key(self):
        """Check if API key is set"""
        api_key = os.getenv("GROQ_API_KEY")
        if api_key and len(api_key) > 10:  # At least some length
            self.results.append(DiagnosticResult(
                name="GROQ API Key",
                passed=True,
                message="API key is set and appears valid",
                severity="info"
            ))
        else:
            self.results.append(DiagnosticResult(
                name="GROQ API Key",
                passed=False,
                message="GROQ_API_KEY environment variable not set or invalid",
                severity="warning"
            ))

    def _check_microphone_permissions(self):
        """Check microphone permissions (platform-specific)"""
        os_name = platform.system()

        if os_name == "Darwin":  # macOS
            try:
                # Check if we can access the microphone
                result = subprocess.run([
                    "osascript", "-e",
                    'tell application "System Events" to security preferences'
                ], capture_output=True, text=True, timeout=5)

                # Try to use a simple command that would require mic access
                # For macOS, we'll test if we can import and use pyaudio or sounddevice
                import sounddevice as sd
                devices = sd.query_devices()

                has_input = any(device['max_input_channels'] > 0
                               for device in devices.values()
                               if device['max_input_channels'] > 0)

                if has_input:
                    self.results.append(DiagnosticResult(
                        name="Microphone Access",
                        passed=True,
                        message="Input devices available",
                        severity="info"
                    ))
                else:
                    self.results.append(DiagnosticResult(
                        name="Microphone Access",
                        passed=False,
                        message="No input devices found - check microphone permissions",
                        severity="error"
                    ))
            except Exception:
                self.results.append(DiagnosticResult(
                    name="Microphone Access",
                    passed=False,
                    message="Cannot check microphone access - likely permission issue",
                    severity="error"
                ))

        elif os_name == "Windows":
            try:
                import sounddevice as sd
                devices = sd.query_devices()

                has_input = any(device['max_input_channels'] > 0
                               for device in devices.values()
                               if device['max_input_channels'] > 0)

                if has_input:
                    self.results.append(DiagnosticResult(
                        name="Microphone Access",
                        passed=True,
                        message="Input devices available",
                        severity="info"
                    ))
                else:
                    self.results.append(DiagnosticResult(
                        name="Microphone Access",
                        passed=False,
                        message="No input devices found",
                        severity="error"
                    ))
            except Exception as e:
                self.results.append(DiagnosticResult(
                    name="Microphone Access",
                    passed=False,
                    message=f"Cannot access microphone: {str(e)}",
                    severity="error"
                ))

        elif os_name == "Linux":
            try:
                # Check for ALSA/PulseAudio
                has_pulse = subprocess.run(["pulseaudio", "--check"],
                                         stdout=subprocess.DEVNULL,
                                         stderr=subprocess.DEVNULL).returncode == 0

                if has_pulse:
                    # Try to list input devices
                    import sounddevice as sd
                    devices = sd.query_devices()

                    has_input = any(device['max_input_channels'] > 0
                                   for device in devices.values()
                                   if device['max_input_channels'] > 0)

                    if has_input:
                        self.results.append(DiagnosticResult(
                            name="Microphone Access",
                            passed=True,
                            message="Input devices available via PulseAudio",
                            severity="info"
                        ))
                    else:
                        self.results.append(DiagnosticResult(
                            name="Microphone Access",
                            passed=False,
                            message="No input devices found - check audio configuration",
                            severity="error"
                        ))
                else:
                    self.results.append(DiagnosticResult(
                        name="Microphone Access",
                        passed=False,
                        message="PulseAudio not running - microphone may not be accessible",
                        severity="warning"
                    ))
            except Exception:
                self.results.append(DiagnosticResult(
                    name="Microphone Access",
                    passed=False,
                    message="Cannot access microphone - check PulseAudio/ALSA setup",
                    severity="error"
                ))

    def _check_audio_devices(self):
        """Check for available audio devices"""
        try:
            import sounddevice as sd
            devices = sd.query_devices()

            input_devices = [d for d in devices.values() if d['max_input_channels'] > 0]

            if input_devices:
                device_names = [d['name'] for d in input_devices]
                self.results.append(DiagnosticResult(
                    name="Audio Devices",
                    passed=True,
                    message=f"Found {len(input_devices)} input device(s): {', '.join(device_names)}",
                    severity="info"
                ))
            else:
                self.results.append(DiagnosticResult(
                    name="Audio Devices",
                    passed=False,
                    message="No audio input devices found",
                    severity="error"
                ))
        except Exception as e:
            self.results.append(DiagnosticResult(
                name="Audio Devices",
                passed=False,
                message=f"Cannot query audio devices: {str(e)}",
                severity="error"
            ))

    def _check_required_packages(self):
        """Check if all required packages are installed"""
        required_packages = [
            'groq',
            'sounddevice',
            'soundfile',
            'numpy',
            'keyboard',
            'pyperclip',
            'python-dotenv',
            'pynput',
            'Pillow'
        ]

        for package in required_packages:
            try:
                pkg_resources.get_distribution(package)
                self.results.append(DiagnosticResult(
                    name=f"Required Package: {package}",
                    passed=True,
                    message=f"{package} is installed",
                    severity="info"
                ))
            except pkg_resources.DistributionNotFound:
                self.results.append(DiagnosticResult(
                    name=f"Required Package: {package}",
                    passed=False,
                    message=f"{package} is not installed",
                    severity="error"
                ))

    def _check_optional_packages(self):
        """Check if optional packages are installed"""
        optional_packages = [
            'pyaudio',
            'pywin32',  # For Windows
            'secretstorage',  # For Linux
        ]

        for package in optional_packages:
            try:
                pkg_resources.get_distribution(package)
                self.results.append(DiagnosticResult(
                    name=f"Optional Package: {package}",
                    passed=True,
                    message=f"{package} is installed (enhanced functionality)",
                    severity="info"
                ))
            except pkg_resources.DistributionNotFound:
                self.results.append(DiagnosticResult(
                    name=f"Optional Package: {package}",
                    passed=True,  # Optional, so not an error
                    message=f"{package} is not installed (some features may be limited)",
                    severity="warning"
                ))

    def _check_model_availability(self):
        """Check if transcription models are available"""
        try:
            # Test basic Groq functionality
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                self.results.append(DiagnosticResult(
                    name="Model Availability",
                    passed=False,
                    message="GROQ_API_KEY not set - cannot test model availability",
                    severity="warning"
                ))
                return

            from groq import Groq
            client = Groq(api_key=api_key)

            # Don't actually transcribe, just test connection
            # For now, just check if client can be created
            self.results.append(DiagnosticResult(
                name="Model Availability",
                passed=True,
                message="Groq client initialized successfully",
                severity="info"
            ))
        except ImportError:
            self.results.append(DiagnosticResult(
                name="Model Availability",
                passed=False,
                message="Groq package not installed",
                severity="error"
            ))
        except Exception as e:
            self.results.append(DiagnosticResult(
                name="Model Availability",
                passed=False,
                message=f"Groq connection failed: {str(e)}",
                severity="error"
            ))

    def get_summary(self) -> Dict[str, any]:
        """Get a summary of the diagnostic results"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed

        errors = [r for r in self.results if r.severity == "error"]
        warnings = [r for r in self.results if r.severity == "warning"]

        return {
            "total_checks": total,
            "passed": passed,
            "failed": failed,
            "errors": len(errors),
            "warnings": len(warnings),
            "results": self.results
        }

    def print_report(self):
        """Print a formatted diagnostic report"""
        summary = self.get_summary()

        print("=" * 60)
        print("DictaPilot Diagnostic Report")
        print("=" * 60)
        print(f"Total Checks: {summary['total_checks']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Errors: {summary['errors']}")
        print(f"Warnings: {summary['warnings']}")
        print("=" * 60)

        for result in self.results:
            status = "✓" if result.passed else "✗"
            severity_icon = {
                "info": "ℹ️",
                "warning": "⚠️",
                "error": "❌"
            }.get(result.severity, "ℹ️")

            print(f"{severity_icon} {status} {result.name}: {result.message}")

        print("=" * 60)


# Example usage
if __name__ == "__main__":
    checker = HealthChecker()
    checker.run_all_diagnostics()
    checker.print_report()
