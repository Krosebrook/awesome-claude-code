# Audit System Documentation

The audit system provides both high-level and scoped auditing capabilities for the Awesome Claude Code repository.

## Overview

The audit system helps you:
- Get a high-level overview of repository health and statistics
- Perform scoped audits on specific categories, authors, or criteria
- Identify inactive resources, missing licenses, and other issues
- Track freshness of resource validations

## Usage

### High-Level Audit

Get a comprehensive overview of the entire repository:

```bash
# Using the script directly
python scripts/audit.py

# Using make
make audit
```

**Output includes:**
- Total resources count
- Active vs inactive breakdown
- Category distribution
- Sub-category distribution  
- License statistics
- Top authors
- Freshness metrics (recently added, checked, outdated)
- Issues (removed from origin, etc.)

### Scoped Audits

Perform targeted audits with filters:

#### Filter by Category

```bash
# Using the script
python scripts/audit.py --category "Agent Skills"

# Using make
make audit-scoped CATEGORY="Agent Skills"
```

#### Filter by Sub-Category

```bash
python scripts/audit.py --sub-category "General"
make audit-scoped SUB_CATEGORY="General"
```

#### Filter by Author

```bash
python scripts/audit.py --author "username"
make audit-scoped AUTHOR="username"
```

#### Filter by License

```bash
python scripts/audit.py --license "MIT"
make audit-scoped LICENSE="MIT"
```

#### Show Only Inactive Resources

```bash
python scripts/audit.py --inactive
make audit-scoped INACTIVE=1
```

#### Show Resources Without License

```bash
python scripts/audit.py --no-license
make audit-scoped NO_LICENSE=1
```

#### Show Recently Added Resources

```bash
# Show resources added in last 30 days
python scripts/audit.py --recent-days 30
make audit-scoped RECENT_DAYS=30
```

### Combined Filters

You can combine multiple filters:

```bash
# Inactive resources in a specific category
python scripts/audit.py --category "Slash-Commands" --inactive
make audit-scoped CATEGORY="Slash-Commands" INACTIVE=1

# Resources by specific author without license
python scripts/audit.py --author "username" --no-license
make audit-scoped AUTHOR="username" NO_LICENSE=1

# Recently added resources in a category
python scripts/audit.py --category "Tooling" --recent-days 7
make audit-scoped CATEGORY="Tooling" RECENT_DAYS=7
```

### JSON Output

For programmatic use, output results in JSON format:

```bash
python scripts/audit.py --json
python scripts/audit.py --category "Agent Skills" --json
```

## Use Cases

### Maintenance Tasks

1. **Find broken links:**
   ```bash
   make audit-scoped INACTIVE=1
   ```

2. **Find resources needing license info:**
   ```bash
   make audit-scoped NO_LICENSE=1
   ```

3. **Check author's contributions:**
   ```bash
   make audit-scoped AUTHOR="username"
   ```

### Quality Assurance

1. **Category health check:**
   ```bash
   make audit-scoped CATEGORY="Slash-Commands"
   ```

2. **Recent additions review:**
   ```bash
   make audit-scoped RECENT_DAYS=7
   ```

### Reporting

1. **Generate JSON reports:**
   ```bash
   python scripts/audit.py --json > audit-report.json
   ```

2. **Weekly health check:**
   ```bash
   make audit
   make audit-scoped RECENT_DAYS=7
   make audit-scoped INACTIVE=1
   ```
