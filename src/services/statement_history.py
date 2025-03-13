from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.statement_history import StatementHistory
from src.models.accounts import Account

class StatementService:
    """
    Service for managing statement history records.
    
    This service is responsible for business logic related to StatementHistory
    models, including due date calculation, validation, and querying. It follows
    ADR-012 by keeping business logic out of the model layer.
    """
    
    def __init__(self, db: AsyncSession):
        """Initialize the service with a database session."""
        self.db = db
    
    def calculate_due_date(self, statement_date: datetime) -> datetime:
        """
        Calculate the due date based on a statement date.
        
        This method replaces the business logic that was previously in the
        StatementHistory.__init__ method, following ADR-012 requirements.
        
        Args:
            statement_date: The statement date
            
        Returns:
            datetime: The calculated due date (25 days after statement date)
        """
        return statement_date + timedelta(days=25)
    
    async def create_statement(
        self,
        account_id: int,
        statement_date: datetime,
        statement_balance: float,
        minimum_payment: Optional[float] = None,
        due_date: Optional[datetime] = None
    ) -> StatementHistory:
        """
        Create a new statement history record.
        
        If due_date is not provided, it will be calculated automatically.
        
        Args:
            account_id: ID of the account
            statement_date: Date of the statement
            statement_balance: Balance on the statement
            minimum_payment: Optional minimum payment amount
            due_date: Optional due date (if not provided, will be calculated)
            
        Returns:
            StatementHistory: The created statement history record
        """
        # Get account to verify it exists
        result = await self.db.execute(
            select(Account).where(Account.id == account_id)
        )
        account = result.scalar_one_or_none()
        
        if not account:
            raise ValueError(f"Account with ID {account_id} not found")
        
        # Calculate due date if not provided
        if due_date is None:
            due_date = self.calculate_due_date(statement_date)
        
        statement = StatementHistory(
            account_id=account_id,
            statement_date=statement_date,
            statement_balance=statement_balance,
            minimum_payment=minimum_payment,
            due_date=due_date
        )
        
        self.db.add(statement)
        return statement
    
    async def get_statement(self, statement_id: int) -> Optional[StatementHistory]:
        """Get a statement by ID."""
        result = await self.db.execute(
            select(StatementHistory).where(StatementHistory.id == statement_id)
        )
        return result.scalar_one_or_none()
    
    async def get_account_statements(
        self, account_id: int, limit: int = 12
    ) -> list[StatementHistory]:
        """
        Get statements for a specific account, ordered by date (newest first).
        
        Args:
            account_id: ID of the account
            limit: Maximum number of statements to return
            
        Returns:
            list[StatementHistory]: List of statement records
        """
        result = await self.db.execute(
            select(StatementHistory)
            .where(StatementHistory.account_id == account_id)
            .order_by(desc(StatementHistory.statement_date))
            .limit(limit)
        )
        return result.scalars().all()
