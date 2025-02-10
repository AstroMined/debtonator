import pytest
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import text, Table, Column, Integer, String, Numeric, Date, Boolean, DateTime, MetaData
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
from alembic.config import Config
from alembic import command

def get_alembic_config(connection) -> Config:
    """Create Alembic config with the given connection"""
    config = Config()
    config.set_main_option("script_location", "alembic")
    config.attributes["connection"] = connection
    return config

def run_migrations(connection):
    """Run migrations using the given connection"""
    config = get_alembic_config(connection)
    command.upgrade(config, "head")

def run_rollback(connection):
    """Run rollback using the given connection"""
    config = get_alembic_config(connection)
    command.downgrade(config, "base")

@pytest.fixture(autouse=True)
async def setup_legacy_bills_table(db_session: AsyncSession):
    """Create a legacy bills table with sample data"""
    try:
        # Create legacy bills table
        await db_session.execute(text("""
            CREATE TABLE bills (
                id INTEGER PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                amount DECIMAL(10, 2) NOT NULL,
                due_date DATE NOT NULL,
                paid BOOLEAN DEFAULT FALSE,
                account_id INTEGER,
                payment_date DATE,
                category VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        await db_session.commit()

        # Insert sample data
        await db_session.execute(text("""
            INSERT INTO bills (name, amount, due_date, paid, account_id, payment_date, category)
            VALUES 
            ('Test Bill 1', 100.00, '2025-01-01', true, 1, '2025-01-01', 'Utilities'),
            ('Test Bill 2', 200.00, '2025-02-01', false, null, null, 'Rent'),
            ('Test Bill 3', 150.00, '2025-01-15', true, 2, '2025-01-15', 'Insurance')
        """))
        await db_session.commit()
    except Exception as e:
        print(f"Error setting up legacy bills table: {e}")
        raise

@pytest.mark.asyncio
async def test_migration_creates_new_tables(db_session: AsyncSession):
    """Test that migration creates the new tables with correct structure"""
    # Get raw connection
    connection = await db_session.connection()
    raw_connection = await connection.get_raw_connection()
    
    # Run migrations using the connection
    run_migrations(raw_connection)

    # Check if tables exist
    result = await db_session.execute(text(
        "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('liabilities', 'payments', 'payment_sources')"
    ))
    tables = result.scalars().all()
    
    assert 'liabilities' in tables
    assert 'payments' in tables
    assert 'payment_sources' in tables

    # Verify liabilities table structure
    result = await db_session.execute(text("PRAGMA table_info(liabilities)"))
    columns = {row[1]: row[2] for row in result.fetchall()}
    
    assert 'name' in columns
    assert 'amount' in columns
    assert 'due_date' in columns
    assert 'category' in columns
    assert 'recurring' in columns
    assert 'recurrence_pattern' in columns

@pytest.mark.asyncio
async def test_migration_transfers_data(db_session: AsyncSession):
    """Test that data is correctly migrated from bills to new tables"""
    # Get data from legacy bills table
    bills_result = await db_session.execute(text("SELECT * FROM bills"))
    original_bills = bills_result.fetchall()
    
    # Get raw connection
    connection = await db_session.connection()
    raw_connection = await connection.get_raw_connection()
    
    # Run migrations using the connection
    run_migrations(raw_connection)
    
    # Verify liabilities data
    liabilities_result = await db_session.execute(text("SELECT * FROM liabilities"))
    liabilities = liabilities_result.fetchall()
    assert len(liabilities) == len(original_bills)
    
    # Verify payments data
    payments_result = await db_session.execute(text("SELECT * FROM payments"))
    payments = payments_result.fetchall()
    # Only paid bills should have payments
    assert len(payments) == len([b for b in original_bills if b.paid])
    
    # Verify payment sources
    sources_result = await db_session.execute(text("SELECT * FROM payment_sources"))
    sources = sources_result.fetchall()
    # Only paid bills with account_id should have sources
    assert len(sources) == len([b for b in original_bills if b.paid and b.account_id is not None])

@pytest.mark.asyncio
async def test_migration_preserves_relationships(db_session: AsyncSession):
    """Test that relationships between entities are preserved during migration"""
    # Get raw connection
    connection = await db_session.connection()
    raw_connection = await connection.get_raw_connection()
    
    # Run migrations using the connection
    run_migrations(raw_connection)
    
    # Check relationships
    result = await db_session.execute(text("""
        SELECT l.name, p.amount, ps.account_id
        FROM liabilities l
        JOIN payments p ON p.bill_id = l.id
        JOIN payment_sources ps ON ps.payment_id = p.id
        WHERE l.name = 'Test Bill 1'
    """))
    relationship_data = result.fetchone()
    
    assert relationship_data is not None
    assert relationship_data.name == 'Test Bill 1'
    assert relationship_data.amount == Decimal('100.00')
    assert relationship_data.account_id == 1

@pytest.mark.asyncio
async def test_migration_handles_missing_data(db_session: AsyncSession):
    """Test that migration handles bills with missing optional data"""
    # Insert bill with minimal data
    await db_session.execute(text("""
        INSERT INTO bills (name, amount, due_date)
        VALUES ('Minimal Bill', 50.00, '2025-03-01')
    """))
    await db_session.commit()
    
    # Get raw connection
    connection = await db_session.connection()
    raw_connection = await connection.get_raw_connection()
    
    # Run migrations using the connection
    run_migrations(raw_connection)
    
    # Verify minimal bill was migrated
    result = await db_session.execute(text("""
        SELECT * FROM liabilities WHERE name = 'Minimal Bill'
    """))
    minimal_bill = result.fetchone()
    
    assert minimal_bill is not None
    assert minimal_bill.amount == Decimal('50.00')
    assert minimal_bill.category == 'Uncategorized'  # Default category
    assert minimal_bill.recurring is False  # Default value

@pytest.mark.asyncio
async def test_migration_rollback(db_session: AsyncSession):
    """Test that migration can be rolled back"""
    # Get raw connection
    connection = await db_session.connection()
    raw_connection = await connection.get_raw_connection()
    
    # Run migrations using the connection
    run_migrations(raw_connection)
    
    # Verify new tables exist
    result = await db_session.execute(text(
        "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('liabilities', 'payments', 'payment_sources')"
    ))
    tables_after_upgrade = set(result.scalars().all())
    assert tables_after_upgrade == {'liabilities', 'payments', 'payment_sources'}
    
    # Rollback using the same connection
    run_rollback(raw_connection)
    
    # Verify new tables are dropped
    result = await db_session.execute(text(
        "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('liabilities', 'payments', 'payment_sources')"
    ))
    tables_after_downgrade = result.scalars().all()
    assert len(tables_after_downgrade) == 0
