"""
DictaPilot Cross-Device Sync Module
Handles synchronization across devices using cloud backend.

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
import time
import hashlib
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime
import threading


def get_sync_config_path() -> Path:
    """Get platform-specific sync config path"""
    system = platform.system()
    
    if system == "Windows":
        data_dir = Path(os.environ.get("APPDATA", ""))
        return data_dir / "DictaPilot" / "sync.json"
    else:
        data_dir = Path(os.path.expanduser("~/.local/share"))
        return data_dir / "dictapilot" / "sync.json"


def get_sync_config_dir() -> Path:
    """Create and return sync config directory"""
    config_path = get_sync_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    return config_path.parent


class SyncProvider(Enum):
    """Sync backend providers"""
    FIREBASE = "firebase"
    SUPABASE = "supabase"
    CUSTOM = "custom"


class SyncStatus(Enum):
    """Sync status"""
    IDLE = "idle"
    SYNCING = "syncing"
    ERROR = "error"
    OFFLINE = "offline"
    CONFLICT = "conflict"


class SyncItemType(Enum):
    """Types of items that can be synced"""
    PERSONAL_DICTIONARY = "personal_dictionary"
    SNIPPETS = "snippets"
    SETTINGS = "settings"
    TRANSCRIPTIONS = "transcriptions"
    COMMANDS = "commands"


@dataclass
class SyncItem:
    """A syncable item"""
    item_id: str
    item_type: SyncItemType
    data: Dict[str, Any]
    device_id: str
    timestamp: float
    version: int = 1
    checksum: str = ""
    parent_id: Optional[str] = None
    
    def __post_init__(self):
        if not self.checksum:
            self.checksum = self._calculate_checksum()
    
    def _calculate_checksum(self) -> str:
        """Calculate checksum of item data"""
        content = json.dumps(self.data, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'item_id': self.item_id,
            'item_type': self.item_type.value,
            'data': self.data,
            'device_id': self.device_id,
            'timestamp': self.timestamp,
            'version': self.version,
            'checksum': self.checksum,
            'parent_id': self.parent_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SyncItem":
        return cls(
            item_id=data['item_id'],
            item_type=SyncItemType(data['item_type']),
            data=data['data'],
            device_id=data['device_id'],
            timestamp=data['timestamp'],
            version=data.get('version', 1),
            checksum=data.get('checksum', ''),
            parent_id=data.get('parent_id')
        )


@dataclass
class SyncConflict:
    """A sync conflict"""
    conflict_id: str
    item_type: SyncItemType
    local_item: SyncItem
    remote_item: SyncItem
    local_timestamp: float
    remote_timestamp: float
    resolved: bool = False
    resolution: Optional[str] = None  # "local", "remote", "merge"
    resolved_item: Optional[SyncItem] = None


@dataclass
class DeviceInfo:
    """Device information"""
    device_id: str
    device_name: str
    platform: str
    last_seen: float
    is_current: bool = False


class ConflictResolver:
    """Resolves sync conflicts"""
    
    @staticmethod
    def resolve_by_timestamp(local: SyncItem, remote: SyncItem) -> SyncItem:
        """Keep the item with the latest timestamp"""
        if local.timestamp > remote.timestamp:
            return local
        return remote
    
    @staticmethod
    def resolve_by_version(local: SyncItem, remote: SyncItem) -> SyncItem:
        """Keep the item with the highest version"""
        if local.version >= remote.version:
            return local
        return remote
    
    @staticmethod
    def merge_items(local: SyncItem, remote: SyncItem) -> SyncItem:
        """Merge two items (simple merge for dict data)"""
        merged_data = {**remote.data, **local.data}
        
        return SyncItem(
            item_id=local.item_id,
            item_type=local.item_type,
            data=merged_data,
            device_id=local.device_id,
            timestamp=max(local.timestamp, remote.timestamp),
            version=max(local.version, remote.version) + 1,
            parent_id=local.item_id
        )


class SyncBackend:
    """Base sync backend"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def connect(self) -> bool:
        """Connect to backend"""
        raise NotImplementedError
    
    def disconnect(self):
        """Disconnect from backend"""
        raise NotImplementedError
    
    def push_item(self, item: SyncItem) -> bool:
        """Push item to backend"""
        raise NotImplementedError
    
    def pull_items(self, item_type: SyncItemType, since: float = 0) -> List[SyncItem]:
        """Pull items from backend"""
        raise NotImplementedError
    
    def delete_item(self, item_id: str) -> bool:
        """Delete item from backend"""
        raise NotImplementedError
    
    def get_devices(self) -> List[DeviceInfo]:
        """Get list of synced devices"""
        raise NotImplementedError


class FirebaseBackend(SyncBackend):
    """Firebase sync backend"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.firebase_app = None
        self.db = None
    
    def connect(self) -> bool:
        """Connect to Firebase"""
        try:
            import firebase_admin
            from firebase_admin import credentials, db
            
            if not firebase_admin._apps:
                cred = credentials.Certificate(self.config.get('credentials_path'))
                firebase_admin.initialize_app(cred, {
                    'databaseURL': self.config.get('database_url')
                })
            
            self.db = db
            return True
        except ImportError:
            print("Firebase SDK not installed")
            return False
        except Exception as e:
            print(f"Firebase connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from Firebase"""
        pass
    
    def push_item(self, item: SyncItem) -> bool:
        """Push item to Firebase"""
        if not self.db:
            return False
        
        try:
            ref = self.db.reference(f"users/{self.config['user_id']}/items/{item.item_type.value}/{item.item_id}")
            ref.set(item.to_dict())
            return True
        except Exception as e:
            print(f"Firebase push failed: {e}")
            return False
    
    def pull_items(self, item_type: SyncItemType, since: float = 0) -> List[SyncItem]:
        """Pull items from Firebase"""
        if not self.db:
            return []
        
        try:
            ref = self.db.reference(f"users/{self.config['user_id']}/items/{item_type.value}")
            data = ref.get()
            
            if not data:
                return []
            
            items = []
            for item_id, item_data in data.items():
                if item_data.get('timestamp', 0) > since:
                    items.append(SyncItem.from_dict(item_data))
            
            return items
        except Exception:
            return []
    
    def delete_item(self, item_id: str) -> bool:
        """Delete item from Firebase"""
        if not self.db:
            return False
        
        try:
            ref = self.db.reference(f"users/{self.config['user_id']}/items/{item_id}")
            ref.delete()
            return True
        except Exception:
            return False
    
    def get_devices(self) -> List[DeviceInfo]:
        """Get list of synced devices"""
        return []  # Would need Firebase implementation


class SupabaseBackend(SyncBackend):
    """Supabase sync backend"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client = None
    
    def connect(self) -> bool:
        """Connect to Supabase"""
        try:
            from supabase import create_client
            
            self.client = create_client(
                self.config.get('url'),
                self.config.get('key')
            )
            return True
        except ImportError:
            print("Supabase SDK not installed")
            return False
        except Exception as e:
            print(f"Supabase connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from Supabase"""
        self.client = None
    
    def push_item(self, item: SyncItem) -> bool:
        """Push item to Supabase"""
        if not self.client:
            return False
        
        try:
            self.client.table('sync_items').upsert({
                'item_id': item.item_id,
                'item_type': item.item_type.value,
                'data': json.dumps(item.data),
                'device_id': item.device_id,
                'timestamp': item.timestamp,
                'version': item.version,
                'checksum': item.checksum,
                'user_id': self.config.get('user_id')
            }).execute()
            return True
        except Exception as e:
            print(f"Supabase push failed: {e}")
            return False
    
    def pull_items(self, item_type: SyncItemType, since: float = 0) -> List[SyncItem]:
        """Pull items from Supabase"""
        if not self.client:
            return []
        
        try:
            response = self.client.table('sync_items').select('*').eq('item_type', item_type.value).eq('user_id', self.config['user_id']).gt('timestamp', since).execute()
            
            items = []
            for row in response.data:
                item_data = row.copy()
                item_data['data'] = json.loads(row['data'])
                items.append(SyncItem.from_dict(item_data))
            
            return items
        except Exception:
            return []
    
    def delete_item(self, item_id: str) -> bool:
        """Delete item from Supabase"""
        if not self.client:
            return False
        
        try:
            self.client.table('sync_items').delete().eq('item_id', item_id).execute()
            return True
        except Exception:
            return False
    
    def get_devices(self) -> List[DeviceInfo]:
        """Get list of synced devices"""
        return []  # Would need Supabase implementation


class SyncService:
    """Main sync service"""
    
    def __init__(self):
        self.provider: Optional[SyncBackend] = None
        self.device_id = self._get_or_create_device_id()
        self.status = SyncStatus.IDLE
        self.last_sync = 0.0
        self.conflicts: List[SyncConflict] = []
        self.listeners: Dict[str, List[Callable]] = {
            'on_status_change': [],
            'on_sync_complete': [],
            'on_conflict': [],
            'on_error': []
        }
        self._sync_thread: Optional[threading.Thread] = None
        self._auto_sync = False
        self._sync_interval = 300  # 5 minutes
        self._load_config()
    
    def _get_or_create_device_id(self) -> str:
        """Get or create unique device ID"""
        config_path = get_sync_config_path()
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    data = json.load(f)
                    return data.get('device_id', str(uuid.uuid4()))
            except:
                pass
        
        # Create new device ID
        device_id = str(uuid.uuid4())
        self._save_config()
        return device_id
    
    def _load_config(self):
        """Load sync configuration"""
        config_path = get_sync_config_path()
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.device_id = data.get('device_id', self.device_id)
                    self.last_sync = data.get('last_sync', 0)
                    self._auto_sync = data.get('auto_sync', False)
                    self._sync_interval = data.get('sync_interval', 300)
                    
                    # Initialize backend
                    provider_type = data.get('provider', 'firebase')
                    if provider_type == 'firebase':
                        self.provider = FirebaseBackend(data.get('config', {}))
                    elif provider_type == 'supabase':
                        self.provider = SupabaseBackend(data.get('config', {}))
            except (json.JSONDecodeError, IOError):
                pass
    
    def _save_config(self):
        """Save sync configuration"""
        get_sync_config_dir()
        config_path = get_sync_config_path()
        
        data = {
            'device_id': self.device_id,
            'last_sync': self.last_sync,
            'auto_sync': self._auto_sync,
            'sync_interval': self._sync_interval
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def connect(self, provider: SyncProvider, config: Dict[str, Any]) -> bool:
        """Connect to sync provider"""
        if provider == SyncProvider.FIREBASE:
            self.provider = FirebaseBackend(config)
        elif provider == SyncProvider.SUPABASE:
            self.provider = SupabaseBackend(config)
        else:
            return False
        
        return self.provider.connect()
    
    def disconnect(self):
        """Disconnect from sync provider"""
        if self.provider:
            self.provider.disconnect()
            self.provider = None
        self.status = SyncStatus.OFFLINE
    
    def register_listener(self, event: str, callback: Callable):
        """Register event listener"""
        if event in self.listeners:
            self.listeners[event].append(callback)
    
    def _emit(self, event: str, *args, **kwargs):
        """Emit event to listeners"""
        if event in self.listeners:
            for callback in self.listeners[event]:
                try:
                    callback(*args, **kwargs)
                except Exception:
                    pass
    
    def sync_item(self, item: SyncItem) -> bool:
        """Sync a single item"""
        if not self.provider:
            return False
        
        self.status = SyncStatus.SYNCING
        self._emit('on_status_change', self.status)
        
        try:
            success = self.provider.push_item(item)
            
            if success:
                self.last_sync = time.time()
                self._save_config()
                self.status = SyncStatus.IDLE
                self._emit('on_status_change', self.status)
                self._emit('on_sync_complete', [item])
            
            return success
        except Exception as e:
            self.status = SyncStatus.ERROR
            self._emit('on_status_change', self.status)
            self._emit('on_error', str(e))
            return False
    
    def sync_all(self, item_types: List[SyncItemType] = None) -> bool:
        """Sync all items"""
        if not self.provider:
            return False
        
        if item_types is None:
            item_types = list(SyncItemType)
        
        self.status = SyncStatus.SYNCING
        self._emit('on_status_change', self.status)
        
        all_items = []
        
        for item_type in item_types:
            try:
                # Pull remote changes
                remote_items = self.provider.pull_items(item_type, self.last_sync)
                
                # Check for conflicts and merge
                for remote_item in remote_items:
                    conflict = self._check_conflict(remote_item)
                    if conflict:
                        self.conflicts.append(conflict)
                        self.status = SyncStatus.CONFLICT
                        self._emit('on_conflict', conflict)
                    else:
                        # Merge remote item
                        self._merge_item(remote_item)
                        all_items.append(remote_item)
                
            except Exception as e:
                self.status = SyncStatus.ERROR
                self._emit('on_error', str(e))
                return False
        
        self.last_sync = time.time()
        self._save_config()
        self.status = SyncStatus.IDLE
        self._emit('on_status_change', self.status)
        self._emit('on_sync_complete', all_items)
        
        return True
    
    def _check_conflict(self, remote_item: SyncItem) -> Optional[SyncConflict]:
        """Check if there's a conflict with local item"""
        # This would check local storage
        # Return conflict if exists
        return None
    
    def _merge_item(self, item: SyncItem):
        """Merge remote item into local storage"""
        # This would update local storage
        pass
    
    def resolve_conflict(self, conflict_id: str, resolution: str) -> bool:
        """Resolve a sync conflict"""
        conflict = next((c for c in self.conflicts if c.conflict_id == conflict_id), None)
        
        if not conflict:
            return False
        
        if resolution == "local":
            resolved = conflict.local_item
        elif resolution == "remote":
            resolved = conflict.remote_item
        elif resolution == "merge":
            resolved = ConflictResolver.merge_items(conflict.local_item, conflict.remote_item)
        else:
            return False
        
        conflict.resolved = True
        conflict.resolution = resolution
        conflict.resolved_item = resolved
        
        # Push resolved item
        if self.provider:
            self.provider.push_item(resolved)
        
        self._emit('on_sync_complete', [resolved])
        
        return True
    
    def get_conflicts(self) -> List[SyncConflict]:
        """Get all unresolved conflicts"""
        return [c for c in self.conflicts if not c.resolved]
    
    def enable_auto_sync(self, interval: int = 300):
        """Enable automatic syncing"""
        self._auto_sync = True
        self._sync_interval = interval
        self._save_config()
        
        if self._sync_thread and self._sync_thread.is_alive():
            return
        
        def auto_sync_loop():
            while self._auto_sync:
                time.sleep(self._sync_interval)
                self.sync_all()
        
        self._sync_thread = threading.Thread(target=auto_sync_loop, daemon=True)
        self._sync_thread.start()
    
    def disable_auto_sync(self):
        """Disable automatic syncing"""
        self._auto_sync = False
        self._save_config()
    
    def get_status(self) -> Dict[str, Any]:
        """Get sync status"""
        return {
            'status': self.status.value,
            'last_sync': self.last_sync,
            'device_id': self.device_id,
            'auto_sync': self._auto_sync,
            'conflicts_count': len(self.get_conflicts())
        }
    
    def get_devices(self) -> List[DeviceInfo]:
        """Get list of synced devices"""
        if self.provider:
            return self.provider.get_devices()
        return []


# Global instance
_sync_service_instance: Optional[SyncService] = None


def get_sync_service() -> SyncService:
    """Get or create the global sync service instance"""
    global _sync_service_instance
    if _sync_service_instance is None:
        _sync_service_instance = SyncService()
    return _sync_service_instance


# Convenience functions
def connect_sync(provider: SyncProvider, **config) -> bool:
    """Connect to sync provider"""
    service = get_sync_service()
    return service.connect(provider, config)


def sync_now() -> bool:
    """Trigger immediate sync"""
    service = get_sync_service()
    return service.sync_all()


def get_sync_status() -> Dict[str, Any]:
    """Get current sync status"""
    service = get_sync_service()
    return service.get_status()
