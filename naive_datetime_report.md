# Naive Datetime Usage Report

## Summary

Found 137 instances of naive datetime usage.

## Details by File

### tests/integration/api/test_balance_reconciliation_api.py

| Line | Code | Context |
|------|------|--------|
| 19 | `datetime.utcnow()` | `created_at=datetime.utcnow(),` |
| 20 | `datetime.utcnow()` | `updated_at=datetime.utcnow(),` |
| 37 | `datetime.utcnow()` | `reconciliation_date=datetime.utcnow(),` |
| 38 | `datetime.utcnow()` | `created_at=datetime.utcnow(),` |
| 39 | `datetime.utcnow()` | `updated_at=datetime.utcnow(),` |

### tests/integration/api/test_payment_schedules_api.py

| Line | Code | Context |
|------|------|--------|
| 37 | `datetime.utcnow()` | `created_at=datetime.utcnow(),` |
| 38 | `datetime.utcnow()` | `updated_at=datetime.utcnow(),` |
| 55 | `datetime.utcnow()` | `created_at=datetime.utcnow(),` |
| 56 | `datetime.utcnow()` | `updated_at=datetime.utcnow(),` |

### tests/integration/api/test_realtime_cashflow_api.py

| Line | Code | Context |
|------|------|--------|
| 18 | `datetime.now()` | `created_at=datetime.now().date(),` |
| 19 | `datetime.now()` | `updated_at=datetime.now().date(),` |
| 27 | `datetime.now()` | `created_at=datetime.now().date(),` |
| 28 | `datetime.now()` | `updated_at=datetime.now().date(),` |
| 41 | `datetime.now()` | `today = datetime.now().date()` |
| 54 | `datetime.now()` | `created_at=datetime.now(),` |
| 55 | `datetime.now()` | `updated_at=datetime.now(),` |
| 68 | `datetime.now()` | `created_at=datetime.now(),` |
| 69 | `datetime.now()` | `updated_at=datetime.now(),` |

### tests/integration/services/test_accounts_services.py

| Line | Code | Context |
|------|------|--------|
| 21 | `datetime.now()` | `transaction_date=datetime.now(),` |
| 22 | `datetime.now()` | `created_at=datetime.now(),` |
| 23 | `datetime.now()` | `updated_at=datetime.now(),` |
| 31 | `datetime.now()` | `transaction_date=datetime.now(),` |
| 32 | `datetime.now()` | `created_at=datetime.now(),` |
| 33 | `datetime.now()` | `updated_at=datetime.now(),` |

### tests/integration/services/test_balance_history_services.py

| Line | Code | Context |
|------|------|--------|
| 19 | `datetime.utcnow()` | `created_at=datetime.utcnow(),` |
| 20 | `datetime.utcnow()` | `updated_at=datetime.utcnow(),` |
| 53 | `datetime.utcnow()` | `datetime.utcnow() - timedelta(days=2),` |
| 54 | `datetime.utcnow()` | `datetime.utcnow() - timedelta(days=1),` |
| 55 | `datetime.utcnow()` | `datetime.utcnow(),` |
| 74 | `datetime.utcnow()` | `start_date = datetime.utcnow() - timedelta(days=2)` |
| 75 | `datetime.utcnow()` | `end_date = datetime.utcnow()` |
| 117 | `datetime.utcnow()` | `datetime.utcnow() - timedelta(days=2),` |
| 118 | `datetime.utcnow()` | `datetime.utcnow() - timedelta(days=1),` |
| 119 | `datetime.utcnow()` | `datetime.utcnow(),` |
| 154 | `datetime.utcnow()` | `start_date = datetime.utcnow() - timedelta(days=1)` |
| 155 | `datetime.utcnow()` | `end_date = datetime.utcnow()` |

### tests/integration/services/test_balance_reconciliation_services.py

| Line | Code | Context |
|------|------|--------|
| 23 | `datetime.utcnow()` | `created_at=datetime.utcnow(),` |
| 24 | `datetime.utcnow()` | `updated_at=datetime.utcnow(),` |
| 41 | `datetime.utcnow()` | `reconciliation_date=datetime.utcnow(),` |
| 42 | `datetime.utcnow()` | `created_at=datetime.utcnow(),` |
| 43 | `datetime.utcnow()` | `updated_at=datetime.utcnow(),` |

### tests/integration/services/test_categories_services.py

| Line | Code | Context |
|------|------|--------|
| 21 | `datetime.utcnow()` | `created_at=datetime.utcnow(),` |
| 22 | `datetime.utcnow()` | `updated_at=datetime.utcnow(),` |
| 36 | `datetime.utcnow()` | `created_at=datetime.utcnow(),` |
| 37 | `datetime.utcnow()` | `updated_at=datetime.utcnow(),` |

### tests/integration/services/test_cross_account_analysis_services.py

| Line | Code | Context |
|------|------|--------|
| 21 | `datetime.now()` | `created_at=datetime.now().date(),` |
| 22 | `datetime.now()` | `updated_at=datetime.now().date(),` |
| 30 | `datetime.now()` | `created_at=datetime.now().date(),` |
| 31 | `datetime.now()` | `updated_at=datetime.now().date(),` |
| 39 | `datetime.now()` | `payment_date=datetime.now().date(),` |
| 41 | `datetime.now()` | `created_at=datetime.now(),` |
| 42 | `datetime.now()` | `updated_at=datetime.now(),` |
| 51 | `datetime.now()` | `created_at=datetime.now(),` |
| 52 | `datetime.now()` | `updated_at=datetime.now(),` |
| 79 | `datetime.now()` | `created_at=datetime.now().date(),` |
| 80 | `datetime.now()` | `updated_at=datetime.now().date(),` |
| 89 | `datetime.now()` | `payment_date=datetime.now().date(),` |
| 91 | `datetime.now()` | `created_at=datetime.now(),` |
| 92 | `datetime.now()` | `updated_at=datetime.now(),` |
| 101 | `datetime.now()` | `created_at=datetime.now(),` |
| 102 | `datetime.now()` | `updated_at=datetime.now(),` |
| 126 | `datetime.now()` | `created_at=datetime.now().date(),` |
| 127 | `datetime.now()` | `updated_at=datetime.now().date(),` |
| 139 | `datetime.now()` | `transaction_date=datetime.now() - timedelta(days=i),` |
| 140 | `datetime.now()` | `created_at=datetime.now(),` |
| 141 | `datetime.now()` | `updated_at=datetime.now(),` |
| 167 | `datetime.now()` | `created_at=datetime.now().date(),` |
| 168 | `datetime.now()` | `updated_at=datetime.now().date(),` |
| 181 | `datetime.now()` | `transaction_date=datetime.now() - timedelta(days=i),` |
| 182 | `datetime.now()` | `created_at=datetime.now(),` |
| 183 | `datetime.now()` | `updated_at=datetime.now(),` |
| 209 | `datetime.now()` | `created_at=datetime.now().date(),` |
| 210 | `datetime.now()` | `updated_at=datetime.now().date(),` |
| 218 | `datetime.now()` | `created_at=datetime.now().date(),` |
| 219 | `datetime.now()` | `updated_at=datetime.now().date(),` |
| 231 | `datetime.now()` | `transaction_date=datetime.now() - timedelta(days=i),` |
| 232 | `datetime.now()` | `created_at=datetime.now(),` |
| 233 | `datetime.now()` | `updated_at=datetime.now(),` |
| 269 | `datetime.now()` | `created_at=datetime.now().date(),` |
| 270 | `datetime.now()` | `updated_at=datetime.now().date(),` |
| 281 | `datetime.now()` | `transaction_date=datetime.now(),` |
| 282 | `datetime.now()` | `created_at=datetime.now(),` |
| 283 | `datetime.now()` | `updated_at=datetime.now(),` |
| 297 | `datetime.now()` | `assert analysis.timestamp == datetime.now().date()` |

### tests/integration/services/test_deposit_schedules_services.py

| Line | Code | Context |
|------|------|--------|
| 34 | `datetime.utcnow()` | `date=datetime.utcnow(),` |
| 52 | `datetime.utcnow()` | `schedule_date=datetime.utcnow() + timedelta(days=1),` |
| 70 | `datetime.utcnow()` | `schedule_date=datetime.utcnow() + timedelta(days=1),` |
| 95 | `datetime.utcnow()` | `schedule_date=datetime.utcnow() + timedelta(days=1),` |

### tests/integration/services/test_historical_trends_services.py

| Line | Code | Context |
|------|------|--------|
| 60 | `datetime(base_date.year, 12, 20, tzinfo=ZoneInfo("UTC")` | `holiday_date = datetime(base_date.year, 12, 20, tzinfo=Zo...` |

### tests/integration/services/test_payment_patterns_services.py

| Line | Code | Context |
|------|------|--------|
| 76 | `datetime(2024, 1, 1, tzinfo=timezone.utc)` | `base_date = datetime(2024, 1, 1, tzinfo=timezone.utc)` |
| 107 | `datetime(2024, 1, 1, tzinfo=timezone.utc)` | `base_date = datetime(2024, 1, 1, tzinfo=timezone.utc)` |
| 140 | `datetime(2024, 1, 1, tzinfo=timezone.utc)` | `base_date = datetime(2024, 1, 1, tzinfo=timezone.utc)` |
| 244 | `datetime(2024, 1, 1, tzinfo=timezone.utc)` | `due_date = datetime(2024, 1, 1, tzinfo=timezone.utc)` |
| 286 | `datetime(2024, 2, 1, tzinfo=timezone.utc)` | `start_date=datetime(2024, 2, 1, tzinfo=timezone.utc),` |
| 287 | `datetime(2024, 4, 1, tzinfo=timezone.utc)` | `end_date=datetime(2024, 4, 1, tzinfo=timezone.utc),` |
| 294 | `datetime(2024, 2, 1, tzinfo=timezone.utc)` | `assert analysis.analysis_period_start >= datetime(2024, 2...` |
| 295 | `datetime(2024, 4, 1, tzinfo=timezone.utc)` | `assert analysis.analysis_period_end <= datetime(2024, 4, ...` |
| 301 | `datetime(2024, 1, 1, tzinfo=timezone.utc)` | `base_date = datetime(2024, 1, 1, tzinfo=timezone.utc)` |
| 332 | `datetime(2024, 1, 1, tzinfo=timezone.utc)` | `base_date = datetime(2024, 1, 1, tzinfo=timezone.utc)` |
| 361 | `datetime(2024, 1, 1, tzinfo=timezone.utc)` | `base_date = datetime(2024, 1, 1, tzinfo=timezone.utc)` |
| 463 | `datetime(2024, 1, 1, tzinfo=timezone.utc)` | `base_date = datetime(2024, 1, 1, tzinfo=timezone.utc)` |
| 512 | `datetime(2024, 1, 1, tzinfo=timezone.utc)` | `base_date = datetime(2024, 1, 1, tzinfo=timezone.utc)` |
| 550 | `datetime(2024, 1, 1, tzinfo=timezone.utc)` | `base_date = datetime(2024, 1, 1, tzinfo=timezone.utc)` |
| 588 | `datetime(2024, 1, 15, tzinfo=timezone.utc)` | `due_date = datetime(2024, 1, 15, tzinfo=timezone.utc)` |
| 627 | `datetime(2024, 1, 1, tzinfo=timezone.utc)` | `base_date = datetime(2024, 1, 1, tzinfo=timezone.utc)` |
| 678 | `datetime(2024, 1, 1, tzinfo=timezone.utc)` | `base_date = datetime(2024, 1, 1, tzinfo=timezone.utc)` |
| 726 | `datetime(2024, 1, 1, tzinfo=timezone.utc)` | `base_date = datetime(2024, 1, 1, tzinfo=timezone.utc)` |
| 770 | `datetime(2024, 1, 1, tzinfo=timezone.utc)` | `base_date = datetime(2024, 1, 1, tzinfo=timezone.utc)` |

### tests/integration/services/test_payment_schedules_services.py

| Line | Code | Context |
|------|------|--------|
| 20 | `datetime.utcnow()` | `created_at=datetime.utcnow(),` |
| 21 | `datetime.utcnow()` | `updated_at=datetime.utcnow(),` |
| 33 | `datetime.utcnow()` | `due_date=datetime.utcnow() + timedelta(days=7),` |
| 39 | `datetime.utcnow()` | `created_at=datetime.utcnow(),` |
| 40 | `datetime.utcnow()` | `updated_at=datetime.utcnow(),` |
| 52 | `datetime.utcnow()` | `scheduled_date=datetime.utcnow() + timedelta(days=5),` |
| 57 | `datetime.utcnow()` | `created_at=datetime.utcnow(),` |
| 58 | `datetime.utcnow()` | `updated_at=datetime.utcnow(),` |
| 70 | `datetime.utcnow()` | `scheduled_date=datetime.utcnow() + timedelta(days=5),` |
| 91 | `datetime.utcnow()` | `scheduled_date=datetime.utcnow() + timedelta(days=5),` |
| 110 | `datetime.utcnow()` | `start_date = datetime.utcnow()` |
| 111 | `datetime.utcnow()` | `end_date = datetime.utcnow() + timedelta(days=7)` |
| 143 | `datetime.utcnow()` | `test_schedule.processed_date = datetime.utcnow()` |
| 165 | `datetime.utcnow()` | `test_schedule.processed_date = datetime.utcnow()` |
| 176 | `datetime.utcnow()` | `test_schedule.scheduled_date = datetime.utcnow()` |

### tests/integration/services/test_realtime_cashflow_services.py

| Line | Code | Context |
|------|------|--------|
| 20 | `datetime.now()` | `created_at=datetime.now().date(),` |
| 21 | `datetime.now()` | `updated_at=datetime.now().date(),` |
| 29 | `datetime.now()` | `created_at=datetime.now().date(),` |
| 30 | `datetime.now()` | `updated_at=datetime.now().date(),` |
| 36 | `datetime.now()` | `created_at=datetime.now().date(),` |
| 37 | `datetime.now()` | `updated_at=datetime.now().date(),` |
| 51 | `datetime.now()` | `today = datetime.now().date()` |
| 64 | `datetime.now()` | `created_at=datetime.now(),` |
| 65 | `datetime.now()` | `updated_at=datetime.now(),` |
| 78 | `datetime.now()` | `created_at=datetime.now(),` |
| 79 | `datetime.now()` | `updated_at=datetime.now(),` |

### tests/integration/services/test_recommendations_services.py

| Line | Code | Context |
|------|------|--------|
| 85 | `datetime(
                base_date.year + year_offset, month, 15, tzinfo=ZoneInfo("UTC")` | `due_date = datetime(` |
| 89 | `datetime(
                base_date.year,
                base_date.month + month_offset,
                15,
                tzinfo=ZoneInfo("UTC")` | `due_date = datetime(` |

### tests/integration/services/test_statement_history_services.py

| Line | Code | Context |
|------|------|--------|
| 27 | `datetime(2025, 3, 15)` | `statement_date = datetime(2025, 3, 15)` |

## Recommended Fixes

Replace naive datetime usage with helpers from `tests/helpers/datetime_utils.py`:

```python
from tests.helpers.datetime_utils import utc_now, utc_datetime, days_from_now, days_ago

# Instead of: datetime.now()
# Use: utc_now()

# Instead of: datetime.utcnow()
# Use: utc_now()

# Instead of: datetime(2025, 3, 15)
# Use: utc_datetime(2025, 3, 15)

# Instead of: datetime.utcnow() + timedelta(days=15)
# Use: days_from_now(15)

# Instead of: datetime.utcnow() - timedelta(days=5)
# Use: days_ago(5)

```
