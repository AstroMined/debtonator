"""
Version information for the Debtonator application.

This module provides consistent access to the current version of the 
application across different parts of the codebase. It allows both programmatic 
access to version components and a formatted string version for display.
"""

VERSION_MAJOR = 0
VERSION_MINOR = 4
VERSION_PATCH = 10

VERSION = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}"
VERSION_TUPLE = (VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH)

__all__ = ["VERSION", "VERSION_TUPLE", "VERSION_MAJOR", "VERSION_MINOR", "VERSION_PATCH"]
