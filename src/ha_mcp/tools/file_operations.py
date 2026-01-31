"""File operations tools for Home Assistant MCP Server.

Provides direct read/write access to Home Assistant configuration files.
"""

import logging
from pathlib import Path
from typing import Any

_LOGGER = logging.getLogger(__name__)

# Base path for all file operations
CONFIG_BASE = Path("/config")


def read_file(path: str) -> dict[str, Any]:
    """Read file contents from /config directory.
    
    Args:
        path: File path relative to /config (e.g., ".storage/core.config_entries")
    
    Returns:
        dict with success status, content, and path
    """
    try:
        # Ensure path is relative and within /config
        clean_path = Path(path.lstrip("/"))
        full_path = CONFIG_BASE / clean_path
        
        # Security check - prevent directory traversal
        if not str(full_path.resolve()).startswith(str(CONFIG_BASE.resolve())):
            return {
                "success": False,
                "error": "Access denied: Path outside /config directory"
            }
        
        if not full_path.exists():
            return {
                "success": False,
                "error": f"File not found: {path}"
            }
        
        if not full_path.is_file():
            return {
                "success": False,
                "error": f"Not a file: {path}"
            }
        
        content = full_path.read_text(encoding="utf-8")
        
        _LOGGER.info(f"Read file: {full_path}")
        
        return {
            "success": True,
            "content": content,
            "path": str(clean_path),
            "size": len(content)
        }
        
    except Exception as e:
        _LOGGER.error(f"Error reading file {path}: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def write_file(path: str, content: str) -> dict[str, Any]:
    """Write file contents to /config directory.
    
    Args:
        path: File path relative to /config
        content: File content to write
    
    Returns:
        dict with success status and path
    """
    try:
        # Ensure path is relative and within /config
        clean_path = Path(path.lstrip("/"))
        full_path = CONFIG_BASE / clean_path
        
        # Security check
        if not str(full_path.resolve()).startswith(str(CONFIG_BASE.resolve())):
            return {
                "success": False,
                "error": "Access denied: Path outside /config directory"
            }
        
        # Create parent directories if needed
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        full_path.write_text(content, encoding="utf-8")
        
        _LOGGER.info(f"Wrote file: {full_path}")
        
        return {
            "success": True,
            "path": str(clean_path),
            "size": len(content)
        }
        
    except Exception as e:
        _LOGGER.error(f"Error writing file {path}: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def list_directory(path: str = "") -> dict[str, Any]:
    """List directory contents in /config.
    
    Args:
        path: Directory path relative to /config (default: root)
    
    Returns:
        dict with success status and list of entries
    """
    try:
        # Ensure path is relative and within /config
        clean_path = Path(path.lstrip("/")) if path else Path(".")
        full_path = CONFIG_BASE / clean_path
        
        # Security check
        if not str(full_path.resolve()).startswith(str(CONFIG_BASE.resolve())):
            return {
                "success": False,
                "error": "Access denied: Path outside /config directory"
            }
        
        if not full_path.exists():
            return {
                "success": False,
                "error": f"Directory not found: {path}"
            }
        
        if not full_path.is_dir():
            return {
                "success": False,
                "error": f"Not a directory: {path}"
            }
        
        entries = []
        for item in sorted(full_path.iterdir()):
            entry = {
                "name": item.name,
                "type": "directory" if item.is_dir() else "file"
            }
            
            if item.is_file():
                entry["size"] = item.stat().st_size
            
            entries.append(entry)
        
        _LOGGER.info(f"Listed directory: {full_path} ({len(entries)} entries)")
        
        return {
            "success": True,
            "path": str(clean_path) if str(clean_path) != "." else "",
            "entries": entries,
            "count": len(entries)
        }
        
    except Exception as e:
        _LOGGER.error(f"Error listing directory {path}: {e}")
        return {
            "success": False,
            "error": str(e)
        }
