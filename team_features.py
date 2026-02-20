"""
DictaPilot Team Features Module
Handles team management, shared resources, and collaboration.

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
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime


def get_team_config_path() -> Path:
    """Get platform-specific team config path"""
    system = platform.system()
    
    if system == "Windows":
        data_dir = Path(os.environ.get("APPDATA", ""))
        return data_dir / "DictaPilot" / "team.json"
    else:
        data_dir = Path(os.path.expanduser("~/.local/share"))
        return data_dir / "dictapilot" / "team.json"


def get_team_config_dir() -> Path:
    """Create and return team config directory"""
    config_path = get_team_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    return config_path.parent


class TeamRole(Enum):
    """Team member roles"""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class ResourceType(Enum):
    """Shareable resource types"""
    SNIPPET = "snippet"
    DICTIONARY = "dictionary"
    COMMAND = "command"
    TEMPLATE = "template"
    SETTINGS = "settings"


class InviteStatus(Enum):
    """Team invite status"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "pending"
    EXPIRED = "expired"


@dataclass
class TeamMember:
    """A team member"""
    user_id: str
    email: str
    display_name: str
    role: TeamRole
    joined_at: float
    last_active: float
    is_online: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'user_id': self.user_id,
            'email': self.email,
            'display_name': self.display_name,
            'role': self.role.value,
            'joined_at': self.joined_at,
            'last_active': self.last_active,
            'is_online': self.is_online
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TeamMember":
        return cls(
            user_id=data['user_id'],
            email=data['email'],
            display_name=data['display_name'],
            role=TeamRole(data['role']),
            joined_at=data['joined_at'],
            last_active=data['last_active'],
            is_online=data.get('is_online', False)
        )


@dataclass
class SharedResource:
    """A shared resource"""
    resource_id: str
    resource_type: ResourceType
    name: str
    description: str
    owner_id: str
    team_id: str
    created_at: float
    updated_at: float
    data: Dict[str, Any]
    permissions: Dict[str, List[str]] = field(default_factory=dict)  # user_id -> permissions
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'resource_id': self.resource_id,
            'resource_type': self.resource_type.value,
            'name': self.name,
            'description': self.description,
            'owner_id': self.owner_id,
            'team_id': self.team_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'data': self.data,
            'permissions': self.permissions
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SharedResource":
        return cls(
            resource_id=data['resource_id'],
            resource_type=ResourceType(data['resource_type']),
            name=data['name'],
            description=data['description'],
            owner_id=data['owner_id'],
            team_id=data['team_id'],
            created_at=data['created_at'],
            updated_at=data['updated_at'],
            data=data['data'],
            permissions=data.get('permissions', {})
        )


@dataclass
class TeamInvite:
    """A team invite"""
    invite_id: str
    team_id: str
    email: str
    role: TeamRole
    invited_by: str
    created_at: float
    expires_at: float
    status: InviteStatus
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'invite_id': self.invite_id,
            'team_id': self.team_id,
            'email': self.email,
            'role': self.role.value,
            'invited_by': self.invited_by,
            'created_at': self.created_at,
            'expires_at': self.expires_at,
            'status': self.status.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TeamInvite":
        return cls(
            invite_id=data['invite_id'],
            team_id=data['team_id'],
            email=data['email'],
            role=TeamRole(data['role']),
            invited_by=data['invited_by'],
            created_at=data['created_at'],
            expires_at=data['expires_at'],
            status=InviteStatus(data['status'])
        )


@dataclass
class Team:
    """A team"""
    team_id: str
    name: str
    description: str
    owner_id: str
    created_at: float
    settings: Dict[str, Any]
    members: List[TeamMember] = field(default_factory=list)
    resources: List[SharedResource] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'team_id': self.team_id,
            'name': self.name,
            'description': self.description,
            'owner_id': self.owner_id,
            'created_at': self.created_at,
            'settings': self.settings,
            'members': [m.to_dict() for m in self.members],
            'resources': [r.to_dict() for r in self.resources]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Team":
        return cls(
            team_id=data['team_id'],
            name=data['name'],
            description=data['description'],
            owner_id=data['owner_id'],
            created_at=data['created_at'],
            settings=data.get('settings', {}),
            members=[TeamMember.from_dict(m) for m in data.get('members', [])],
            resources=[SharedResource.from_dict(r) for r in data.get('resources', [])]
        )


@dataclass
class TeamAnalytics:
    """Team usage analytics"""
    team_id: str
    period_start: float
    period_end: float
    total_dictations: int = 0
    total_words: int = 0
    total_time_minutes: float = 0
    top_users: List[Dict[str, Any]] = field(default_factory=list)
    top_snippets: List[Dict[str, Any]] = field(default_factory=list)
    usage_by_day: Dict[str, int] = field(default_factory=dict)


class TeamBackend:
    """Base team backend"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def create_team(self, team: Team) -> bool:
        """Create a new team"""
        raise NotImplementedError
    
    def get_team(self, team_id: str) -> Optional[Team]:
        """Get team by ID"""
        raise NotImplementedError
    
    def update_team(self, team: Team) -> bool:
        """Update team"""
        raise NotImplementedError
    
    def delete_team(self, team_id: str) -> bool:
        """Delete team"""
        raise NotImplementedError
    
    def add_member(self, team_id: str, member: TeamMember) -> bool:
        """Add member to team"""
        raise NotImplementedError
    
    def remove_member(self, team_id: str, user_id: str) -> bool:
        """Remove member from team"""
        raise NotImplementedError
    
    def share_resource(self, resource: SharedResource) -> bool:
        """Share resource with team"""
        raise NotImplementedError
    
    def get_shared_resources(self, team_id: str, resource_type: ResourceType = None) -> List[SharedResource]:
        """Get shared resources"""
        raise NotImplementedError
    
    def create_invite(self, invite: TeamInvite) -> str:
        """Create team invite"""
        raise NotImplementedError
    
    def accept_invite(self, invite_id: str) -> bool:
        """Accept team invite"""
        raise NotImplementedError


class LocalTeamBackend(TeamBackend):
    """Local-only team backend (for demo/offline)"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.teams: Dict[str, Team] = {}
        self.invites: Dict[str, TeamInvite] = {}
        self._load_data()
    
    def _load_data(self):
        """Load data from file"""
        config_path = get_team_config_path()
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.teams = {t['team_id']: Team.from_dict(t) for t in data.get('teams', [])}
                    self.invites = {i['invite_id']: TeamInvite.from_dict(i) for i in data.get('invites', [])}
            except (json.JSONDecodeError, IOError):
                pass
    
    def _save_data(self):
        """Save data to file"""
        get_team_config_dir()
        config_path = get_team_config_path()
        
        data = {
            'teams': [t.to_dict() for t in self.teams.values()],
            'invites': [i.to_dict() for i in self.invites.values()]
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def create_team(self, team: Team) -> bool:
        """Create a new team"""
        self.teams[team.team_id] = team
        self._save_data()
        return True
    
    def get_team(self, team_id: str) -> Optional[Team]:
        """Get team by ID"""
        return self.teams.get(team_id)
    
    def update_team(self, team: Team) -> bool:
        """Update team"""
        if team.team_id in self.teams:
            self.teams[team.team_id] = team
            self._save_data()
            return True
        return False
    
    def delete_team(self, team_id: str) -> bool:
        """Delete team"""
        if team_id in self.teams:
            del self.teams[team_id]
            self._save_data()
            return True
        return False
    
    def add_member(self, team_id: str, member: TeamMember) -> bool:
        """Add member to team"""
        team = self.teams.get(team_id)
        if team:
            team.members.append(member)
            self._save_data()
            return True
        return False
    
    def remove_member(self, team_id: str, user_id: str) -> bool:
        """Remove member from team"""
        team = self.teams.get(team_id)
        if team:
            team.members = [m for m in team.members if m.user_id != user_id]
            self._save_data()
            return True
        return False
    
    def share_resource(self, resource: SharedResource) -> bool:
        """Share resource with team"""
        team = self.teams.get(resource.team_id)
        if team:
            team.resources.append(resource)
            self._save_data()
            return True
        return False
    
    def get_shared_resources(self, team_id: str, resource_type: ResourceType = None) -> List[SharedResource]:
        """Get shared resources"""
        team = self.teams.get(team_id)
        if not team:
            return []
        
        if resource_type:
            return [r for r in team.resources if r.resource_type == resource_type]
        return team.resources
    
    def create_invite(self, invite: TeamInvite) -> str:
        """Create team invite"""
        self.invites[invite.invite_id] = invite
        self._save_data()
        return invite.invite_id
    
    def accept_invite(self, invite_id: str) -> bool:
        """Accept team invite"""
        invite = self.invites.get(invite_id)
        if invite:
            invite.status = InviteStatus.ACCEPTED
            self._save_data()
            return True
        return False


class TeamManager:
    """Main team management service"""
    
    def __init__(self):
        self.backend = LocalTeamBackend({})
        self.current_user_id = str(uuid.uuid4())
        self.current_team: Optional[Team] = None
        self._load_user_config()
    
    def _load_user_config(self):
        """Load user configuration"""
        config_path = get_team_config_path()
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.current_user_id = data.get('user_id', self.current_user_id)
            except (json.JSONDecodeError, IOError):
                pass
    
    def _save_user_config(self):
        """Save user configuration"""
        get_team_config_dir()
        config_path = get_team_config_path()
        
        # Save current teams and invites
        if hasattr(self.backend, 'teams'):
            data = {
                'user_id': self.current_user_id,
                'teams': [t.to_dict() for t in self.backend.teams.values()],
                'invites': [i.to_dict() for i in self.backend.invites.values()]
            }
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
    
    def create_team(self, name: str, description: str = "") -> Optional[Team]:
        """Create a new team"""
        team = Team(
            team_id=str(uuid.uuid4()),
            name=name,
            description=description,
            owner_id=self.current_user_id,
            created_at=datetime.now().timestamp(),
            settings={
                'allow_sharing': True,
                'require_approval': False,
                'default_role': TeamRole.MEMBER.value
            },
            members=[
                TeamMember(
                    user_id=self.current_user_id,
                    email="",
                    display_name="You",
                    role=TeamRole.OWNER,
                    joined_at=datetime.now().timestamp(),
                    last_active=datetime.now().timestamp(),
                    is_online=True
                )
            ]
        )
        
        if self.backend.create_team(team):
            self.current_team = team
            return team
        
        return None
    
    def join_team(self, invite_code: str) -> bool:
        """Join a team via invite"""
        # Would validate invite code
        return False
    
    def leave_team(self, team_id: str) -> bool:
        """Leave a team"""
        return self.backend.remove_member(team_id, self.current_user_id)
    
    def get_current_team(self) -> Optional[Team]:
        """Get current team"""
        return self.current_team
    
    def set_current_team(self, team_id: str):
        """Set current team"""
        self.current_team = self.backend.get_team(team_id)
    
    def get_teams(self) -> List[Team]:
        """Get all teams"""
        return list(self.backend.teams.values())
    
    def invite_member(self, email: str, role: TeamRole = TeamRole.MEMBER) -> Optional[str]:
        """Invite a member to the team"""
        if not self.current_team:
            return None
        
        invite = TeamInvite(
            invite_id=str(uuid.uuid4()),
            team_id=self.current_team.team_id,
            email=email,
            role=role,
            invited_by=self.current_user_id,
            created_at=datetime.now().timestamp(),
            expires_at=datetime.now().timestamp() + (7 * 24 * 60 * 60),  # 7 days
            status=InviteStatus.PENDING
        )
        
        return self.backend.create_invite(invite)
    
    def remove_member(self, user_id: str) -> bool:
        """Remove a member from the team"""
        if not self.current_team:
            return False
        
        return self.backend.remove_member(self.current_team.team_id, user_id)
    
    def update_member_role(self, user_id: str, role: TeamRole) -> bool:
        """Update a member's role"""
        if not self.current_team:
            return False
        
        for member in self.current_team.members:
            if member.user_id == user_id:
                member.role = role
                self.backend.update_team(self.current_team)
                return True
        
        return False
    
    def share_snippet(self, snippet_data: Dict[str, Any], name: str, description: str = "") -> bool:
        """Share a snippet with the team"""
        if not self.current_team:
            return False
        
        resource = SharedResource(
            resource_id=str(uuid.uuid4()),
            resource_type=ResourceType.SNIPPET,
            name=name,
            description=description,
            owner_id=self.current_user_id,
            team_id=self.current_team.team_id,
            created_at=datetime.now().timestamp(),
            updated_at=datetime.now().timestamp(),
            data=snippet_data
        )
        
        return self.backend.share_resource(resource)
    
    def share_dictionary(self, dictionary_data: Dict[str, Any], name: str, description: str = "") -> bool:
        """Share a dictionary with the team"""
        if not self.current_team:
            return False
        
        resource = SharedResource(
            resource_id=str(uuid.uuid4()),
            resource_type=ResourceType.DICTIONARY,
            name=name,
            description=description,
            owner_id=self.current_user_id,
            team_id=self.current_team.team_id,
            created_at=datetime.now().timestamp(),
            updated_at=datetime.now().timestamp(),
            data=dictionary_data
        )
        
        return self.backend.share_resource(resource)
    
    def get_shared_snippets(self) -> List[SharedResource]:
        """Get shared snippets"""
        if not self.current_team:
            return []
        
        return self.backend.get_shared_resources(
            self.current_team.team_id, 
            ResourceType.SNIPPET
        )
    
    def get_shared_dictionaries(self) -> List[SharedResource]:
        """Get shared dictionaries"""
        if not self.current_team:
            return []
        
        return self.backend.get_shared_resources(
            self.current_team.team_id,
            ResourceType.DICTIONARY
        )
    
    def adopt_shared_resource(self, resource_id: str) -> bool:
        """Adopt a shared resource to personal library"""
        if not self.current_team:
            return False
        
        resource = next(
            (r for r in self.current_team.resources if r.resource_id == resource_id),
            None
        )
        
        if not resource:
            return False
        
        # Would save to personal library
        return True
    
    def get_team_analytics(self, period_days: int = 30) -> TeamAnalytics:
        """Get team analytics"""
        if not self.current_team:
            return TeamAnalytics(
                team_id="",
                period_start=0,
                period_end=0
            )
        
        now = datetime.now().timestamp()
        period_start = now - (period_days * 24 * 60 * 60)
        
        return TeamAnalytics(
            team_id=self.current_team.team_id,
            period_start=period_start,
            period_end=now,
            total_dictations=0,
            total_words=0,
            total_time_minutes=0,
            top_users=[],
            top_snippets=[],
            usage_by_day={}
        )


# Global instance
_team_manager_instance: Optional[TeamManager] = None


def get_team_manager() -> TeamManager:
    """Get or create the global team manager instance"""
    global _team_manager_instance
    if _team_manager_instance is None:
        _team_manager_instance = TeamManager()
    return _team_manager_instance


# Convenience functions
def create_team(name: str, description: str = "") -> Optional[Team]:
    """Create a new team"""
    manager = get_team_manager()
    return manager.create_team(name, description)


def get_teams() -> List[Team]:
    """Get all teams"""
    manager = get_team_manager()
    return manager.get_teams()


def invite_to_team(email: str, role: TeamRole = TeamRole.MEMBER) -> Optional[str]:
    """Invite someone to the current team"""
    manager = get_team_manager()
    return manager.invite_member(email, role)
