#!/usr/bin/env python3
"""
Alex Cognitive Architecture - Full Release Workflow

One command to rule them all: version bump, publish, and announce.

Usage:
    python release.py --bump patch     # Full release with patch bump
    python release.py --bump minor     # Full release with minor bump
    python release.py --skip-announce  # Skip social media announcements
    python release.py --dry-run        # Preview entire workflow
"""

import argparse
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent

def run_script(script: str, args: list[str]) -> bool:
    """Run a script and return success status."""
    cmd = [sys.executable, str(SCRIPTS_DIR / script)] + args
    print(f"\n{'=' * 60}")
    print(f"  Running: python {script} {' '.join(args)}")
    print(f"{'=' * 60}\n")

    result = subprocess.run(cmd, cwd=SCRIPTS_DIR)
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(
        description="Full release workflow for Alex Cognitive Architecture",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Full release with patch bump
    python release.py --bump patch

    # Release without announcements
    python release.py --bump minor --skip-announce

    # Preview entire workflow
    python release.py --bump patch --dry-run

Workflow:
    1. Check prerequisites
    2. Clone/update extension repo
    3. Bump version (version.py)
    4. Package & publish (publish.py --publish-only)
    5. Announce on social media (announce.py)
        """,
    )

    parser.add_argument(
        "--bump",
        choices=["major", "minor", "patch"],
        required=True,
        help="Version bump type"
    )
    parser.add_argument(
        "--skip-announce",
        action="store_true",
        help="Skip social media announcements"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without executing"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("  Alex Cognitive Architecture - Full Release")
    print("=" * 60)

    dry_run_flag = ["--dry-run"] if args.dry_run else []

    # Step 1: Check prerequisites
    print("\n📋 Step 1/5: Checking prerequisites...")
    if not run_script("publish.py", ["--check"]):
        print("\n❌ Prerequisites check failed!")
        sys.exit(1)

    # Step 2: Clone/update extension repo (package does this)
    print("\n📋 Step 2/5: Setting up extension repository...")
    if not run_script("publish.py", ["--package"] + dry_run_flag):
        print("\n❌ Repository setup failed!")
        sys.exit(1)

    # Step 3: Bump version (in the cloned repo)
    print("\n📋 Step 3/5: Bumping version...")
    if not run_script("version.py", ["--bump", args.bump, "--auto-push"] + dry_run_flag):
        print("\n❌ Version bump failed!")
        sys.exit(1)

    # Step 4: Re-package and publish (with new version)
    print("\n📋 Step 4/5: Publishing extension...")
    if not run_script("publish.py", ["--publish"] + dry_run_flag):
        print("\n❌ Publishing failed!")
        sys.exit(1)

    # Step 5: Announce (optional)
    if not args.skip_announce:
        print("\n📋 Step 5/5: Announcing release...")
        if args.dry_run:
            run_script("announce.py", ["--platform", "all", "--dry-run"])
        else:
            response = input("\n  Post announcements to social media? [y/N]: ")
            if response.lower() == "y":
                # Post to primary channels first
                run_script("announce.py", ["--platform", "reddit", "--subreddit", "vscode"])
                run_script("announce.py", ["--platform", "twitter"])
                run_script("announce.py", ["--platform", "devto"])

                print("\n  ✅ Primary announcements posted!")
                print("  💡 Post to secondary channels tomorrow:")
                print("     python announce.py --platform reddit --subreddit github")
                print("     python announce.py --platform discord")
                print("     python announce.py --platform linkedin")
            else:
                print("\n  ⏭️  Skipped announcements")
                print("     Run manually: python announce.py --platform all")
    else:
        print("\n📋 Step 5/5: Skipping announcements (--skip-announce)")

    # Summary
    print("\n" + "=" * 60)
    if args.dry_run:
        print("  ⚠️  DRY RUN COMPLETE - No changes were made")
    else:
        print("  ✅ RELEASE COMPLETE!")
        print("\n  Verify at:")
        print("  🔗 https://marketplace.visualstudio.com/items?itemName=fabioc-aloha.alex-cognitive-architecture")
    print("=" * 60)


if __name__ == "__main__":
    main()

