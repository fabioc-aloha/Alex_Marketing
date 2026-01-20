# Alex Marketing

Marketing and release automation for [Alex Cognitive Architecture](https://github.com/fabioc-aloha/Alex_Plug_In).

## Scripts

| Script | Purpose |
| ------ | ------- |
| `release.py` | **Full release workflow** - bump, publish, announce |
| `publish.py` | Package, publish, and create GitHub releases |
| `version.py` | Bump version and update files |
| `announce.py` | Post announcements to social media |

## Quick Start

```bash
# Install dependencies
cd scripts
pip install -r requirements.txt

# Configure credentials
cp .env.example .env
# Edit .env with your PAT and API keys

# Authenticate GitHub CLI
gh auth login

# Preview a full release (dry run)
python release.py --bump patch --dry-run

# Do a real release
python release.py --bump patch
```

## Full Release Workflow

One command does everything:

```bbash
python release.py --bump patch
```

This will:
1. ✅ Check prerequisites (node, npm, vsce, git, gh, PAT)
2. 📦 Clone/update extension repo
3. 🔢 Bump version in package.json, CHANGELOG.md, copilot-instructions.md
4. 🏗️ Build and package extension
5. 🚀 Publish to VS Code Marketplace
6. 🏷️ Create GitHub Release with .vsix attached
7. 📢 Post to Reddit, Twitter, Dev.to

## GitHub Releases

**.vsix files are stored as GitHub Release assets** - not in git. This keeps the repos clean while providing versioned binary downloads.

### How It Works

1. When you publish, a GitHub Release is automatically created
2. The .vsix file is attached as a release asset
3. Users can download any version from the Releases page

### Commands

```bash
# Full publish (includes GitHub release)
python publish.py --publish

# Publish without GitHub release
python publish.py --publish --skip-github

# Create GitHub release only (for existing version)
python publish.py --release-only
python publish.py --release-only --version 1.5.4

# List recent releases
python publish.py --list-releases

# Download .vsix from a release
python publish.py --download-release              # Latest version
python publish.py --download-release --version 1.5.4
```

### Manual Access

- **Browse**: https://github.com/fabioc-aloha/Alex_Plug_In/releases
- **Download**: Click the .vsix asset on any release
- **Install**: `code --install-extension alex-cognitive-architecture-X.Y.Z.vsix`

## Individual Scripts

### publish.py - Package & Publish

```bash
# Check prerequisites
python publish.py --check

# Package only (creates .vsix)
python publish.py --package

# Full publish (Marketplace + GitHub release)
python publish.py --publish

# Publish without GitHub release
python publish.py --publish --skip-github

# Publish existing .vsix
python publish.py --publish-only
```

### version.py - Version Management

```bash
# Bump patch (2.0.0 -> 2.0.1)
python version.py --bump patch

# Bump minor (2.0.0 -> 2.1.0)
python version.py --bump minor

# Bump major (2.0.0 -> 3.0.0)
python version.py --bump major

# Set specific version
python version.py --set 2.1.0
```

### announce.py - Social Media

```bash
# Preview all platforms
python announce.py --platform all --dry-run

# Post to Reddit
python announce.py --platform reddit --subreddit vscode

# Post Twitter thread
python announce.py --platform twitter

# Publish Dev.to article
python announce.py --platform devto

# Post to Discord
python announce.py --platform discord
```

## Configuration

### Prerequisites

```bash
# Node.js & npm - for building extension
# Git - for cloning repos
# vsce - VS Code Extension Manager
npm install -g @vscode/vsce

# GitHub CLI - for releases
# Install from: https://cli.github.com/
gh auth login
```

### .env File

```env
# VS Code Marketplace PAT
VSCE_PAT=your_pat_here

# Reddit
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
REDDIT_USERNAME=
REDDIT_PASSWORD=

# Twitter/X
TWITTER_API_KEY=
TWITTER_API_SECRET=
TWITTER_ACCESS_TOKEN=
TWITTER_ACCESS_SECRET=

# Dev.to
DEVTO_API_KEY=

# Discord
DISCORD_WEBHOOK_URL=
```

## Architecture

```
Alex_Marketing (this repo)
    │
    ├── scripts/
    │   ├── release.py      # Orchestrates full release
    │   ├── publish.py      # Packaging, publishing & GitHub releases
    │   ├── version.py      # Version management
    │   ├── announce.py     # Social media posting
    │   └── .env            # Credentials (gitignored)
    │
    ├── MARKETING.md        # Full marketing plan
    └── PRE-PUBLISH-CHECKLIST.md

    ↓ Fetches via GitHub API

Alex_Plug_In (extension repo)
    ├── package.json        # Version source of truth
    ├── CHANGELOG.md        # Release notes
    └── Releases/           # .vsix files as GitHub Release assets
```

## Version History via Releases

Instead of storing .vsix files in git:
- Each version gets a GitHub Release tag (v2.0.0, v2.0.1, etc.)
- The .vsix is attached as a downloadable asset
- Release notes are extracted from CHANGELOG.md
- Full history preserved without bloating repositories


## Key Workflow Notes

### Tested Release Process (v2.0.1)

The full release was tested and works as follows:

1. **Run from scripts directory**: `cd scripts`
2. **Execute release**: `python release.py --bump patch`
3. **Workflow executes**:
   - Checks prerequisites (node, npm, vsce, git, gh, PAT)
   - Clones/updates extension repo to `extension-build/`
   - Bumps version and pushes changes (`--auto-push`)
   - Builds and packages `.vsix`
   - Publishes to VS Code Marketplace
   - Creates GitHub Release with `.vsix` attached

### Windows Compatibility

Scripts are Windows-compatible with these considerations:

- **npm/vsce calls**: Use `.cmd` extension (`npm.cmd`, `npx.cmd`) for subprocess calls
- **File encoding**: All file operations use UTF-8 encoding explicitly
- **Path handling**: Uses `pathlib.Path` for cross-platform paths
- **Shell commands**: Subprocess calls work in both PowerShell and cmd

### Workflow Order (Important)

The release workflow ensures proper sequencing:

1. `version.py --auto-push` bumps AND pushes before publish
2. `publish.py` fetches fresh from origin (gets the pushed version)
3. This prevents the "reset wiping local changes" issue

### Dry Run Mode

Always test with `--dry-run` first:

`bash
python release.py --bump patch --dry-run
`

Dry run will:
- ✅ Check all prerequisites
- ✅ Show what version would be bumped
- ✅ Skip actual publishing and GitHub release creation
- ✅ Not modify any files or push any changes

## Related

- [Alex Cognitive Architecture](https://github.com/fabioc-aloha/Alex_Plug_In) - Extension source
- [Releases](https://github.com/fabioc-aloha/Alex_Plug_In/releases) - All versions with .vsix downloads
- [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=fabioc-aloha.alex-cognitive-architecture)
