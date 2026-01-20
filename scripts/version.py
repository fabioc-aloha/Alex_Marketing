#!/usr/bin/env python3
"""
Alex Cognitive Architecture - Version Bump Script

Bumps the version in the extension repo and creates a release.

Usage:
    python version.py --bump patch    # 2.0.0 -> 2.0.1
    python version.py --bump minor    # 2.0.0 -> 2.1.0
    python version.py --bump major    # 2.0.0 -> 3.0.0
    python version.py --set 2.1.0     # Set specific version
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    print("Missing python-dotenv. Run: pip install python-dotenv")
    sys.exit(1)

load_dotenv(Path(__file__).parent / ".env")

EXTENSION_DIR = Path(__file__).parent.parent / "extension-build"

# =============================================================================
# VERSION HELPERS
# =============================================================================

def parse_version(version: str) -> tuple[int, int, int]:
    """Parse version string into tuple."""
    match = re.match(r"(\d+)\.(\d+)\.(\d+)", version)
    if not match:
        raise ValueError(f"Invalid version: {version}")
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def bump_version(current: str, bump_type: str) -> str:
    """Bump version according to type."""
    major, minor, patch = parse_version(current)
    
    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    elif bump_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")


def version_to_name(version: str) -> str:
    """Convert version to IUPAC-style name (e.g., 2.0.0 -> BINILNILIUM)."""
    names = {
        "0": "NIL", "1": "UN", "2": "BI", "3": "TRI", "4": "QUAD",
        "5": "PENT", "6": "HEX", "7": "SEPT", "8": "OCT", "9": "ENN"
    }
    parts = version.replace(".", "")
    name = "".join(names.get(d, d) for d in parts)
    return f"{name}IUM"


# =============================================================================
# FILE UPDATES
# =============================================================================

def update_package_json(extension_dir: Path, new_version: str, dry_run: bool = False) -> str:
    """Update version in package.json. Returns old version."""
    package_json = extension_dir / "package.json"
    
    with open(package_json) as f:
        data = json.load(f)
    
    old_version = data.get("version", "0.0.0")
    
    if dry_run:
        print(f"  [DRY RUN] Would update package.json: {old_version} -> {new_version}")
        return old_version
    
    data["version"] = new_version
    
    with open(package_json, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    
    print(f"  ✅ Updated package.json: {old_version} -> {new_version}")
    return old_version


def update_changelog(extension_dir: Path, new_version: str, dry_run: bool = False) -> None:
    """Add new version entry to CHANGELOG.md."""
    changelog = extension_dir / "CHANGELOG.md"
    today = datetime.now().strftime("%Y-%m-%d")
    
    new_entry = f"""## [{new_version}] - {today}

### Added

- 

### Changed

- 

### Fixed

- 

"""
    
    if dry_run:
        print(f"  [DRY RUN] Would add CHANGELOG entry for {new_version}")
        return
    
    content = changelog.read_text()
    
    # Insert after the first heading
    insert_pos = content.find("\n## ")
    if insert_pos == -1:
        insert_pos = content.find("\n")
    
    new_content = content[:insert_pos + 1] + new_entry + content[insert_pos + 1:]
    changelog.write_text(new_content)
    
    print(f"  ✅ Added CHANGELOG entry for {new_version}")


def update_copilot_instructions(extension_dir: Path, new_version: str, dry_run: bool = False) -> None:
    """Update version in copilot-instructions.md."""
    instructions = extension_dir / ".github" / "copilot-instructions.md"
    
    if not instructions.exists():
        print(f"  ⚠️  copilot-instructions.md not found, skipping")
        return
    
    version_name = version_to_name(new_version)
    
    if dry_run:
        print(f"  [DRY RUN] Would update copilot-instructions.md: {new_version} {version_name}")
        return
    
    content = instructions.read_text()
    
    # Update version line
    content = re.sub(
        r"\*\*Version\*\*: [\d.]+ [A-Z]+",
        f"**Version**: {new_version} {version_name}",
        content
    )
    
    instructions.write_text(content)
    print(f"  ✅ Updated copilot-instructions.md: {new_version} {version_name}")


# =============================================================================
# GIT OPERATIONS
# =============================================================================

def git_commit_and_tag(extension_dir: Path, new_version: str, dry_run: bool = False) -> None:
    """Commit changes and create a git tag."""
    
    if dry_run:
        print(f"  [DRY RUN] Would commit and tag v{new_version}")
        return
    
    # Stage changes
    subprocess.run(["git", "add", "-A"], cwd=extension_dir, check=True)
    
    # Commit
    subprocess.run(
        ["git", "commit", "-m", f"chore: bump version to {new_version}"],
        cwd=extension_dir,
        check=True
    )
    
    # Tag
    subprocess.run(
        ["git", "tag", "-a", f"v{new_version}", "-m", f"Release v{new_version}"],
        cwd=extension_dir,
        check=True
    )
    
    print(f"  ✅ Created commit and tag v{new_version}")


def git_push(extension_dir: Path, dry_run: bool = False) -> None:
    """Push commits and tags."""
    
    if dry_run:
        print(f"  [DRY RUN] Would push to origin with tags")
        return
    
    subprocess.run(["git", "push"], cwd=extension_dir, check=True)
    subprocess.run(["git", "push", "--tags"], cwd=extension_dir, check=True)
    
    print(f"  ✅ Pushed to origin with tags")


# =============================================================================
# MAIN WORKFLOW
# =============================================================================

def workflow_bump(bump_type: str = None, set_version: str = None, dry_run: bool = False) -> str:
    """Bump version and prepare release."""
    
    print("\n📦 Version Bump Workflow\n")
    
    # Check extension repo exists
    if not EXTENSION_DIR.exists():
        print(f"  ❌ Extension repo not found at {EXTENSION_DIR}")
        print(f"     Run: python publish.py --package first")
        sys.exit(1)
    
    # Get current version
    package_json = EXTENSION_DIR / "package.json"
    with open(package_json) as f:
        current_version = json.load(f).get("version", "0.0.0")
    
    # Determine new version
    if set_version:
        new_version = set_version
    elif bump_type:
        new_version = bump_version(current_version, bump_type)
    else:
        raise ValueError("Must specify --bump or --set")
    
    version_name = version_to_name(new_version)
    
    print(f"  📌 Current version: {current_version}")
    print(f"  📌 New version: {new_version} ({version_name})")
    print()
    
    # Update files
    update_package_json(EXTENSION_DIR, new_version, dry_run)
    update_changelog(EXTENSION_DIR, new_version, dry_run)
    update_copilot_instructions(EXTENSION_DIR, new_version, dry_run)
    
    # Git operations
    print()
    git_commit_and_tag(EXTENSION_DIR, new_version, dry_run)
    
    # Ask before pushing
    if not dry_run:
        response = input("\n  Push to origin? [y/N]: ")
        if response.lower() == "y":
            git_push(EXTENSION_DIR, dry_run)
        else:
            print("  ⏭️  Skipped push. Run manually: git push && git push --tags")
    
    return new_version


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Bump version for Alex Cognitive Architecture",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Bump patch version (2.0.0 -> 2.0.1)
    python version.py --bump patch

    # Bump minor version (2.0.0 -> 2.1.0)
    python version.py --bump minor

    # Bump major version (2.0.0 -> 3.0.0)
    python version.py --bump major

    # Set specific version
    python version.py --set 2.1.0

    # Preview without changes
    python version.py --bump patch --dry-run
        """,
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--bump", choices=["major", "minor", "patch"], help="Bump type")
    group.add_argument("--set", dest="set_version", type=str, help="Set specific version")
    
    parser.add_argument("--dry-run", action="store_true", help="Preview without executing")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("  Alex Cognitive Architecture - Version Manager")
    print("=" * 60)
    
    new_version = workflow_bump(args.bump, args.set_version, args.dry_run)
    
    if args.dry_run:
        print("\n⚠️  This was a dry run. No changes were made.")
    else:
        print(f"\n✅ Version bumped to {new_version}")
        print(f"\n  Next steps:")
        print(f"  1. Edit CHANGELOG.md with release notes")
        print(f"  2. Run: python publish.py --publish")
        print(f"  3. Run: python announce.py --platform all")


if __name__ == "__main__":
    main()
