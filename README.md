# Alex Marketing

Marketing automation for [Alex Cognitive Architecture](https://github.com/fabioc-aloha/Alex_Plug_In).

## Overview

This repository contains marketing materials and automation scripts for promoting the Alex VS Code extension.

| Component | Description |
| --------- | ----------- |
| `MARKETING.md` | Full marketing plan and strategies |
| `scripts/announce.py` | Multi-platform announcement automation |
| `scripts/.env.example` | API credentials template |

## Quick Start

```bash
# Install dependencies
cd scripts
pip install -r requirements.txt

# Configure credentials
cp .env.example .env
# Edit .env with your API keys

# Preview announcements (dry run)
python announce.py --platform all --dry-run

# Post to Reddit
python announce.py --platform reddit --subreddit vscode

# Post everywhere
python announce.py --platform all
```

## Automated Sync

The announcement script automatically fetches the latest version and changelog from the main extension repository - no manual sync needed.

```python
# Version is fetched from:
https://raw.githubusercontent.com/fabioc-aloha/Alex_Plug_In/main/package.json

# Changelog is fetched from:
https://raw.githubusercontent.com/fabioc-aloha/Alex_Plug_In/main/CHANGELOG.md
```

## Supported Platforms

| Platform | Automation | Setup Required |
| -------- | ---------- | -------------- |
| Reddit | Full | PRAW credentials |
| Twitter/X | Full | X API v2 |
| Dev.to | Full | API key |
| Discord | Full | Webhook URL |
| LinkedIn | Semi-auto | None (clipboard) |
| Hacker News | Manual | No API |

## Related

- [Alex Cognitive Architecture](https://github.com/fabioc-aloha/Alex_Plug_In) - Main extension repository
- [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=fabioc-aloha.alex-cognitive-architecture) - Extension page

## License

MIT - Same as the main Alex repository
