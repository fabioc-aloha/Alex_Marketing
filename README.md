# Alex Marketing

Marketing and release automation for [Alex Cognitive Architecture](https://github.com/fabioc-aloha/Alex_Plug_In).

## Scripts

| Script | Purpose |
| ------ | ------- |
| `release.py` | **Full release workflow** - bump, publish, announce |
| `publish.py` | Package and publish extension to Marketplace |
| `version.py` | Bump version and update files |
| `announce.py` | Post announcements to social media |

## Quick Start

`ash
# Install dependencies
cd scripts
pip install -r requirements.txt

# Configure credentials
cp .env.example .env
# Edit .env with your PAT and API keys

# Preview a full release (dry run)
python release.py --bump patch --dry-run

# Do a real release
python release.py --bump patch
`

## Full Release Workflow

One command does everything:

`ash
python release.py --bump patch
`

This will:
1. ✅ Check prerequisites (node, npm, vsce, git, PAT)
2. 📦 Clone/update extension repo
3. 🔢 Bump version in package.json, CHANGELOG.md, copilot-instructions.md
4. 🏗️ Build and package extension
5. 🚀 Publish to VS Code Marketplace
6. 📢 Post to Reddit, Twitter, Dev.to

## Individual Scripts

### publish.py - Package & Publish

`ash
# Check prerequisites
python publish.py --check

# Package only (creates .vsix)
python publish.py --package

# Full publish
python publish.py --publish

# Publish existing .vsix
python publish.py --publish-only
`

### version.py - Version Management

`ash
# Bump patch (2.0.0 -> 2.0.1)
python version.py --bump patch

# Bump minor (2.0.0 -> 2.1.0)
python version.py --bump minor

# Bump major (2.0.0 -> 3.0.0)
python version.py --bump major

# Set specific version
python version.py --set 2.1.0
`

### announce.py - Social Media

`ash
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
`

## Configuration

### .env File

`nv
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
`

## Architecture

`
Alex_Marketing (this repo)
    │
    ├── scripts/
    │   ├── release.py      # Orchestrates full release
    │   ├── publish.py      # Packaging & publishing
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
    └── ...
`

## Related

- [Alex Cognitive Architecture](https://github.com/fabioc-aloha/Alex_Plug_In) - Extension source
- [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=fabioc-aloha.alex-cognitive-architecture)
