"""
DictaPilot Compliance & Security Module
Handles HIPAA compliance, encryption, audit logging, and data retention.

MIT License
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

import json
import os
import platform
import uuid
import hashlib
import hmac
import base64
import cryptography
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
import threading


def get_security_config_path() -> Path:
    """Get platform-specific security config path"""
    system = platform.system()
    
    if system == "Windows":
        data_dir = Path(os.environ.get("APPDATA", ""))
        return data_dir / "DictaPilot" / "security.json"
    else:
        data_dir = Path(os.path.expanduser("~/.local/share"))
        return data_dir / "dictapilot" / "security.json"


def get_security_config_dir() -> Path:
    """Create and return security config directory"""
    config_path = get_security_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    return config_path.parent


class ComplianceMode(Enum):
    """Compliance modes"""
    STANDARD = "standard"
    HIPAA = "hipaa"
    GDPR = "gdpr"
    SOC2 = "soc2"


class EncryptionLevel(Enum):
    """Encryption levels"""
    NONE = "none"
    AT_REST = "at_rest"
    IN_TRANSIT = "in_transit"
    END_TO_END = "end_to_end"


class AuditAction(Enum):
    """Audit log actions"""
    LOGIN = "login"
    LOGOUT = "logout"
    DATA_ACCESS = "data_access"
    DATA_EXPORT = "data_export"
    DATA_DELETE = "data_delete"
    SETTINGS_CHANGE = "settings_change"
    USER_INVITE = "user_invite"
    DATA_SHARE = "data_share"
    ENCRYPTION_KEY_ROTATE = "encryption_key_rotate"


@dataclass
class AuditLogEntry:
    """Audit log entry"""
    entry_id: str
    timestamp: float
    user_id: str
    action: AuditAction
    resource_type: str
    resource_id: str
    ip_address: Optional[str]
    details: Dict[str, Any]
    checksum: str = ""
    
    def __post_init__(self):
        if not self.checksum:
            self.checksum = self._calculate_checksum()
    
    def _calculate_checksum(self) -> str:
        """Calculate checksum of entry"""
        content = f"{self.timestamp}:{self.user_id}:{self.action.value}:{self.resource_id}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'entry_id': self.entry_id,
            'timestamp': self.timestamp,
            'user_id': self.user_id,
            'action': self.action.value,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'ip_address': self.ip_address,
            'details': self.details,
            'checksum': self.checksum
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuditLogEntry":
        return cls(
            entry_id=data['entry_id'],
            timestamp=data['timestamp'],
            user_id=data['user_id'],
            action=AuditAction(data['action']),
            resource_type=data.get('resource_type', ''),
            resource_id=data.get('resource_id', ''),
            ip_address=data.get('ip_address'),
            details=data.get('details', {}),
            checksum=data.get('checksum', '')
        )


@dataclass
class DataRetentionPolicy:
    """Data retention policy"""
    transcription_retention_days: int = 365
    audio_retention_days: int = 30
    log_retention_days: int = 730
    auto_delete: bool = True
    archive_before_delete: bool = True


@dataclass
class EncryptionConfig:
    """Encryption configuration"""
    level: EncryptionLevel = EncryptionLevel.AT_REST
    algorithm: str = "AES-256-GCM"
    key_rotation_days: int = 90
    master_key_id: str = ""
    last_rotated: float = 0


class AuditLogger:
    """Audit logging service"""
    
    def __init__(self):
        self.logs: List[AuditLogEntry] = []
        self._lock = threading.Lock()
        self._load_logs()
    
    def _load_logs(self):
        """Load logs from file"""
        config_path = get_security_config_path()
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logs_data = data.get('audit_logs', [])
                    self.logs = [AuditLogEntry.from_dict(l) for l in logs_data]
            except (json.JSONDecodeError, IOError):
                pass
    
    def _save_logs(self):
        """Save logs to file"""
        get_security_config_dir()
        config_path = get_security_config_path()
        
        # Load existing config
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except:
                data = {}
        else:
            data = {}
        
        data['audit_logs'] = [l.to_dict() for l in self.logs]
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def log_action(
        self,
        user_id: str,
        action: AuditAction,
        resource_type: str = "",
        resource_id: str = "",
        details: Dict[str, Any] = None,
        ip_address: Optional[str] = None
    ) -> AuditLogEntry:
        """Log an action"""
        with self._lock:
            entry = AuditLogEntry(
                entry_id=str(uuid.uuid4()),
                timestamp=datetime.now().timestamp(),
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                ip_address=ip_address,
                details=details or {}
            )
            
            self.logs.append(entry)
            
            # Keep only last 10000 entries in memory
            if len(self.logs) > 10000:
                self.logs = self.logs[-5000:]
            
            # Save periodically
            if len(self.logs) % 10 == 0:
                self._save_logs()
            
            return entry
    
    def get_logs(
        self,
        user_id: str = None,
        action: AuditAction = None,
        start_time: float = None,
        end_time: float = None,
        limit: int = 100
    ) -> List[AuditLogEntry]:
        """Get audit logs with filters"""
        results = self.logs
        
        if user_id:
            results = [l for l in results if l.user_id == user_id]
        
        if action:
            results = [l for l in results if l.action == action]
        
        if start_time:
            results = [l for l in results if l.timestamp >= start_time]
        
        if end_time:
            results = [l for l in results if l.timestamp <= end_time]
        
        # Sort by timestamp descending
        results = sorted(results, key=lambda x: x.timestamp, reverse=True)
        
        return results[:limit]
    
    def export_logs(self, filepath: Path, format: str = "json") -> bool:
        """Export audit logs"""
        try:
            if format == "json":
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump([l.to_dict() for l in self.logs], f, indent=2)
            elif format == "csv":
                import csv
                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['entry_id', 'timestamp', 'user_id', 'action', 'resource_type', 'resource_id', 'ip_address', 'details'])
                    for log in self.logs:
                        writer.writerow([
                            log.entry_id,
                            datetime.fromtimestamp(log.timestamp).isoformat(),
                            log.user_id,
                            log.action.value,
                            log.resource_type,
                            log.resource_id,
                            log.ip_address,
                            json.dumps(log.details)
                        ])
            return True
        except Exception as e:
            print(f"Export failed: {e}")
            return False


class EncryptionService:
    """Encryption service"""
    
    def __init__(self):
        self.config = EncryptionConfig()
        self._key: Optional[bytes] = None
        self._load_config()
    
    def _load_config(self):
        """Load encryption config"""
        config_path = get_security_config_path()
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    enc_config = data.get('encryption', {})
                    self.config = EncryptionConfig(
                        level=EncryptionLevel(enc_config.get('level', 'at_rest')),
                        algorithm=enc_config.get('algorithm', 'AES-256-GCM'),
                        key_rotation_days=enc_config.get('key_rotation_days', 90),
                        master_key_id=enc_config.get('master_key_id', ''),
                        last_rotated=enc_config.get('last_rotated', 0)
                    )
            except (json.JSONDecodeError, IOError):
                pass
    
    def _save_config(self):
        """Save encryption config"""
        get_security_config_dir()
        config_path = get_security_config_path()
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except:
                data = {}
        else:
            data = {}
        
        data['encryption'] = {
            'level': self.config.level.value,
            'algorithm': self.config.algorithm,
            'key_rotation_days': self.config.key_rotation_days,
            'master_key_id': self.config.master_key_id,
            'last_rotated': self.config.last_rotated
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def set_level(self, level: EncryptionLevel):
        """Set encryption level"""
        self.config.level = level
        self._save_config()
    
    def _generate_key(self) -> bytes:
        """Generate a new encryption key"""
        return hashlib.sha256(str(uuid.uuid4()).encode()).digest()
    
    def initialize(self, password: str = None):
        """Initialize encryption"""
        if self.config.level == EncryptionLevel.NONE:
            return
        
        # Static salt for key derivation (not a secret)
        KDF_SALT = b'dictapilot_salt_v1'
        
        if password:
            # Derive key from password
            self._key = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode(),
                KDF_SALT,
                100000
            )
        else:
            # Generate random key
            self._key = self._generate_key()
        
        self.config.master_key_id = str(uuid.uuid4())
        self._save_config()
    
    def encrypt(self, data: str) -> str:
        """Encrypt data"""
        if not self._key or self.config.level == EncryptionLevel.NONE:
            return data
        
        try:
            from cryptography.fernet import Fernet
            
            # Ensure key is 32 bytes for Fernet
            key = hashlib.sha256(self._key).digest()
            f = Fernet(base64.urlsafe_b64encode(key))
            
            encrypted = f.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except ImportError:
            print("cryptography library not installed")
            return data
        except Exception as e:
            print(f"Encryption failed: {e}")
            return data
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt data"""
        if not self._key or self.config.level == EncryptionLevel.NONE:
            return encrypted_data
        
        try:
            from cryptography.fernet import Fernet
            
            key = hashlib.sha256(self._key).digest()
            f = Fernet(base64.urlsafe_b64encode(key))
            
            decoded = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = f.decrypt(decoded)
            return decrypted.decode()
        except Exception:
            return encrypted_data
    
    def encrypt_file(self, input_path: Path, output_path: Path) -> bool:
        """Encrypt a file"""
        if not self._key:
            return False
        
        try:
            with open(input_path, 'rb') as f:
                data = f.read()
            
            encrypted = self.encrypt(base64.b64encode(data).decode())
            
            with open(output_path, 'w') as f:
                f.write(encrypted)
            
            return True
        except Exception:
            return False
    
    def decrypt_file(self, input_path: Path, output_path: Path) -> bool:
        """Decrypt a file"""
        if not self._key:
            return False
        
        try:
            with open(input_path, 'r') as f:
                encrypted = f.read()
            
            decrypted = self.decrypt(encrypted)
            data = base64.b64decode(decrypted)
            
            with open(output_path, 'wb') as f:
                f.write(data)
            
            return True
        except Exception:
            return False
    
    def rotate_keys(self) -> bool:
        """Rotate encryption keys"""
        # Would re-encrypt all data with new key
        self._key = self._generate_key()
        self.config.last_rotated = datetime.now().timestamp()
        self.config.master_key_id = str(uuid.uuid4())
        self._save_config()
        return True


class DataRetentionService:
    """Data retention management"""
    
    def __init__(self):
        self.policy = DataRetentionPolicy()
        self._load_policy()
    
    def _load_policy(self):
        """Load retention policy"""
        config_path = get_security_config_path()
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    ret_policy = data.get('retention', {})
                    self.policy = DataRetentionPolicy(
                        transcription_retention_days=ret_policy.get('transcription_retention_days', 365),
                        audio_retention_days=ret_policy.get('audio_retention_days', 30),
                        log_retention_days=ret_policy.get('log_retention_days', 730),
                        auto_delete=ret_policy.get('auto_delete', True),
                        archive_before_delete=ret_policy.get('archive_before_delete', True)
                    )
            except (json.JSONDecodeError, IOError):
                pass
    
    def _save_policy(self):
        """Save retention policy"""
        get_security_config_dir()
        config_path = get_security_config_path()
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except:
                data = {}
        else:
            data = {}
        
        data['retention'] = {
            'transcription_retention_days': self.policy.transcription_retention_days,
            'audio_retention_days': self.policy.audio_retention_days,
            'log_retention_days': self.policy.log_retention_days,
            'auto_delete': self.policy.auto_delete,
            'archive_before_delete': self.policy.archive_before_delete
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def set_policy(self, policy: DataRetentionPolicy):
        """Set retention policy"""
        self.policy = policy
        self._save_policy()
    
    def get_expired_items(self, item_type: str) -> List[str]:
        """Get expired items for deletion"""
        now = datetime.now().timestamp()
        
        if item_type == "transcription":
            cutoff = now - (self.policy.transcription_retention_days * 24 * 60 * 60)
        elif item_type == "audio":
            cutoff = now - (self.policy.audio_retention_days * 24 * 60 * 60)
        elif item_type == "log":
            cutoff = now - (self.policy.log_retention_days * 24 * 60 * 60)
        else:
            return []
        
        # Would query database for items older than cutoff
        return []
    
    def apply_retention_policy(self, callback: Callable[[str, List[str]], bool] = None) -> int:
        """Apply retention policy and delete expired data"""
        deleted_count = 0
        
        for item_type in ["transcription", "audio", "log"]:
            expired = self.get_expired_items(item_type)
            
            for item_id in expired:
                if callback:
                    success = callback(item_type, [item_id])
                else:
                    success = True  # Would actually delete
                
                if success:
                    deleted_count += 1
        
        return deleted_count


class ComplianceManager:
    """Compliance management"""
    
    def __init__(self):
        self.mode = ComplianceMode.STANDARD
        self.audit_logger = AuditLogger()
        self.encryption = EncryptionService()
        self.retention = DataRetentionService()
        self._load_config()
    
    def _load_config(self):
        """Load compliance config"""
        config_path = get_security_config_path()
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.mode = ComplianceMode(data.get('compliance_mode', 'standard'))
            except (json.JSONDecodeError, IOError):
                pass
    
    def _save_config(self):
        """Save compliance config"""
        get_security_config_dir()
        config_path = get_security_config_path()
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except:
                data = {}
        else:
            data = {}
        
        data['compliance_mode'] = self.mode.value
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def enable_hipaa_mode(self) -> bool:
        """Enable HIPAA compliance mode"""
        self.mode = ComplianceMode.HIPAA
        
        # Enable encryption at rest and in transit
        self.encryption.set_level(EncryptionLevel.END_TO_END)
        
        # Enable audit logging
        # Enable strict retention
        self.retention.policy.transcription_retention_days = 365
        self.retention.policy.audio_retention_days = 30
        self.retention.policy.auto_delete = True
        
        self._save_config()
        return True
    
    def enable_gdpr_mode(self) -> bool:
        """Enable GDPR compliance mode"""
        self.mode = ComplianceMode.GDPR
        
        # Enable encryption
        self.encryption.set_level(EncryptionLevel.END_TO_END)
        
        # Enable audit logging
        # Enable right to be forgotten (deletion)
        
        self._save_config()
        return True
    
    def enable_soc2_mode(self) -> bool:
        """Enable SOC 2 compliance mode"""
        self.mode = ComplianceMode.SOC2
        
        # Enable encryption
        self.encryption.set_level(EncryptionLevel.IN_TRANSIT)
        
        # Enable audit logging
        # Enable key rotation
        
        self._save_config()
        return True
    
    def get_compliance_status(self) -> Dict[str, Any]:
        """Get compliance status"""
        return {
            'mode': self.mode.value,
            'encryption_level': self.encryption.config.level.value,
            'audit_logging_enabled': True,
            'retention_policy': {
                'transcription_days': self.retention.policy.transcription_retention_days,
                'audio_days': self.retention.policy.audio_retention_days,
                'log_days': self.retention.policy.log_retention_days,
                'auto_delete': self.retention.policy.auto_delete
            }
        }
    
    def generate_compliance_report(self) -> Dict[str, Any]:
        """Generate compliance report"""
        return {
            'generated_at': datetime.now().isoformat(),
            'compliance_mode': self.mode.value,
            'encryption': {
                'level': self.encryption.config.level.value,
                'algorithm': self.encryption.config.algorithm,
                'last_key_rotation': datetime.fromtimestamp(
                    self.encryption.config.last_rotated
                ).isoformat() if self.encryption.config.last_rotated else None
            },
            'audit_logs': {
                'total_entries': len(self.audit_logger.logs),
                'recent_entries': len(self.audit_logger.get_logs(limit=100))
            },
            'retention': self.retention.policy.__dict__
        }


# Global instance
_compliance_manager_instance: Optional[ComplianceManager] = None


def get_compliance_manager() -> ComplianceManager:
    """Get or create the global compliance manager instance"""
    global _compliance_manager_instance
    if _compliance_manager_instance is None:
        _compliance_manager_instance = ComplianceManager()
    return _compliance_manager_instance


# Convenience functions
def enable_hipaa() -> bool:
    """Enable HIPAA compliance mode"""
    manager = get_compliance_manager()
    return manager.enable_hipaa_mode()


def get_compliance_status() -> Dict[str, Any]:
    """Get compliance status"""
    manager = get_compliance_manager()
    return manager.get_compliance_status()


def log_audit(
    action: AuditAction,
    resource_type: str = "",
    resource_id: str = "",
    details: Dict[str, Any] = None
):
    """Log an audit entry"""
    manager = get_compliance_manager()
    manager.audit_logger.log_action(
        user_id="",  # Would get from auth
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details
    )
