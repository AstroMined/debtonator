"""
Test models for polymorphic repository testing.

This module contains model classes specifically designed for testing the
polymorphic repository functionality. These models are intentionally
simple and focused on testing polymorphic entity relationships.
"""

from sqlalchemy import Column, ForeignKey, Integer, String

from src.database.base import Base


class TestBaseModel(Base):
    """
    Base model for polymorphic entity testing.
    
    This model serves as the base class for polymorphic entity testing,
    using model_type as the discriminator column.
    """
    __tablename__ = "test_base_models"
    __mapper_args__ = {"polymorphic_on": "model_type", "polymorphic_identity": "base"}

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    model_type = Column(String, nullable=False)


class TestTypeAModel(TestBaseModel):
    """
    Test model for Type A entities.
    
    This model extends TestBaseModel with an optional a_field property.
    """
    __tablename__ = "test_type_a_models"
    __mapper_args__ = {"polymorphic_identity": "type_a"}

    id = Column(Integer, ForeignKey("test_base_models.id"), primary_key=True)
    a_field = Column(String, nullable=True)


class TestTypeBModel(TestBaseModel):
    """
    Test model for Type B entities.
    
    This model extends TestBaseModel with a required b_field property
    to test handling of required fields in polymorphic entities.
    """
    __tablename__ = "test_type_b_models"
    __mapper_args__ = {"polymorphic_identity": "type_b"}

    id = Column(Integer, ForeignKey("test_base_models.id"), primary_key=True)
    b_field = Column(String, nullable=False)  # Required field
