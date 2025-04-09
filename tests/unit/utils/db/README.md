# Database Utilities Testing

## Integration Test Candidates

The `handle_db_error` function in `db.py` requires integration tests rather than unit tests because:

1. It interacts with SQLAlchemy's `IntegrityError` which is difficult to mock accurately
2. It crosses layers between database and HTTP concerns
3. It raises HTTP exceptions based on database error content

## Testing Philosophy

This function should be tested with integration tests that:

- Use a real (test) database
- Trigger actual integrity errors (e.g., unique constraint violations)
- Verify the correct HTTP exceptions are raised

## Current Coverage

Current coverage for `src/utils/db.py` is 38%, with the following lines missing:

```
7-12
```

These lines correspond to the error handling logic that requires integration tests.

## Refactoring Recommendation

As noted in the module's docstring, this function crosses layers between database and HTTP concerns. It would be more appropriate to move this functionality to `src/errors/` to maintain proper separation of concerns.

After refactoring, unit tests could be written for the error mapping logic, while integration tests would still be needed for the database interaction aspects.
