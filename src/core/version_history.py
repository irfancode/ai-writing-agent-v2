"""Version History - Track and manage content versions"""

import json
import os
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path
import difflib


@dataclass
class Version:
    """A single version of content"""
    version_id: str
    content: str
    timestamp: float
    word_count: int
    delta: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DocumentHistory:
    """Complete history of a document"""
    document_id: str
    versions: List[Version] = field(default_factory=list)
    current_version: Optional[str] = None
    created_at: float = 0
    updated_at: float = 0


class VersionHistory:
    """Manages version history for documents"""
    
    def __init__(self, storage_dir: Optional[str] = None):
        if storage_dir:
            self.storage_dir = Path(storage_dir)
        else:
            self.storage_dir = Path.home() / ".ai-writing-agent" / "history"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.documents: Dict[str, DocumentHistory] = {}
        self._load_all()
    
    def save_version(
        self,
        document_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Save a new version of a document"""
        if document_id not in self.documents:
            doc = DocumentHistory(
                document_id=document_id,
                created_at=datetime.now().timestamp(),
            )
            self.documents[document_id] = doc
        else:
            doc = self.documents[document_id]
        
        previous = doc.versions[-1].content if doc.versions else None
        delta = self._compute_delta(previous, content) if previous else None
        
        version_id = f"v{doc.versions.__len__() + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        version = Version(
            version_id=version_id,
            content=content,
            timestamp=datetime.now().timestamp(),
            word_count=len(content.split()),
            delta=delta,
            metadata=metadata or {},
        )
        
        doc.versions.append(version)
        doc.current_version = version_id
        doc.updated_at = datetime.now().timestamp()
        
        self._save_document(doc)
        
        return version_id
    
    def get_version(self, document_id: str, version_id: str) -> Optional[Version]:
        """Get a specific version"""
        doc = self.documents.get(document_id)
        if not doc:
            return None
        
        for v in doc.versions:
            if v.version_id == version_id:
                return v
        return None
    
    def get_current(self, document_id: str) -> Optional[Version]:
        """Get current version"""
        doc = self.documents.get(document_id)
        if not doc or not doc.current_version:
            return None
        return self.get_version(document_id, doc.current_version)
    
    def list_versions(self, document_id: str) -> List[Dict[str, Any]]:
        """List all versions of a document"""
        doc = self.documents.get(document_id)
        if not doc:
            return []
        
        return [
            {
                "version_id": v.version_id,
                "timestamp": v.timestamp,
                "word_count": v.word_count,
                "delta": v.delta,
                "metadata": v.metadata,
            }
            for v in reversed(doc.versions)
        ]
    
    def rollback(self, document_id: str, version_id: str) -> Optional[str]:
        """Rollback to a specific version"""
        version = self.get_version(document_id, version_id)
        if not version:
            return None
        
        return self.save_version(document_id, version.content, {"action": "rollback"})
    
    def compare_versions(
        self,
        document_id: str,
        version_id_1: str,
        version_id_2: str,
    ) -> str:
        """Compare two versions"""
        v1 = self.get_version(document_id, version_id_1)
        v2 = self.get_version(document_id, version_id_2)
        
        if not v1 or not v2:
            return "One or both versions not found"
        
        diff = difflib.unified_diff(
            v1.content.splitlines(keepends=True),
            v2.content.splitlines(keepends=True),
            fromfile=version_id_1,
            tofile=version_id_2,
            lineterm="",
        )
        
        return "".join(diff)
    
    def delete_document(self, document_id: str):
        """Delete a document and all its versions"""
        if document_id in self.documents:
            del self.documents[document_id]
            self._delete_document_file(document_id)
    
    def _compute_delta(self, old: str, new: str) -> str:
        """Compute a brief summary of changes"""
        old_words = set(old.lower().split())
        new_words = set(new.lower().split())
        
        added = new_words - old_words
        removed = old_words - new_words
        
        changes = []
        if len(added) > 0:
            changes.append(f"+{len(added)} words")
        if len(removed) > 0:
            changes.append(f"-{len(removed)} words")
        
        word_diff = len(new.split()) - len(old.split())
        if word_diff != 0:
            changes.append(f"({'+' if word_diff > 0 else ''}{word_diff} total)")
        
        return ", ".join(changes) if changes else "no change"
    
    def _save_document(self, doc: DocumentHistory):
        """Save document to disk"""
        data = {
            "document_id": doc.document_id,
            "created_at": doc.created_at,
            "updated_at": doc.updated_at,
            "current_version": doc.current_version,
            "versions": [
                {
                    "version_id": v.version_id,
                    "content": v.content,
                    "timestamp": v.timestamp,
                    "word_count": v.word_count,
                    "delta": v.delta,
                    "metadata": v.metadata,
                }
                for v in doc.versions
            ],
        }
        
        safe_id = "".join(c for c in doc.document_id if c.isalnum())
        with open(self.storage_dir / f"{safe_id}.json", "w") as f:
            json.dump(data, f, indent=2)
    
    def _load_all(self):
        """Load all documents from disk"""
        for file in self.storage_dir.glob("*.json"):
            try:
                with open(file) as f:
                    data = json.load(f)
                    doc = DocumentHistory(
                        document_id=data["document_id"],
                        created_at=data.get("created_at", 0),
                        updated_at=data.get("updated_at", 0),
                        current_version=data.get("current_version"),
                    )
                    doc.versions = [
                        Version(
                            version_id=v["version_id"],
                            content=v["content"],
                            timestamp=v["timestamp"],
                            word_count=v["word_count"],
                            delta=v.get("delta"),
                            metadata=v.get("metadata", {}),
                        )
                        for v in data.get("versions", [])
                    ]
                    self.documents[data["document_id"]] = doc
            except Exception:
                continue
    
    def _delete_document_file(self, document_id: str):
        """Delete document file from disk"""
        safe_id = "".join(c for c in document_id if c.isalnum())
        file_path = self.storage_dir / f"{safe_id}.json"
        if file_path.exists():
            file_path.unlink()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get overall statistics"""
        total_docs = len(self.documents)
        total_versions = sum(len(d.versions) for d in self.documents.values())
        
        return {
            "documents": total_docs,
            "total_versions": total_versions,
            "storage_used_mb": sum(f.stat().st_size for f in self.storage_dir.glob("*.json")) / 1024 / 1024,
        }


version_history = VersionHistory()
