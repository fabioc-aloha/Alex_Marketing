#!/usr/bin/env python3
"""
Alex Cognitive Architecture - Extension Publishing Script

Automates packaging and publishing the VS Code extension from the marketing repo.
Clones/updates the extension repo, builds, packages, and publishes.

Requirements:
    - Node.js and npm installed
    - vsce installed globally (npm install -g @vscode/vsce)
    - Git installed
    - PAT stored in .env file

Usage:
    python publish.py --check          # Verify prerequisites
    python publish.py --package        # Package only (creates .vsix)
    python publish.py --publish        # Package and publish
    python publish.py --publish-only   # Publish existing .vsix
    python publish.py --dry-run        # Preview without executing
"""

import argparse
import json
import os
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
EXTENSION_DIR = Path(__file__).parent.parent / "extension-build"
PUBLISHER = "fabioc-aloha"
EXTENSION_ID = "alex-cognitive-architecture"

# =============================================================================
# HELPERS
# =============================================================================

def run_command(cmd: list[str], cwd: Path = None, capture: bool = False) -> subprocess.CompletedProcess:
    """Run a command and handle errors."""
    print(f"  → {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=capture,
            text=True,
            check=True
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


# =============================================================================
# PREREQUISITE CHECKS
# =============================================================================

def check_prerequisites() -> bool:
    """Verify all required tools are installed."""
    print("\n🔍 Checking prerequisites...\n")
    
    checks = [
        ("node", ["node", "--version"], "Node.js"),
        ("npm", ["npm", "--version"], "npm"),
        ("vsce", ["vsce", "--version"], "vsce (VS Code Extension Manager)"),
        ("git", ["git", "--version"], "Git"),
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
            all_good = False
    
    # Check PAT
    pat = os.getenv("VSCE_PAT")
    if pat:
        print(f"  ✅ VSCE_PAT: Configured ({len(pat)} chars)")
    else:
        print(f"  ⚠️  VSCE_PAT: Not set in .env (needed for publishing)")
    
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
    
    run_command(["npm", "ci"], cwd=extension_dir)
    print(f"  ✅ Dependencies installed")


def build_extension(extension_dir: Path, dry_run: bool = False) -> None:
    """Compile the extension."""
    print("\n🔨 Building extension...\n")
    
    if dry_run:
        print(f"  [DRY RUN] Would run: npm run compile")
        return
    
    run_command(["npm", "run", "compile"], cwd=extension_dir)
    print(f"  ✅ Build complete")


def package_extension(extension_dir: Path, dry_run: bool = False) -> Path:
    """Package the extension into a .vsix file."""
    print("\n📦 Packaging extension...\n")
    
    version = get_version(extension_dir)
    vsix_name = f"{EXTENSION_ID}-{version}.vsix"
    vsix_path = extension_dir / vsix_name
    
    if dry_run:
        print(f"  [DRY RUN] Would run: vsce package")
        print(f"  [DRY RUN] Output: {vsix_path}")
        return vsix_path
    
    # Remove old vsix files
    for old_vsix in extension_dir.glob("*.vsix"):
        old_vsix.unlink()
    
    run_command(["vsce", "package"], cwd=extension_dir)
    
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
            ["vsce", "verify-pat", PUBLISHER],
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
    print("\n🚀 Publishing extension...\n")
    
    if dry_run:
        print(f"  [DRY RUN] Would publish: {vsix_path.name}")
        return
    
    if not vsix_path.exists():
        print(f"  ❌ VSIX file not found: {vsix_path}")
        sys.exit(1)
    
    run_command(
        ["vsce", "publish", "-p", pat, "--packagePath", str(vsix_path)],
        cwd=vsix_path.parent
    )
    
    print(f"  ✅ Published successfully!")
    print(f"\n  🔗 Marketplace: https://marketplace.visualstudio.com/items?itemName={PUBLISHER}.{EXTENSION_ID}")


def show_marketplace_status() -> None:
    """Show current extension status on Marketplace."""
    print("\n📊 Marketplace Status...\n")
    
    try:
        result = subprocess.run(
            ["vsce", "show", f"{PUBLISHER}.{EXTENSION_ID}"],
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


def workflow_publish(dry_run: bool = False) -> None:
    """Full publish workflow: package + publish."""
    pat = verify_pat()
    vsix_path = workflow_package(dry_run)
    publish_extension(vsix_path, pat, dry_run)
    
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

    # Full publish (clone, build, package, publish)
    python publish.py --publish

    # Publish existing .vsix
    python publish.py --publish-only
    python publish.py --publish-only --vsix ./my-extension.vsix

    # Preview without executing
    python publish.py --publish --dry-run
        """,
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true", help="Verify prerequisites")
    group.add_argument("--package", action="store_true", help="Clone, build, and package")
    group.add_argument("--publish", action="store_true", help="Full publish workflow")
    group.add_argument("--publish-only", action="store_true", help="Publish existing .vsix")
    
    parser.add_argument("--vsix", type=str, help="Path to .vsix file (for --publish-only)")
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
        workflow_publish(args.dry_run)
    
    elif args.publish_only:
        workflow_publish_only(args.vsix, args.dry_run)
    
    if args.dry_run:
        print("\n⚠️  This was a dry run. No changes were made.")
        print("   Remove --dry-run to execute for real.")


if __name__ == "__main__":
    main()
