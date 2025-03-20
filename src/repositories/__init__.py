"""
Repository layer for CRUD operations.

This module provides a standardized approach to database operations through the repository pattern.
Repositories handle all interactions with the database, separating data access from business logic.
"""

from src.repositories.base import BaseRepository, ModelType, PKType
from src.repositories.factory import RepositoryFactory
from src.repositories.accounts import AccountRepository
