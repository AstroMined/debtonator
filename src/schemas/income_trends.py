from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pydantic import ConfigDict, Field, field_validator

from src.schemas import BaseSchemaValidator, MoneyDecimal, PercentageDecimal


class FrequencyType(str, Enum):
    """
    Enumeration of income frequency types.

    Used to categorize different patterns of income frequency.
    """

    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    IRREGULAR = "irregular"


class IncomePattern(BaseSchemaValidator):
    """
    Pattern identified in income data.

    Contains information about recurring income patterns, including frequency
    and statistical measures.
    All datetime fields are validated to ensure they have UTC timezone.
    """

    source: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Source of the income (e.g., employer name)",
    )
    frequency: FrequencyType = Field(..., description="Frequency pattern of the income")
    average_amount: MoneyDecimal = Field(
        ..., gt=0, description="Average amount of income from this source"
    )
    confidence_score: PercentageDecimal = Field(
        ..., description="Confidence score for this pattern (0-1)"
    )
    last_occurrence: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Date of the last occurrence of this income (UTC timezone)",
    )
    next_predicted: Optional[datetime] = Field(
        None, description="Predicted date of the next occurrence (UTC timezone)"
    )
    # No custom validators needed - BaseSchemaValidator handles UTC validation


class PeriodType(str, Enum):
    """
    Enumeration of period types for seasonality analysis.

    Used to specify the time period for seasonal income patterns.
    """

    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"


class SeasonalityMetrics(BaseSchemaValidator):
    """
    Seasonal patterns in income.

    Contains metrics about seasonal variations in income patterns.
    """

    period: PeriodType = Field(..., description="Period type for seasonality analysis")
    peak_months: List[int] = Field(
        ...,
        min_items=1,
        max_items=12,
        description="Months with peak income (1-12 representing months)",
    )
    trough_months: List[int] = Field(
        ...,
        min_items=1,
        max_items=12,
        description="Months with lowest income (1-12 representing months)",
    )
    variance_coefficient: float = Field(
        ..., ge=0.0, description="Coefficient of variance in seasonal income"
    )
    confidence_score: PercentageDecimal = Field(
        ..., description="Confidence score for seasonality detection (0-1)"
    )

    @field_validator("peak_months", "trough_months")
    @classmethod
    def validate_months(cls, value: List[int]) -> List[int]:
        """
        Validate that month values are in the valid range and unique.

        Args:
            value: List of month numbers to validate

        Returns:
            The original list if valid

        Raises:
            ValueError: If any month is outside 1-12 range or there are duplicates
        """
        if not all(1 <= month <= 12 for month in value):
            raise ValueError("Months must be between 1 and 12")
        if len(set(value)) != len(value):
            raise ValueError("Duplicate months are not allowed")
        return value


class SourceStatistics(BaseSchemaValidator):
    """
    Statistical analysis for an income source.

    Contains detailed statistical metrics about an income source.
    """

    source: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Source of the income (e.g., employer name)",
    )
    total_occurrences: int = Field(
        ..., gt=0, description="Total number of times this income source has occurred"
    )
    total_amount: MoneyDecimal = Field(
        ..., ge=0, description="Total amount received from this source"
    )
    average_amount: MoneyDecimal = Field(
        ..., gt=0, description="Average amount per occurrence"
    )
    min_amount: MoneyDecimal = Field(
        ..., ge=0, description="Minimum amount received from this source"
    )
    max_amount: MoneyDecimal = Field(
        ..., gt=0, description="Maximum amount received from this source"
    )
    standard_deviation: float = Field(
        ..., ge=0.0, description="Standard deviation of amounts"
    )
    reliability_score: PercentageDecimal = Field(
        ..., description="Reliability score for this source (0-1)"
    )

    @field_validator("max_amount")
    @classmethod
    def validate_max_amount(cls, v: Decimal, info) -> Decimal:
        """
        Validate that max_amount is greater than or equal to min_amount.

        Args:
            v: The max_amount value to validate
            info: ValidationInfo object containing values being validated

        Returns:
            The original value if validation passes

        Raises:
            ValueError: If max_amount is less than min_amount
        """
        if "min_amount" in info.data and v < info.data["min_amount"]:
            raise ValueError("max_amount must be greater than or equal to min_amount")
        return v


class IncomeTrendsAnalysis(BaseSchemaValidator):
    """
    Complete income trends analysis.

    Contains comprehensive analysis of income patterns, seasonality,
    and statistical metrics across all sources.
    All datetime fields are validated to ensure they have UTC timezone.
    """

    patterns: List[IncomePattern] = Field(
        ..., min_items=1, description="List of identified income patterns"
    )
    seasonality: Optional[SeasonalityMetrics] = Field(
        None, description="Seasonal patterns if detected"
    )
    source_statistics: List[SourceStatistics] = Field(
        ..., min_items=1, description="Statistical analysis per income source"
    )
    analysis_date: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Date when analysis was performed (UTC timezone)",
    )
    data_start_date: datetime = Field(
        ..., description="Start date of the analyzed data period (UTC timezone)"
    )
    data_end_date: datetime = Field(
        ..., description="End date of the analyzed data period (UTC timezone)"
    )
    overall_predictability_score: PercentageDecimal = Field(
        ..., description="Overall predictability score for future income (0-1)"
    )

    @field_validator("data_end_date")
    @classmethod
    def validate_date_range(cls, v: datetime, info) -> datetime:
        """
        Validate that end date is after start date.

        Args:
            v: The end date value to validate
            info: ValidationInfo object containing values being validated

        Returns:
            The original value if validation passes

        Raises:
            ValueError: If end date is before start date
        """
        if "data_start_date" in info.data and v < info.data["data_start_date"]:
            raise ValueError("data_end_date must be after data_start_date")
        return v

    # No custom timezone validators needed - BaseSchemaValidator handles UTC validation


class IncomeTrendsRequest(BaseSchemaValidator):
    """
    Request parameters for trends analysis.

    Contains request parameters for generating income trend analysis.
    All datetime fields are validated to ensure they have UTC timezone.
    """

    start_date: Optional[datetime] = Field(
        None, description="Optional start date for analysis period (UTC timezone)"
    )
    end_date: Optional[datetime] = Field(
        None, description="Optional end date for analysis period (UTC timezone)"
    )
    source: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Optional specific income source to analyze",
    )
    min_confidence: PercentageDecimal = Field(
        default=Decimal("0.5"),
        description="Minimum confidence score for included patterns (0-1)",
    )

    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, v: Optional[datetime], info) -> Optional[datetime]:
        """
        Validate that end date is after start date if both are provided.

        Args:
            v: The end date value to validate
            info: ValidationInfo object containing values being validated

        Returns:
            The original value if validation passes

        Raises:
            ValueError: If end date is before start date
        """
        if (
            v
            and "start_date" in info.data
            and info.data["start_date"]
            and v < info.data["start_date"]
        ):
            raise ValueError("end_date must be after start_date")
        return v

    # No custom timezone validators needed - BaseSchemaValidator handles UTC validation

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "start_date": "2024-01-01T00:00:00Z",
                "end_date": "2024-12-31T23:59:59Z",
                "source": "salary",
                "min_confidence": 0.7,
            }
        }
    )
