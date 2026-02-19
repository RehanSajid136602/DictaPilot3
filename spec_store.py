"""
DictaPilot Specification Store
Manages storage and versioning of specifications

Original by: Rohan Sharvesh
Fork maintained by: Rehan

MIT License
Copyright (c) 2026 Rohan Sharvesh
Copyright (c) 2026 Rehan
"""

import json
import os
import platform
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime
from dataclasses import asdict
from spec_generator import Specification


def get_spec_storage_path() -> Path:
    """Get platform-specific spec storage path"""
    system = platform.system()
    
    if system == "Windows":
        base_dir = Path(os.environ.get("APPDATA", ""))
        return base_dir / "DictaPilot" / "specs"
    else:
        base_dir = Path(os.path.expanduser("~/.local/share"))
        return base_dir / "dictapilot" / "specs"


class SpecStore:
    """Manages specification storage and versioning"""
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or get_spec_storage_path()
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.index_file = self.storage_path / "index.json"
        self._load_index()
    
    def _load_index(self):
        """Load spec index from disk"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r') as f:
                    self.index = json.load(f)
            except Exception:
                self.index = {"specs": [], "version": "1.0"}
        else:
            self.index = {"specs": [], "version": "1.0"}
    
    def _save_index(self):
        """Save spec index to disk"""
        try:
            with open(self.index_file, 'w') as f:
                json.dump(self.index, f, indent=2)
        except Exception as e:
            print(f"Error saving index: {e}")
    
    def save_spec(self, spec: Specification, format_style: str = "standard") -> Optional[str]:
        """Save specification and return spec ID"""
        spec_id = self._generate_spec_id(spec.title)
        spec_dir = self.storage_path / spec_id
        spec_dir.mkdir(parents=True, exist_ok=True)
        
        # Save markdown version
        md_file = spec_dir / "spec.md"
        try:
            with open(md_file, 'w') as f:
                f.write(spec.to_markdown(format_style))
        except Exception as e:
            print(f"Error saving spec markdown: {e}")
            return None
        
        # Save JSON version for easy parsing
        json_file = spec_dir / "spec.json"
        try:
            spec_dict = asdict(spec)
            with open(json_file, 'w') as f:
                json.dump(spec_dict, f, indent=2)
        except Exception as e:
            print(f"Error saving spec JSON: {e}")
        
        # Update index
        spec_entry = {
            "id": spec_id,
            "title": spec.title,
            "created_at": spec.created_at,
            "updated_at": spec.updated_at,
            "metadata": spec.metadata,
            "path": str(spec_dir)
        }
        
        # Remove old entry if exists
        self.index["specs"] = [s for s in self.index["specs"] if s["id"] != spec_id]
        self.index["specs"].append(spec_entry)
        self._save_index()
        
        return spec_id
    
    def load_spec(self, spec_id: str) -> Optional[Specification]:
        """Load specification by ID"""
        spec_dir = self.storage_path / spec_id
        json_file = spec_dir / "spec.json"
        
        if not json_file.exists():
            return None
        
        try:
            with open(json_file, 'r') as f:
                spec_dict = json.load(f)
            
            return Specification(**spec_dict)
        except Exception as e:
            print(f"Error loading spec: {e}")
            return None
    
    def list_specs(self, limit: int = 50) -> List[Dict]:
        """List all specifications"""
        specs = sorted(
            self.index["specs"],
            key=lambda x: x.get("updated_at", ""),
            reverse=True
        )
        return specs[:limit]
    
    def search_specs(self, query: str) -> List[Dict]:
        """Search specifications by title or metadata"""
        query_lower = query.lower()
        results = []
        
        for spec_entry in self.index["specs"]:
            if query_lower in spec_entry["title"].lower():
                results.append(spec_entry)
            elif any(query_lower in str(v).lower() for v in spec_entry.get("metadata", {}).values()):
                results.append(spec_entry)
        
        return results
    
    def delete_spec(self, spec_id: str) -> bool:
        """Delete specification"""
        spec_dir = self.storage_path / spec_id
        
        if spec_dir.exists():
            try:
                import shutil
                shutil.rmtree(spec_dir)
            except Exception as e:
                print(f"Error deleting spec directory: {e}")
                return False
        
        self.index["specs"] = [s for s in self.index["specs"] if s["id"] != spec_id]
        self._save_index()
        return True
    
    def export_spec(self, spec_id: str, output_path: Path, format_style: str = "standard") -> bool:
        """Export specification to file"""
        spec = self.load_spec(spec_id)
        if not spec:
            return False
        
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(spec.to_markdown(format_style))
            return True
        except Exception as e:
            print(f"Error exporting spec: {e}")
            return False
    
    def get_spec_versions(self, spec_id: str) -> List[Dict]:
        """Get version history of a specification"""
        spec_dir = self.storage_path / spec_id / "versions"
        
        if not spec_dir.exists():
            return []
        
        versions = []
        for version_file in sorted(spec_dir.glob("*.json")):
            try:
                with open(version_file, 'r') as f:
                    version_data = json.load(f)
                versions.append({
                    "timestamp": version_data.get("updated_at", ""),
                    "file": str(version_file)
                })
            except Exception:
                continue
        
        return versions
    
    def create_version(self, spec_id: str) -> bool:
        """Create a version snapshot of current spec"""
        spec = self.load_spec(spec_id)
        if not spec:
            return False
        
        spec_dir = self.storage_path / spec_id
        versions_dir = spec_dir / "versions"
        versions_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version_file = versions_dir / f"v_{timestamp}.json"
        
        try:
            spec_dict = asdict(spec)
            with open(version_file, 'w') as f:
                json.dump(spec_dict, f, indent=2)
            return True
        except Exception as e:
            print(f"Error creating version: {e}")
            return False
    
    def _generate_spec_id(self, title: str) -> str:
        """Generate unique spec ID from title"""
        import re
        
        # Convert to lowercase and replace spaces with hyphens
        spec_id = title.lower().strip()
        spec_id = re.sub(r'[^\w\s-]', '', spec_id)
        spec_id = re.sub(r'[-\s]+', '-', spec_id)
        
        # Add timestamp to ensure uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        spec_id = f"{spec_id}_{timestamp}"
        
        return spec_id
    
    def get_storage_info(self) -> Dict:
        """Get storage statistics"""
        total_specs = len(self.index["specs"])
        total_size = 0
        
        for spec_entry in self.index["specs"]:
            spec_dir = Path(spec_entry["path"])
            if spec_dir.exists():
                for file in spec_dir.rglob("*"):
                    if file.is_file():
                        total_size += file.stat().st_size
        
        return {
            "total_specs": total_specs,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "storage_path": str(self.storage_path)
        }
