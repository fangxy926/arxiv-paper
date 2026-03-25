#!/usr/bin/env python3
"""Shared utility functions for the arXiv paper pipeline."""
import json
import os
from pathlib import Path
from typing import Any, Optional


def load_json(filepath: str, default: Optional[Any] = None) -> Any:
    """Load JSON from file with error handling.

    Args:
        filepath: Path to JSON file
        default: Default value to return if file doesn't exist or is invalid

    Returns:
        Parsed JSON data or default value
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, IOError):
        return default


def save_json(filepath: str, data: Any) -> bool:
    """Save data to JSON file with proper formatting.

    Args:
        filepath: Path to output file
        data: Data to serialize

    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure parent directory exists
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except (IOError, OSError) as e:
        print(f"[WARN] Failed to save JSON to {filepath}: {e}")
        return False


def get_data_path(filename: str) -> str:
    """Get full path for a data file in OUTPUT_DIR.

    Args:
        filename: Name of the file

    Returns:
        Full path to the file
    """
    output_dir = os.getenv('OUTPUT_DIR', '.')
    return os.path.join(output_dir, filename)


def ensure_output_dir() -> str:
    """Ensure OUTPUT_DIR exists and return its path.

    Returns:
        Path to output directory
    """
    output_dir = os.getenv('OUTPUT_DIR', '.')
    os.makedirs(output_dir, exist_ok=True)
    return output_dir
