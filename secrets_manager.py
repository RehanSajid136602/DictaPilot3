"""
DictaPilot Secrets Manager
Secure storage and retrieval of API keys and sensitive data

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
import platform
import logging
from typing import Optional


class SecretsManager:
    """
    Cross-platform secure storage for API keys and sensitive data
    Uses platform-specific secure storage when available, falls back to environment variables
    """

    def __init__(self):
        self.system = platform.system()
        self.logger = logging.getLogger(__name__)

    def store_secret(self, service_name: str, key: str, value: str) -> bool:
        """
        Store a secret value securely
        """
        if self.system == "Darwin":  # macOS
            return self._store_macos(service_name, key, value)
        elif self.system == "Windows":
            return self._store_windows(service_name, key, value)
        elif self.system == "Linux":
            return self._store_linux(service_name, key, value)
        else:
            # Fallback to environment variable (not secure, for dev only)
            os.environ[f"DICTAPILOT_{service_name.upper()}_{key.upper()}"] = value
            self.logger.warning(f"Storing secret in environment variable for {self.system}. This is not secure!")
            return True

    def retrieve_secret(self, service_name: str, key: str) -> Optional[str]:
        """
        Retrieve a stored secret value
        """
        if self.system == "Darwin":  # macOS
            return self._retrieve_macos(service_name, key)
        elif self.system == "Windows":
            return self._retrieve_windows(service_name, key)
        elif self.system == "Linux":
            return self._retrieve_linux(service_name, key)
        else:
            # Fallback to environment variable (not secure, for dev only)
            env_key = f"DICTAPILOT_{service_name.upper()}_{key.upper()}"
            return os.environ.get(env_key)

    def delete_secret(self, service_name: str, key: str) -> bool:
        """
        Delete a stored secret
        """
        if self.system == "Darwin":  # macOS
            return self._delete_macos(service_name, key)
        elif self.system == "Windows":
            return self._delete_windows(service_name, key)
        elif self.system == "Linux":
            return self._delete_linux(service_name, key)
        else:
            # Fallback to environment variable removal
            env_key = f"DICTAPILOT_{service_name.upper()}_{key.upper()}"
            if env_key in os.environ:
                del os.environ[env_key]
            return True

    def _store_macos(self, service_name: str, key: str, value: str) -> bool:
        """
        Store secret using macOS Keychain
        """
        try:
            import subprocess
            import sys

            cmd = [
                "security", "add-generic-password",
                "-s", f"DictaPilot-{service_name}-{key}",
                "-a", os.getlogin() if hasattr(os, 'getlogin') else "user",
                "-w", value,
                "-U"  # Update if exists
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                self.logger.error(f"Keychain error: {result.stderr}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error storing secret in macOS Keychain: {e}")
            return False

    def _retrieve_macos(self, service_name: str, key: str) -> Optional[str]:
        """
        Retrieve secret from macOS Keychain
        """
        try:
            import subprocess

            cmd = [
                "security", "find-generic-password",
                "-s", f"DictaPilot-{service_name}-{key}",
                "-w"  # Only return password
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                # Password not found is not an error
                if "password not found" in result.stderr.lower():
                    return None
                self.logger.error(f"Keychain error: {result.stderr}")
                return None
        except Exception as e:
            self.logger.error(f"Error retrieving secret from macOS Keychain: {e}")
            return None

    def _delete_macos(self, service_name: str, key: str) -> bool:
        """
        Delete secret from macOS Keychain
        """
        try:
            import subprocess

            cmd = [
                "security", "delete-generic-password",
                "-s", f"DictaPilot-{service_name}-{key}",
                "-a", os.getlogin() if hasattr(os, 'getlogin') else "user",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            # Return code 0 means deleted successfully, 44 means item not found (also success)
            return result.returncode in [0, 44]
        except Exception as e:
            self.logger.error(f"Error deleting secret from macOS Keychain: {e}")
            return False

    def _store_windows(self, service_name: str, key: str, value: str) -> bool:
        """
        Store secret using Windows Credential Manager
        """
        try:
            import win32cred
            import pywintypes

            target_name = f"DictaPilot-{service_name}-{key}"

            # Create credential dictionary
            credential = {
                'TargetName': target_name,
                'UserName': os.getlogin() if hasattr(os, 'getlogin') else 'user',
                'Password': value,
                'Type': win32cred.CRED_TYPE_GENERIC,
                'Persist': win32cred.CRED_PERSIST_ENTERPRISE,
                'Comment': f'Secret for DictaPilot {service_name}'
            }

            win32cred.CredWrite(credential, 0)
            return True
        except ImportError:
            # win32cred not available, fall back to a warning
            self.logger.warning("pywin32 not installed. Storing secret in environment variable (not secure).")
            os.environ[f"DICTAPILOT_{service_name.upper()}_{key.upper()}"] = value
            return True
        except Exception as e:
            self.logger.error(f"Error storing secret in Windows Credential Manager: {e}")
            # Fall back to environment variable if Credential Manager fails
            os.environ[f"DICTAPILOT_{service_name.upper()}_{key.upper()}"] = value
            return False

    def _retrieve_windows(self, service_name: str, key: str) -> Optional[str]:
        """
        Retrieve secret from Windows Credential Manager
        """
        try:
            import win32cred

            target_name = f"DictaPilot-{service_name}-{key}"

            try:
                credential = win32cred.CredRead(target_name, win32cred.CRED_TYPE_GENERIC)
                return credential['CredentialBlob'].decode('utf-16')
            except pywintypes.error as e:
                # Error code 1168 means credential not found
                if e.winerror == 1168:
                    return None
                raise
        except ImportError:
            # win32cred not available, fall back to environment variable
            env_key = f"DICTAPILOT_{service_name.upper()}_{key.upper()}"
            return os.environ.get(env_key)
        except Exception as e:
            self.logger.error(f"Error retrieving secret from Windows Credential Manager: {e}")
            return None

    def _delete_windows(self, service_name: str, key: str) -> bool:
        """
        Delete secret from Windows Credential Manager
        """
        try:
            import win32cred
            import pywintypes

            target_name = f"DictaPilot-{service_name}-{key}"

            try:
                win32cred.CredDelete(target_name, win32cred.CRED_TYPE_GENERIC)
                return True
            except pywintypes.error as e:
                # Error code 1168 means credential not found (success)
                if e.winerror == 1168:
                    return True
                raise
        except ImportError:
            # win32cred not available, fall back to removing environment variable
            env_key = f"DICTAPILOT_{service_name.upper()}_{key.upper()}"
            if env_key in os.environ:
                del os.environ[env_key]
            return True
        except Exception as e:
            self.logger.error(f"Error deleting secret from Windows Credential Manager: {e}")
            return False

    def _store_linux(self, service_name: str, key: str, value: str) -> bool:
        """
        Store secret using Linux Secret Service (if available)
        Falls back to environment variable for dev
        """
        try:
            import secretstorage
            import getpass

            # Connect to the secret service
            bus = secretstorage.dbus_init()
            collection = secretstorage.get_default_collection(bus)

            attributes = {
                'application': 'DictaPilot',
                'service': service_name,
                'username': getpass.getuser(),
                'key': key
            }

            collection.create_item(
                f'DictaPilot {service_name} {key}',
                attributes,
                value.encode('utf-8'),
                replace=True
            )
            return True
        except ImportError:
            # SecretService not available, fall back to warning
            self.logger.warning("SecretStorage not installed. Storing secret in environment variable (not secure).")
            os.environ[f"DICTAPILOT_{service_name.upper()}_{key.upper()}"] = value
            return True
        except Exception as e:
            self.logger.error(f"Error storing secret in Linux Secret Service: {e}")
            # Fall back to environment variable if Secret Service fails
            os.environ[f"DICTAPILOT_{service_name.upper()}_{key.upper()}"] = value
            return False

    def _retrieve_linux(self, service_name: str, key: str) -> Optional[str]:
        """
        Retrieve secret from Linux Secret Service (if available)
        Falls back to environment variable for dev
        """
        try:
            import secretstorage
            import getpass

            # Connect to the secret service
            bus = secretstorage.dbus_init()
            collection = secretstorage.get_default_collection(bus)

            attributes = {
                'application': 'DictaPilot',
                'service': service_name,
                'username': getpass.getuser(),
                'key': key
            }

            items = list(collection.search_items(attributes))
            if items:
                item = items[0]
                return item.get_secret().decode('utf-8')
            return None
        except ImportError:
            # SecretService not available, fall back to environment variable
            env_key = f"DICTAPILOT_{service_name.upper()}_{key.upper()}"
            return os.environ.get(env_key)
        except Exception as e:
            self.logger.error(f"Error retrieving secret from Linux Secret Service: {e}")
            return None

    def _delete_linux(self, service_name: str, key: str) -> bool:
        """
        Delete secret from Linux Secret Service (if available)
        Falls back to environment variable for dev
        """
        try:
            import secretstorage
            import getpass

            # Connect to the secret service
            bus = secretstorage.dbus_init()
            collection = secretstorage.get_default_collection(bus)

            attributes = {
                'application': 'DictaPilot',
                'service': service_name,
                'username': getpass.getuser(),
                'key': key
            }

            items = list(collection.search_items(attributes))
            if items:
                item = items[0]
                item.delete()

            return True
        except ImportError:
            # SecretService not available, fall back to removing environment variable
            env_key = f"DICTAPILOT_{service_name.upper()}_{key.upper()}"
            if env_key in os.environ:
                del os.environ[env_key]
            return True
        except Exception as e:
            self.logger.error(f"Error deleting secret from Linux Secret Service: {e}")
            return False


class APISecretsManager(SecretsManager):
    """
    Specialized secrets manager for API keys
    """

    def __init__(self):
        super().__init__()

    def store_api_key(self, service: str, api_key: str) -> bool:
        """
        Store an API key for a specific service
        """
        return self.store_secret(service, "api_key", api_key)

    def retrieve_api_key(self, service: str) -> Optional[str]:
        """
        Retrieve an API key for a specific service
        """
        # First try to get from secure storage
        api_key = self.retrieve_secret(service, "api_key")

        if not api_key:
            # Fallback to environment variable (for backward compatibility)
            env_vars = [
                f"{service.upper()}_API_KEY",
                f"{service.upper()}_KEY",
                f"{service.upper()}_TOKEN",
            ]

            for var in env_vars:
                api_key = os.getenv(var)
                if api_key:
                    break

        return api_key

    def set_api_key_env(self, service: str):
        """
        Set the API key as an environment variable for compatibility
        """
        api_key = self.retrieve_api_key(service)
        if api_key:
            env_var = f"{service.upper()}_API_KEY"
            os.environ[env_var] = api_key
            return True
        return False


# Example usage:
if __name__ == "__main__":
    import sys

    secrets = APISecretsManager()

    # Example usage
    service_name = "groq"
    api_key = "your-api-key-here"

    print(f"Platform: {platform.system()}")

    # Store the API key
    if secrets.store_api_key(service_name, api_key):
        print("API key stored successfully")
    else:
        print("Failed to store API key")

    # Retrieve the API key
    retrieved_key = secrets.retrieve_api_key(service_name)
    if retrieved_key:
        print(f"Retrieved API key: {'*' * len(retrieved_key)}")
    else:
        print("API key not found")

    # Set as environment variable for compatibility
    if secrets.set_api_key_env(service_name):
        print(f"{service_name.upper()}_API_KEY set in environment")

    # Delete the API key
    # Note: Uncomment the next line to actually delete the key
    # secrets.delete_secret(service_name, "api_key")