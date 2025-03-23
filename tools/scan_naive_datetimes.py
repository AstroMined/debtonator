#!/usr/bin/env python
"""
Scan for naive datetime usage in Python files.

This script scans Python files for naive datetime usage patterns
that violate ADR-011 requirements, generating a comprehensive report.
"""

import os
import re
import sys
from pathlib import Path


def check_file(filepath):
    """Check a single file for naive datetime usage."""
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            content = f.read()
        except UnicodeDecodeError:
            print(f"Warning: Could not read {filepath} - not a text file")
            return []

    naive_patterns = [
        # Simple patterns without lookbehinds
        r"datetime\.now\(\)",
        r"datetime\.utcnow\(\)",
        r"datetime\([^)]*\)(?![^.;,:)]*tzinfo)",  # Still use lookahead to check for tzinfo
    ]

    # Patterns to ignore (e.g., in comments, strings, helper functions)
    ignore_contexts = [
        # Documentation
        r'"""[^"]*naive datetime[^"]*"""',
        r"'''[^']*naive datetime[^']*'''",
        r"#.*naive datetime",
        # Test functions about naive datetimes
        r"def.*test_.*naive.*datetime",
        # Import statements
        r"from datetime import datetime",
        # Helper functions
        r"utc_datetime",
        r"ensure_utc",
        r"naive_utc_now",
        # Inside validators that check for naive datetimes
        r"tzinfo is None",
        r"value.tzinfo",
    ]

    issues = []
    for pattern in naive_patterns:
        matches = re.finditer(pattern, content)
        for match in matches:
            match_start = match.start()
            line_num = content[:match_start].count("\n") + 1

            # Get context around the match
            line_start = content.rfind("\n", 0, match_start) + 1
            line_end = content.find("\n", match_start)
            if line_end == -1:  # Handle last line
                line_end = len(content)

            line_context = content[line_start:line_end].strip()

            # Check if this is part of a helper function or otherwise excluded
            # Get text before the match to check for prefixes
            prefix_end = match_start
            prefix_start = max(0, prefix_end - 20)  # Look back 20 chars
            prefix_text = content[prefix_start:prefix_end]

            # Skip if it's part of a helper function
            if any(
                helper in prefix_text
                for helper in ["utc_datetime", "ensure_utc", "naive_utc_now"]
            ):
                continue

            # Skip if it's part of a word (not standalone 'datetime')
            if prefix_text and prefix_text[-1].isalnum() and prefix_text[-1] != " ":
                continue

            # Get a wider context window for other checks
            context_start = max(0, match_start - 200)
            context_end = min(len(content), match_start + len(match.group()) + 200)
            context = content[context_start:context_end]

            # Check if in ignorable context (comments, etc.)
            if any(
                re.search(ignore_pattern, context) for ignore_pattern in ignore_contexts
            ):
                continue

            # Check if it's part of a function definition or inside a docstring
            lines_before = content[:match_start].split("\n")
            if lines_before:
                last_line = lines_before[-1].strip()
                # Skip if part of a function definition
                if "def " in last_line and "(" in last_line:
                    continue

                # Skip if in an import statement
                if "import" in last_line or "from" in last_line:
                    continue

                # Check for open docstrings
                triple_quotes = lines_before[-1].count('"""') + sum(
                    line.count('"""')
                    for line in lines_before[-5:]
                    if len(lines_before) >= 5
                )
                single_triple_quotes = lines_before[-1].count("'''") + sum(
                    line.count("'''")
                    for line in lines_before[-5:]
                    if len(lines_before) >= 5
                )
                if triple_quotes % 2 == 1 or single_triple_quotes % 2 == 1:
                    continue

            issues.append(
                {
                    "file": str(filepath),
                    "line": line_num,
                    "code": match.group(),
                    "context": line_context,
                }
            )

    return issues


def scan_directory(directory, pattern="*.py"):
    """Recursively scan a directory for Python files with naive datetime usage."""
    issues = []

    for path in Path(directory).rglob(pattern):
        if path.is_file():
            file_issues = check_file(path)
            if file_issues:
                print(f"Found {len(file_issues)} issues in {path}")
                issues.extend(file_issues)

    return issues


def generate_report(issues, output_file="naive_datetime_report.md"):
    """Generate a markdown report of naive datetime usage."""
    with open(output_file, "w") as f:
        f.write("# Naive Datetime Usage Report\n\n")
        f.write("## Summary\n\n")
        f.write(f"Found {len(issues)} instances of naive datetime usage.\n\n")

        # Group by file
        files = {}
        for issue in issues:
            filepath = issue["file"]
            if filepath not in files:
                files[filepath] = []
            files[filepath].append(issue)

        # Write file details
        f.write("## Details by File\n\n")
        for filepath, file_issues in sorted(files.items()):
            relative_path = os.path.relpath(filepath)
            f.write(f"### {relative_path}\n\n")
            f.write("| Line | Code | Context |\n")
            f.write("|------|------|--------|\n")
            for issue in sorted(file_issues, key=lambda x: x["line"]):
                context = issue["context"]
                if len(context) > 60:
                    context = context[:57] + "..."
                f.write(f"| {issue['line']} | `{issue['code']}` | `{context}` |\n")
            f.write("\n")

        # Write example fixes
        f.write("## Recommended Fixes\n\n")
        f.write(
            "Replace naive datetime usage with helpers from `tests/helpers/datetime_utils.py`:\n\n"
        )
        f.write("```python\n")
        f.write(
            "from tests.helpers.datetime_utils import utc_now, utc_datetime, days_from_now, days_ago\n\n"
        )

        # Generate specific examples based on actual findings
        patterns_found = set()
        contexts_found = set()

        for issue in issues:
            if "datetime.now()" in issue["code"]:
                patterns_found.add("datetime.now()")
            elif "datetime.utcnow()" in issue["code"]:
                patterns_found.add("datetime.utcnow()")
            elif re.match(r"datetime\([^)]*\)", issue["code"]):
                patterns_found.add("datetime_constructor")

            if "timedelta" in issue["context"]:
                contexts_found.add("timedelta")

        if "datetime.now()" in patterns_found:
            f.write("# Instead of: datetime.now()\n")
            f.write("# Use: utc_now()\n\n")

        if "datetime.utcnow()" in patterns_found:
            f.write("# Instead of: datetime.utcnow()\n")
            f.write("# Use: utc_now()\n\n")

        if "datetime_constructor" in patterns_found:
            f.write("# Instead of: datetime(2025, 3, 15)\n")
            f.write("# Use: utc_datetime(2025, 3, 15)\n\n")

        if "timedelta" in contexts_found:
            f.write("# Instead of: datetime.utcnow() + timedelta(days=15)\n")
            f.write("# Use: days_from_now(15)\n\n")

            f.write("# Instead of: datetime.utcnow() - timedelta(days=5)\n")
            f.write("# Use: days_ago(5)\n\n")

        # Default examples if nothing specific was found
        if not patterns_found and not contexts_found:
            f.write("# Instead of: datetime.now()\n")
            f.write("# Use: utc_now()\n\n")
            f.write("# Instead of: datetime.utcnow()\n")
            f.write("# Use: utc_now()\n\n")
            f.write("# Instead of: datetime(2025, 3, 15)\n")
            f.write("# Use: utc_datetime(2025, 3, 15)\n\n")
            f.write("# Instead of: datetime.utcnow() + timedelta(days=15)\n")
            f.write("# Use: days_from_now(15)\n")

        f.write("```\n")


if __name__ == "__main__":
    # Default directories to scan
    directories = ["tests"]
    if len(sys.argv) > 1:
        # Allow specifying directories via command line
        directories = sys.argv[1:]

    all_issues = []
    for directory in directories:
        print(f"Scanning {directory}...")
        issues = scan_directory(directory)
        all_issues.extend(issues)
        print(f"Found {len(issues)} issues in {directory}")

    if all_issues:
        generate_report(all_issues)
        print(f"\nTotal: {len(all_issues)} naive datetime issues found")
        print(f"Report generated: naive_datetime_report.md")
    else:
        print("\nNo naive datetime issues found!")
