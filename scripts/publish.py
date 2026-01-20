#!/usr/bin/env python3
"""
Alex Cognitive Architecture - Extension Publishing Script

Automates packaging and publishing the VS Code extension from the marketing repo.
Clones/updates the extension repo, builds, packages, publishes, and creates GitHub releases.

Requirements:
    - Node.js and npm installed
    - vsce installed globally (npm install -g @vscode/vsce)
    - Git installed
    - GitHub CLI (gh) installed
    - PAT stored in .env file

Usage:
    python publish.py --check          # Verify prerequisites
    python publish.py --package        # Package only (creates .vsix)
    python publish.py --publish        # Package, publish, and create GitHub release
    python publish.py --publish-only   # Publish existing .vsix
    python publish.py --dry-run        # Preview without executing
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    print("Missing python-dotenv. Run: pip install python-dotenv")
    sys.exit(1)

# Load environment variables
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# =============================================================================
# CONFIGURATION
# =============================================================================

EXTENSION_REPO = "https://github.com/fabioc-aloha/Alex_Plug_In.git"
EXTENSION_REPO_NAME = "fabioc-aloha/Alex_Plug_In"
EXTENSION_DIR = Path(__file__).parent.parent / "extension-build"
PUBLISHER = "fabioc-aloha"
EXTENSION_ID = "alex-cognitive-architecture"

# =============================================================================
# HELPERS
# =============================================================================

def run_command(cmd: list[str], cwd: Path = None, capture: bool = False, check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and handle errors."""
    print(f"  → {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=capture,
            text=True,
            check=check
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Command failed: {e}")
        if e.stdout:
            print(f"  stdout: {e.stdout}")
        if e.stderr:
            print(f"  stderr: {e.stderr}")
        raise


def get_version(extension_dir: Path) -> str:
    """Get version from package.json."""
    package_json = extension_dir / "package.json"
    with open(package_json) as f:
        data = json.load(f)
    return data.get("version", "0.0.0")


def get_changelog_section(extension_dir: Path, version: str) -> str:
    """Extract release notes for a specific version from CHANGELOG.md."""
    changelog = extension_dir / "CHANGELOG.md"
    if not changelog.exists():
        return f"Release v{version}"
    
    content = changelog.read_text()
    
    # Find the section for this version
    pattern = rf"## \[{re.escape(version)}\].*?\n(.*?)(?=\n## \[|\Z)"
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        notes = match.group(1).strip()
        # Clean up empty sections
        notes = re.sub(r"### \w+\n\n- \n", "", notes)
        notes = re.sub(r"### \w+\n\n\n", "", notes)
        return notes if notes else f"Release v{version}"
    
    return f"Release v{version}"


# =============================================================================
# PREREQUISITE CHECKS
# =============================================================================

def check_prerequisites() -> bool:
    """Verify all required tools are installed."""
    print("\n🔍 Checking prerequisites...\n")

    checks = [
        ("node", ["node", "--version"], "Node.js"),
        ("npm", ["npm.cmd", "--version"], "npm"),
        ("vsce", ["vsce.cmd", "--version"], "vsce (VS Code Extension Manager)"),
        ("git", ["git", "--version"], "Git"),
        ("gh", ["gh", "--version"], "GitHub CLI"),
    ]

    all_good = True
    for name, cmd, display in checks:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            version = result.stdout.strip().split("\n")[0]
            print(f"  ✅ {display}: {version}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"  ❌ {display}: NOT FOUND")
            if name == "vsce":
                print(f"     Install with: npm install -g @vscode/vsce")
            elif name == "gh":
                print(f"     Install from: https://cli.github.com/")
            all_good = False

    # Check PAT
    pat = os.getenv("VSCE_PAT")
    if pat:
        print(f"  ✅ VSCE_PAT: Configured ({len(pat)} chars)")
    else:
        print(f"  ⚠️  VSCE_PAT: Not set in .env (needed for publishing)")

    # Check GitHub CLI auth
    try:
        result = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✅ GitHub CLI: Authenticated")
        else:
            print(f"  ⚠️  GitHub CLI: Not authenticated (run: gh auth login)")
    except FileNotFoundError:
        pass

    print()
    return all_good


# =============================================================================
# CLONE/UPDATE REPO
# =============================================================================

def setup_extension_repo(dry_run: bool = False) -> Path:
    """Clone or update the extension repository."""
    print("\n📥 Setting up extension repository...\n")

    if dry_run:
        print(f"  [DRY RUN] Would clone/update {EXTENSION_REPO}")
        print(f"  [DRY RUN] Target directory: {EXTENSION_DIR}")
        return EXTENSION_DIR

    if EXTENSION_DIR.exists():
        print(f"  📂 Repository exists at {EXTENSION_DIR}")
        print(f"  🔄 Pulling latest changes...")
        run_command(["git", "fetch", "origin"], cwd=EXTENSION_DIR)
        run_command(["git", "reset", "--hard", "origin/main"], cwd=EXTENSION_DIR)
        run_command(["git", "clean", "-fd"], cwd=EXTENSION_DIR)
    else:
        print(f"  📂 Cloning repository...")
        run_command(["git", "clone", EXTENSION_REPO, str(EXTENSION_DIR)])

    print(f"  ✅ Repository ready")
    return EXTENSION_DIR


# =============================================================================
# BUILD & PACKAGE
# =============================================================================

def install_dependencies(extension_dir: Path, dry_run: bool = False) -> None:
    """Install npm dependencies."""
    print("\n📦 Installing dependencies...\n")

    if dry_run:
        print(f"  [DRY RUN] Would run: npm ci")
        return

    run_command(["npm.cmd", "ci"], cwd=extension_dir)
    print(f"  ✅ Dependencies installed")


def build_extension(extension_dir: Path, dry_run: bool = False) -> None:
    """Compile the extension."""
    print("\n🔨 Building extension...\n")

    if dry_run:
        print(f"  [DRY RUN] Would run: npm run compile")
        return

    run_command(["npm.cmd", "run", "compile"], cwd=extension_dir)
    print(f"  ✅ Build complete")


def package_extension(extension_dir: Path, dry_run: bool = False) -> Path:
    """Package the extension into a .vsix file."""
    print("\n📦 Packaging extension...\n")

    if dry_run:
        print(f"  [DRY RUN] Would run: vsce package")
        print(f"  [DRY RUN] Output: {extension_dir / EXTENSION_ID}-X.Y.Z.vsix")
        return extension_dir / f"{EXTENSION_ID}-0.0.0.vsix"

    version = get_version(extension_dir)
    vsix_name = f"{EXTENSION_ID}-{version}.vsix"
    vsix_path = extension_dir / vsix_name

    # Remove old vsix files
    for old_vsix in extension_dir.glob("*.vsix"):
        old_vsix.unlink()

    run_command(["vsce.cmd", "package"], cwd=extension_dir)

    # Find the created vsix
    vsix_files = list(extension_dir.glob("*.vsix"))
    if not vsix_files:
        raise RuntimeError("No .vsix file created!")

    vsix_path = vsix_files[0]
    size_kb = vsix_path.stat().st_size / 1024
    print(f"  ✅ Package created: {vsix_path.name} ({size_kb:.1f} KB)")

    return vsix_path


# =============================================================================
# PUBLISH
# =============================================================================

def verify_pat() -> str:
    """Verify PAT is configured and valid."""
    print("\n🔑 Verifying PAT...\n")

    pat = os.getenv("VSCE_PAT")
    if not pat:
        print("  ❌ VSCE_PAT not set in .env file")
        print("  💡 Add your PAT to scripts/.env:")
        print("     VSCE_PAT=your_token_here")
        sys.exit(1)

    # Verify PAT
    try:
        result = subprocess.run(
            ["vsce.cmd", "verify-pat", PUBLISHER],
            env={**os.environ, "VSCE_PAT": pat},
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"  ✅ PAT verified for publisher: {PUBLISHER}")
        else:
            print(f"  ❌ PAT verification failed")
            print(f"     {result.stderr}")
            sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"  ❌ PAT verification failed: {e}")
        sys.exit(1)

    return pat


def publish_extension(vsix_path: Path, pat: str, dry_run: bool = False) -> None:
    """Publish the extension to VS Code Marketplace."""
    print("\n🚀 Publishing to VS Code Marketplace...\n")

    if dry_run:
        print(f"  [DRY RUN] Would publish: {vsix_path.name}")
        return

    if not vsix_path.exists():
        print(f"  ❌ VSIX file not found: {vsix_path}")
        sys.exit(1)

    run_command(
        ["vsce.cmd", "publish", "-p", pat, "--packagePath", str(vsix_path)],
        cwd=vsix_path.parent
    )

    print(f"  ✅ Published successfully!")
    print(f"\n  🔗 Marketplace: https://marketplace.visualstudio.com/items?itemName={PUBLISHER}.{EXTENSION_ID}")


# =============================================================================
# GITHUB RELEASES
# =============================================================================

def check_release_exists(version: str) -> bool:
    """Check if a GitHub release already exists for this version."""
    result = subprocess.run(
        ["gh", "release", "view", f"v{version}", "--repo", EXTENSION_REPO_NAME],
        capture_output=True,
        text=True
    )
    return result.returncode == 0


def create_github_release(vsix_path: Path, extension_dir: Path, dry_run: bool = False) -> None:
    """Create a GitHub release with the .vsix file attached."""
    print("\n🏷️  Creating GitHub Release...\n")

    if dry_run:
        print(f"  [DRY RUN] Would create release: vX.Y.Z")
        print(f"  [DRY RUN] Would attach: {vsix_path.name}")
        return

    version = get_version(extension_dir)
    tag = f"v{version}"

    # Check if release already exists
    if check_release_exists(version):
        print(f"  ⚠️  Release {tag} already exists")
        response = input("  Overwrite existing release? [y/N]: ")
        if response.lower() != "y":
            print("  ⏭️  Skipping GitHub release")
            return
        # Delete existing release
        run_command(
            ["gh", "release", "delete", tag, "--repo", EXTENSION_REPO_NAME, "--yes"],
            check=False
        )
    
    # Get release notes from CHANGELOG
    notes = get_changelog_section(extension_dir, version)
    
    # Create release with .vsix attached
    run_command([
        "gh", "release", "create", tag,
        str(vsix_path),
        "--repo", EXTENSION_REPO_NAME,
        "--title", f"Alex Cognitive Architecture v{version}",
        "--notes", notes
    ])
    
    print(f"  ✅ GitHub release created: {tag}")
    print(f"  🔗 https://github.com/{EXTENSION_REPO_NAME}/releases/tag/{tag}")


def list_github_releases() -> None:
    """List recent GitHub releases."""
    print("\n📋 Recent GitHub Releases:\n")
    
    result = subprocess.run(
        ["gh", "release", "list", "--repo", EXTENSION_REPO_NAME, "--limit", "5"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0 and result.stdout:
        print(result.stdout)
    else:
        print("  No releases found")


def download_release_vsix(version: str = None, output_dir: Path = None) -> Path:
    """Download .vsix from a GitHub release."""
    print("\n📥 Downloading .vsix from GitHub Release...\n")
    
    output_dir = output_dir or Path.cwd()
    
    if version:
        tag = f"v{version}"
    else:
        # Get latest release
        result = subprocess.run(
            ["gh", "release", "view", "--repo", EXTENSION_REPO_NAME, "--json", "tagName"],
            capture_output=True,
            text=True,
            check=True
        )
        tag = json.loads(result.stdout)["tagName"]
    
    print(f"  📦 Downloading from release: {tag}")
    
    # Download assets
    run_command([
        "gh", "release", "download", tag,
        "--repo", EXTENSION_REPO_NAME,
        "--pattern", "*.vsix",
        "--dir", str(output_dir)
    ])
    
    # Find downloaded file
    vsix_files = list(output_dir.glob("*.vsix"))
    if vsix_files:
        print(f"  ✅ Downloaded: {vsix_files[0].name}")
        return vsix_files[0]
    else:
        raise RuntimeError("No .vsix file downloaded")


def show_marketplace_status() -> None:
    """Show current extension status on Marketplace."""
    print("\n📊 Marketplace Status...\n")

    try:
        result = subprocess.run(
            ["vsce.cmd", "show", f"{PUBLISHER}.{EXTENSION_ID}"],
            capture_output=True,
            text=True
        )
        print(result.stdout)
    except subprocess.CalledProcessError:
        print("  Could not fetch marketplace status")


# =============================================================================
# MAIN WORKFLOWS
# =============================================================================

def workflow_package(dry_run: bool = False) -> Path:
    """Full package workflow: clone, install, build, package."""
    extension_dir = setup_extension_repo(dry_run)

    if not dry_run:
        install_dependencies(extension_dir, dry_run)
        build_extension(extension_dir, dry_run)

    vsix_path = package_extension(extension_dir, dry_run)
    return vsix_path


def workflow_publish(dry_run: bool = False, skip_github: bool = False) -> None:
    """Full publish workflow: package + publish + GitHub release."""
    pat = verify_pat()
    vsix_path = workflow_package(dry_run)
    publish_extension(vsix_path, pat, dry_run)
    
    # Create GitHub release
    if not skip_github:
        extension_dir = EXTENSION_DIR
        create_github_release(vsix_path, extension_dir, dry_run)

    if not dry_run:
        show_marketplace_status()


def workflow_publish_only(vsix_path: str = None, dry_run: bool = False) -> None:
    """Publish an existing .vsix file."""
    pat = verify_pat()

    if vsix_path:
        path = Path(vsix_path)
    else:
        # Find most recent vsix in extension-build
        vsix_files = list(EXTENSION_DIR.glob("*.vsix"))
        if not vsix_files:
            print("  ❌ No .vsix file found. Run --package first.")
            sys.exit(1)
        path = max(vsix_files, key=lambda p: p.stat().st_mtime)

    print(f"\n📦 Using package: {path.name}")
    publish_extension(path, pat, dry_run)

    if not dry_run:
        show_marketplace_status()


def workflow_release_only(version: str = None, dry_run: bool = False) -> None:
    """Create GitHub release for existing version (without publishing to Marketplace)."""
    extension_dir = setup_extension_repo(dry_run)
    
    if version:
        # Check out specific version tag
        if not dry_run:
            run_command(["git", "checkout", f"v{version}"], cwd=extension_dir)
    
    vsix_path = workflow_package(dry_run)
    create_github_release(vsix_path, extension_dir, dry_run)


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Package and publish Alex Cognitive Architecture extension",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Check prerequisites
    python publish.py --check

    # Package only (creates .vsix in extension-build/)
    python publish.py --package

    # Full publish (package, publish to Marketplace, create GitHub release)
    python publish.py --publish

    # Publish without creating GitHub release
    python publish.py --publish --skip-github

    # Publish existing .vsix
    python publish.py --publish-only
    python publish.py --publish-only --vsix ./my-extension.vsix

    # Create GitHub release only (for existing version)
    python publish.py --release-only
    python publish.py --release-only --version 1.5.4

    # List GitHub releases
    python publish.py --list-releases

    # Download .vsix from GitHub release
    python publish.py --download-release
    python publish.py --download-release --version 1.5.4

    # Preview without executing
    python publish.py --publish --dry-run
        """,
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true", help="Verify prerequisites")
    group.add_argument("--package", action="store_true", help="Clone, build, and package")
    group.add_argument("--publish", action="store_true", help="Full publish workflow")
    group.add_argument("--publish-only", action="store_true", help="Publish existing .vsix")
    group.add_argument("--release-only", action="store_true", help="Create GitHub release only")
    group.add_argument("--list-releases", action="store_true", help="List GitHub releases")
    group.add_argument("--download-release", action="store_true", help="Download .vsix from GitHub release")

    parser.add_argument("--vsix", type=str, help="Path to .vsix file (for --publish-only)")
    parser.add_argument("--version", type=str, help="Version for --release-only or --download-release")
    parser.add_argument("--skip-github", action="store_true", help="Skip GitHub release creation")
    parser.add_argument("--dry-run", action="store_true", help="Preview without executing")

    args = parser.parse_args()

    print("=" * 60)
    print("  Alex Cognitive Architecture - Publisher")
    print("=" * 60)

    if args.check:
        success = check_prerequisites()
        sys.exit(0 if success else 1)

    elif args.package:
        workflow_package(args.dry_run)

    elif args.publish:
        workflow_publish(args.dry_run, args.skip_github)

    elif args.publish_only:
        workflow_publish_only(args.vsix, args.dry_run)

    elif args.release_only:
        workflow_release_only(args.version, args.dry_run)

    elif args.list_releases:
        list_github_releases()

    elif args.download_release:
        download_release_vsix(args.version)

    if args.dry_run:
        print("\n⚠️  This was a dry run. No changes were made.")
        print("   Remove --dry-run to execute for real.")


if __name__ == "__main__":
    main()




