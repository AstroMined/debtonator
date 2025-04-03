import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from alembic.config import Config

# Import our models and config
from src.database.base import Base

# from src.models.accounts import Account
# from src.models.balance_history import BalanceHistory
# from src.models.balance_reconciliation import BalanceReconciliation
# from src.models.bill_splits import BillSplit
# from src.models.cashflow import CashflowForecast
# from src.models.categories import Category
# from src.models.credit_limit_history import CreditLimitHistory
# from src.models.deposit_schedules import DepositSchedule
# from src.models.feature_flags import FeatureFlag
# from src.models.income_categories import IncomeCategory
# from src.models.income import Income
# from src.models.liabilities import Liability
# from src.models.payment_schedules import PaymentSchedule
# from src.models.payments import Payment, PaymentSource
# from src.models.recurring_bills import RecurringBill
# from src.models.recurring_income import RecurringIncome
# from src.models.statement_history import StatementHistory
# from src.models.transaction_history import TransactionHistory
from src.utils.config import get_settings

settings = get_settings()
# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the database URL from our settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Add model's MetaData object for 'autogenerate' support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
