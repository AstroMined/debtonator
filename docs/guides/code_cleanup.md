# Code Cleanup Guide for Debtonator

This guide explains how to use code cleanup tools configured for the Debtonator project to maintain consistent code quality.

## Tools Overview

The project uses three primary code cleanup tools:

1. **autoflake** - Removes unused imports and unused variables
2. **isort** - Sorts and organizes imports
3. **black** - Formats code according to PEP 8 style guide

## Installation

All development tools are configured in `pyproject.toml` and can be installed with:

```bash
# Install all development tools
uv pip install -e ".[dev]"
```

## Using Autoflake

Autoflake is configured to focus on removing unused imports while preserving unused variables (especially important in test files).

### Check Mode (Safe - No Changes)

Before making changes, you can see what autoflake would do:

```bash
# Check what unused imports would be removed (verbose output)
autoflake --remove-all-unused-imports --recursive src/ --check --verbose

# Check both src and tests directories
autoflake --remove-all-unused-imports --recursive src/ tests/ --check --verbose
```

### Making Actual Changes

When you're ready to apply the changes:

```bash
# Remove unused imports from source code
autoflake --remove-all-unused-imports --recursive src/ --in-place

# Remove unused imports from tests
autoflake --remove-all-unused-imports --recursive tests/ --in-place
```

## Using isort

isort is used to organize and sort imports according to PEP 8:

```bash
# Check what would be changed
isort --check-only --diff src/ tests/

# Apply the changes
isort src/ tests/
```

## Using black

black enforces a consistent code style:

```bash
# Check what would be formatted
black --check src/ tests/

# Format the code
black src/ tests/
```

## Complete Cleanup Workflow

For a complete code cleanup process, run the following:

```bash
# Full cleanup pipeline
autoflake --remove-all-unused-imports --recursive src/ tests/ --in-place && \
isort src/ tests/ && \
black src/ tests/
```

## Specific Cleanup Tasks

### Focusing on One Directory

```bash
# Clean up a specific module
autoflake --remove-all-unused-imports --recursive src/repositories/ --in-place && \
isort src/repositories/ && \
black src/repositories/
```

### Targeting Specific Files

```bash
# Clean up a specific file
autoflake --remove-all-unused-imports src/models/accounts.py --in-place && \
isort src/models/accounts.py && \
black src/models/accounts.py
```

## Configuration

All tools are configured in `pyproject.toml`:

- **autoflake**: Configured to remove unused imports while preserving unused variables
- **isort**: (Add your existing isort configuration here)
- **black**: (Add your existing black configuration here)

## Notes on Unused Variables

The autoflake configuration specifically avoids removing unused variables (`remove-unused-variables = false`) as they may be legitimately needed in test files for error handling patterns. If you want to handle unused variables:

1. Use the underscore convention for intentionally unused variables:

   ```python
   # Before
   result = function_that_returns_unneeded_value()
   
   # After
   _ = function_that_returns_unneeded_value()
   ```

2. Use pytest's explicit assertion patterns:

   ```python
   # Before
   try:
       result = function_that_should_raise_error()
       assert False, "Expected exception wasn't raised"
   except ExpectedException:
       assert True
       
   # After
   with pytest.raises(ExpectedException):
       function_that_should_raise_error()
   ```
