#!/usr/bin/env python3
"""
Audit script for the Awesome Claude Code repository.

This script provides both high-level and scoped auditing capabilities:
- High-level: Repository-wide statistics and health checks
- Scoped: Detailed audits for specific categories, resources, or criteria

Usage:
    # High-level audit (default)
    python scripts/audit.py

    # Scoped audits
    python scripts/audit.py --category "Agent Skills"
    python scripts/audit.py --sub-category "General"
    python scripts/audit.py --author "username"
    python scripts/audit.py --license MIT
    python scripts/audit.py --inactive
    python scripts/audit.py --no-license
    python scripts/audit.py --recent-days 30

    # Combined scopes
    python scripts/audit.py --category "Tooling" --inactive
"""

import argparse
import csv
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# File paths
CSV_FILE = "THE_RESOURCES_TABLE.csv"


class AuditReport:
    """Container for audit results."""

    def __init__(self):
        self.high_level: dict[str, Any] = {}
        self.scoped: dict[str, Any] = {}
        self.warnings: list[str] = []
        self.errors: list[str] = []


def load_resources() -> tuple[list[dict[str, str]], list[str]]:
    """Load resources from CSV file."""
    csv_path = Path(CSV_FILE)
    if not csv_path.exists():
        print(f"Error: {CSV_FILE} not found")
        sys.exit(1)

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = list(reader.fieldnames) if reader.fieldnames else []

    return rows, fieldnames


def parse_date(date_str: str) -> datetime | None:
    """Parse date string in format YYYY-MM-DD:HH-MM-SS."""
    if not date_str or date_str.strip() == "":
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d:%H-%M-%S")
    except ValueError:
        return None


def high_level_audit(resources: list[dict[str, str]]) -> dict[str, Any]:
    """Perform high-level audit of all resources."""
    total = len(resources)
    active = sum(1 for r in resources if r.get("Active", "").upper() == "TRUE")
    inactive = total - active

    # Category breakdown
    categories = Counter(r.get("Category", "Unknown") for r in resources)
    sub_categories = Counter(r.get("Sub-Category", "Unknown") for r in resources)

    # License breakdown
    licenses = Counter(r.get("License", "Unknown") for r in resources)
    no_license = sum(
        1 for r in resources if not r.get("License") or r.get("License") == "NOT_FOUND"
    )

    # Author breakdown
    authors = Counter(r.get("Author Name", "Unknown") for r in resources)
    unique_authors = len([a for a in authors if a != "Unknown"])

    # Date analysis
    now = datetime.now()
    recently_added = []
    recently_checked = []
    never_checked = []
    outdated = []  # Not checked in 30+ days

    for resource in resources:
        date_added = parse_date(resource.get("Date Added", ""))
        if date_added and (now - date_added).days <= 30:
            recently_added.append(resource)

        last_checked = parse_date(resource.get("Last Checked", ""))
        if not last_checked:
            never_checked.append(resource)
        elif (now - last_checked).days <= 7:
            recently_checked.append(resource)
        elif (now - last_checked).days > 30:
            outdated.append(resource)

    # Links with issues
    removed_from_origin = sum(
        1 for r in resources if r.get("Removed From Origin", "").upper() == "TRUE"
    )

    return {
        "total_resources": total,
        "active": active,
        "inactive": inactive,
        "categories": dict(categories.most_common()),
        "sub_categories": dict(sub_categories.most_common()),
        "licenses": dict(licenses.most_common()),
        "no_license": no_license,
        "unique_authors": unique_authors,
        "top_authors": dict(authors.most_common(10)),
        "recently_added": len(recently_added),
        "recently_checked": len(recently_checked),
        "never_checked": len(never_checked),
        "outdated_checks": len(outdated),
        "removed_from_origin": removed_from_origin,
    }


def scoped_audit(
    resources: list[dict[str, str]],
    category: str | None = None,
    sub_category: str | None = None,
    author: str | None = None,
    license_filter: str | None = None,
    inactive_only: bool = False,
    no_license_only: bool = False,
    recent_days: int | None = None,
) -> dict[str, Any]:
    """Perform scoped audit based on filters."""
    filtered = resources

    # Apply filters
    if category:
        filtered = [r for r in filtered if r.get("Category", "").lower() == category.lower()]

    if sub_category:
        filtered = [
            r for r in filtered if r.get("Sub-Category", "").lower() == sub_category.lower()
        ]

    if author:
        filtered = [r for r in filtered if r.get("Author Name", "").lower() == author.lower()]

    if license_filter:
        filtered = [
            r for r in filtered if r.get("License", "").lower() == license_filter.lower()
        ]

    if inactive_only:
        filtered = [r for r in filtered if r.get("Active", "").upper() != "TRUE"]

    if no_license_only:
        filtered = [
            r
            for r in filtered
            if not r.get("License") or r.get("License") == "NOT_FOUND"
        ]

    if recent_days is not None:
        cutoff_date = datetime.now() - timedelta(days=recent_days)
        filtered = [
            r
            for r in filtered
            if parse_date(r.get("Date Added", ""))
            and parse_date(r.get("Date Added", "")) >= cutoff_date
        ]

    # Analyze filtered resources
    result = {
        "filter_criteria": {
            "category": category,
            "sub_category": sub_category,
            "author": author,
            "license": license_filter,
            "inactive_only": inactive_only,
            "no_license_only": no_license_only,
            "recent_days": recent_days,
        },
        "matched_count": len(filtered),
        "resources": [],
    }

    # Add detailed info for each matched resource
    for resource in filtered:
        last_checked = parse_date(resource.get("Last Checked", ""))
        days_since_check = (
            (datetime.now() - last_checked).days if last_checked else None
        )

        result["resources"].append(
            {
                "id": resource.get("ID", ""),
                "name": resource.get("Display Name", ""),
                "category": resource.get("Category", ""),
                "sub_category": resource.get("Sub-Category", ""),
                "active": resource.get("Active", ""),
                "license": resource.get("License", ""),
                "author": resource.get("Author Name", ""),
                "primary_link": resource.get("Primary Link", ""),
                "last_checked": resource.get("Last Checked", ""),
                "days_since_check": days_since_check,
                "removed_from_origin": resource.get("Removed From Origin", ""),
            }
        )

    return result


def print_high_level_report(audit_data: dict[str, Any]) -> None:
    """Print high-level audit report."""
    print("\n" + "=" * 80)
    print("HIGH-LEVEL AUDIT REPORT")
    print("=" * 80)

    print(f"\n📊 OVERVIEW")
    print(f"  Total Resources: {audit_data['total_resources']}")
    print(f"  Active: {audit_data['active']} ({audit_data['active']/audit_data['total_resources']*100:.1f}%)")
    print(f"  Inactive: {audit_data['inactive']} ({audit_data['inactive']/audit_data['total_resources']*100:.1f}%)")
    print(f"  Unique Authors: {audit_data['unique_authors']}")

    print(f"\n📁 CATEGORIES ({len(audit_data['categories'])} total)")
    for cat, count in audit_data["categories"].items():
        print(f"  {cat}: {count}")

    print(f"\n📂 SUB-CATEGORIES ({len(audit_data['sub_categories'])} total)")
    for subcat, count in list(audit_data["sub_categories"].items())[:10]:
        print(f"  {subcat}: {count}")
    if len(audit_data["sub_categories"]) > 10:
        print(f"  ... and {len(audit_data['sub_categories']) - 10} more")

    print(f"\n⚖️  LICENSES")
    print(f"  Resources without license: {audit_data['no_license']}")
    print(f"  Top licenses:")
    for lic, count in list(audit_data["licenses"].items())[:10]:
        if lic not in ["NOT_FOUND", "Unknown", ""]:
            print(f"    {lic}: {count}")

    print(f"\n👥 TOP AUTHORS")
    for author, count in list(audit_data["top_authors"].items())[:10]:
        if author != "Unknown":
            print(f"  {author}: {count} resources")

    print(f"\n📅 FRESHNESS")
    print(f"  Recently added (last 30 days): {audit_data['recently_added']}")
    print(f"  Recently checked (last 7 days): {audit_data['recently_checked']}")
    print(f"  Never checked: {audit_data['never_checked']}")
    print(f"  Outdated checks (>30 days): {audit_data['outdated_checks']}")

    print(f"\n⚠️  ISSUES")
    print(f"  Removed from origin: {audit_data['removed_from_origin']}")

    print("\n" + "=" * 80 + "\n")


def print_scoped_report(scoped_data: dict[str, Any]) -> None:
    """Print scoped audit report."""
    print("\n" + "=" * 80)
    print("SCOPED AUDIT REPORT")
    print("=" * 80)

    print(f"\n🔍 FILTER CRITERIA:")
    criteria = scoped_data["filter_criteria"]
    active_filters = []
    for key, value in criteria.items():
        if value is not None and value is not False:
            active_filters.append(f"  {key.replace('_', ' ').title()}: {value}")

    if active_filters:
        print("\n".join(active_filters))
    else:
        print("  No filters applied")

    print(f"\n📊 MATCHED: {scoped_data['matched_count']} resources")

    if scoped_data["matched_count"] > 0:
        print(f"\n📋 RESOURCES:")
        for i, resource in enumerate(scoped_data["resources"], 1):
            status = "✓" if resource["active"] == "TRUE" else "✗"
            days = (
                f"({resource['days_since_check']}d ago)"
                if resource["days_since_check"] is not None
                else "(never checked)"
            )

            print(f"\n  {i}. {status} {resource['name']}")
            print(f"     Category: {resource['category']} / {resource['sub_category']}")
            print(f"     Author: {resource['author']}")
            print(f"     License: {resource['license']}")
            print(f"     Link: {resource['primary_link']}")
            print(f"     Last Checked: {resource['last_checked']} {days}")
            if resource["removed_from_origin"] == "TRUE":
                print(f"     ⚠️  REMOVED FROM ORIGIN")

    print("\n" + "=" * 80 + "\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Audit the Awesome Claude Code repository",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # High-level audit
  python scripts/audit.py

  # Scoped audits
  python scripts/audit.py --category "Agent Skills"
  python scripts/audit.py --sub-category "General"
  python scripts/audit.py --author "username"
  python scripts/audit.py --license MIT
  python scripts/audit.py --inactive
  python scripts/audit.py --no-license
  python scripts/audit.py --recent-days 30

  # Combined scopes
  python scripts/audit.py --category "Tooling" --inactive
        """,
    )

    # Scoped filters
    parser.add_argument("--category", help="Filter by category")
    parser.add_argument("--sub-category", help="Filter by sub-category")
    parser.add_argument("--author", help="Filter by author name")
    parser.add_argument("--license", dest="license_filter", help="Filter by license")
    parser.add_argument(
        "--inactive", action="store_true", help="Show only inactive resources"
    )
    parser.add_argument(
        "--no-license", action="store_true", help="Show resources without license"
    )
    parser.add_argument(
        "--recent-days", type=int, help="Show resources added in last N days"
    )

    # Output options
    parser.add_argument(
        "--json", action="store_true", help="Output in JSON format"
    )

    args = parser.parse_args()

    # Load resources
    resources, _ = load_resources()

    # Check if any scoped filters are applied
    has_scoped_filters = any(
        [
            args.category,
            args.sub_category,
            args.author,
            args.license_filter,
            args.inactive,
            args.no_license,
            args.recent_days,
        ]
    )

    if has_scoped_filters:
        # Perform scoped audit
        scoped_data = scoped_audit(
            resources,
            category=args.category,
            sub_category=args.sub_category,
            author=args.author,
            license_filter=args.license_filter,
            inactive_only=args.inactive,
            no_license_only=args.no_license,
            recent_days=args.recent_days,
        )

        if args.json:
            import json

            print(json.dumps(scoped_data, indent=2))
        else:
            print_scoped_report(scoped_data)
    else:
        # Perform high-level audit
        high_level_data = high_level_audit(resources)

        if args.json:
            import json

            print(json.dumps(high_level_data, indent=2))
        else:
            print_high_level_report(high_level_data)


if __name__ == "__main__":
    main()
