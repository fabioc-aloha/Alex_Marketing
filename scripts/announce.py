#!/usr/bin/env python3
"""
Alex Cognitive Architecture - Multi-Platform Announcement Script

Automates posting release announcements to:
- Reddit (r/vscode, r/github, r/programming, r/artificial, r/ChatGPT)
- Dev.to
- Twitter/X
- Discord (webhook)
- LinkedIn (manual - opens browser)

Requirements:
    pip install praw python-dotenv requests tweepy

Setup:
    1. Copy scripts/.env.example to scripts/.env
    2. Fill in API credentials (see MARKETING.md for instructions)
    3. Run: python scripts/announce.py --platform all --version 2.0.0
"""

import argparse
import json
import os
import subprocess
import sys
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    import praw
    import requests
    import tweepy
    from dotenv import load_dotenv
except ImportError:
    print("Missing dependencies. Run: pip install praw python-dotenv requests tweepy")
    sys.exit(1)

# Load environment variables
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# =============================================================================
# CONFIGURATION
# =============================================================================

EXTENSION_NAME = "Alex Cognitive Architecture"
EXTENSION_ID = "fabioc-aloha.alex-cognitive-architecture"
MARKETPLACE_URL = "https://marketplace.visualstudio.com/items?itemName=fabioc-aloha.alex-cognitive-architecture"
GITHUB_URL = "https://github.com/fabioc-aloha/Alex_Plug_In"
DOCS_URL = "https://github.com/fabioc-aloha/Alex_Plug_In/blob/main/README.md"

# =============================================================================
# COPY TEMPLATES
# =============================================================================

def get_reddit_title(version: str, subreddit: str) -> str:
    """Get Reddit post title based on subreddit."""
    titles = {
        "vscode": f"I built a VS Code extension that gives GitHub Copilot persistent memory - Alex v{version}",
        "github": f"Alex Cognitive Architecture v{version} - Transform Copilot into an intelligent learning partner",
        "programming": f"Building a cognitive architecture for AI assistants - Alex v{version} (VS Code/Copilot)",
        "artificial": f"Alex v{version}: Giving GitHub Copilot persistent memory and meta-cognitive awareness",
        "ChatGPT": f"I made a VS Code extension that gives Copilot memory like ChatGPT - Alex v{version}",
        "LocalLLaMA": f"Alex v{version}: Open source cognitive architecture for GitHub Copilot with 150+ AI models",
    }
    return titles.get(subreddit, titles["vscode"])


def get_reddit_body(version: str, subreddit: str) -> str:
    """Get Reddit post body."""
    return f"""Hey r/{subreddit}!

I've been working on something I'm really excited to share - **Alex Cognitive Architecture v{version}**, a free VS Code extension that transforms GitHub Copilot into an intelligent learning partner.

## What it does

Instead of Copilot forgetting everything between sessions, Alex gives it:

- 🧠 **Persistent Memory** - Stores knowledge in markdown files that survive restarts
- 🔄 **Meta-cognitive Awareness** - Monitors its own reasoning and learning effectiveness
- 🌙 **Neural Maintenance** - Automated "dream" protocols that optimize memory
- 💬 **Chat Participant** - Talk to @alex directly in VS Code chat
- 🛠️ **150+ AI Models** - Access Azure AI Foundry models (GPT-5, Claude, Llama, etc.)

## How it works

Alex uses a hybrid memory system inspired by cognitive psychology:
- Working memory (7±2 rule)
- Procedural memory (.instructions.md files)
- Episodic memory (.prompt.md files)
- Domain knowledge (DK-*.md files)

## What's new in v{version}

- Chat Participant API - Talk to @alex directly
- 5 Language Model Tools for inline assistance
- 5 Custom Agents (Azure, M365, Cognitive specialists)
- 150+ Azure AI Foundry model integrations
- Improved upgrade path from previous versions

## Links

- 🔗 [VS Code Marketplace]({MARKETPLACE_URL})
- 📦 [GitHub Source]({GITHUB_URL})
- 📖 [Documentation]({DOCS_URL})

It's completely free and open source. Would love to hear your feedback!

**Edit:** Happy to answer any questions about the cognitive architecture or implementation!
"""


def get_twitter_thread(version: str) -> list[str]:
    """Get Twitter thread as list of tweets."""
    return [
        f"""🧠 Just released Alex v{version} - a VS Code extension that gives GitHub Copilot a brain!

Here's how it works 👇""",
        
        """1/ The problem: Copilot forgets everything between sessions. It doesn't learn your style, remember your patterns, or build on previous conversations.""",
        
        f"""2/ The solution: A cognitive architecture based on human memory research.

Alex gives Copilot:
🧠 Persistent memory
🔄 Meta-cognitive awareness
🌙 Neural maintenance ("dream" protocols)
💬 Direct chat via @alex""",
        
        """3/ How it works:

• Working Memory → 7±2 active rules (Miller's Law)
• Procedural Memory → .instructions.md files
• Episodic Memory → .prompt.md files
• Domain Knowledge → DK-*.md expertise files""",
        
        f"""4/ NEW in v{version}:

• Chat Participant API - Talk to @alex directly
• 5 Language Model Tools - #alex-status, #alex-dream, etc.
• 5 Custom Agents - Azure, M365, Cognitive specialists
• 150+ Azure AI Foundry models""",
        
        f"""5/ It's completely FREE and open source.

🔗 VS Code: {MARKETPLACE_URL}
📦 GitHub: {GITHUB_URL}

Would love your feedback! 🙏

#VSCode #GitHubCopilot #AI #DevTools""",
    ]


def get_devto_article(version: str) -> dict:
    """Get Dev.to article as dict with title, tags, and body."""
    return {
        "title": f"Alex v{version}: Building a Cognitive Architecture for GitHub Copilot",
        "tags": ["vscode", "githubcopilot", "ai", "productivity"],
        "body": f"""---
title: Alex v{version}: Building a Cognitive Architecture for GitHub Copilot
published: true
description: How I transformed Copilot from a forgetful autocomplete into an intelligent learning partner
tags: vscode, githubcopilot, ai, productivity
cover_image: https://raw.githubusercontent.com/fabioc-aloha/Alex_Plug_In/main/assets/banner.png
---

# Alex v{version}: Building a Cognitive Architecture for GitHub Copilot

Have you ever wished GitHub Copilot could remember your coding preferences? Or learn from your project over time instead of starting fresh every session?

I spent the last 6 months building **Alex** - a VS Code extension that gives Copilot a brain.

## The Problem

Copilot is great at generating code, but it has amnesia. Every session starts from zero. It doesn't remember:
- Your preferred coding style
- Patterns you've established in your project
- Corrections you've made to its suggestions

## The Solution: A Cognitive Architecture

Alex implements a hybrid memory system based on cognitive psychology research:

### 1. Working Memory (7±2 Rule)

Based on Miller's research, Alex maintains 7 active "rules" in context:
- 4 core meta-cognitive rules (always active)
- 3 domain-specific rules (context-activated)

### 2. Procedural Memory

Repeatable processes stored in `.instructions.md` files:

```markdown
# bootstrap-learning.instructions.md
Acquire domain knowledge through conversation...
```

### 3. Episodic Memory

Complex workflows in `.prompt.md` files for meditation and learning sessions.

### 4. Domain Knowledge

Specialized expertise in `DK-*.md` files that can be activated on demand.

## What's New in v{version}

- **Chat Participant API** - Talk to @alex directly in VS Code chat
- **5 Language Model Tools** - Use #alex-status, #alex-dream inline
- **5 Custom Agents** - Specialized agents for Azure, M365, and more
- **150+ AI Models** - Azure AI Foundry integration (GPT-5, Claude, Llama, etc.)

## Try It Yourself

1. Install from [VS Code Marketplace]({MARKETPLACE_URL})
2. Run `Alex: Initialize Architecture`
3. Open chat and type `@alex /status`

## What's Next?

I'm working on:
- Better cross-project memory transfer
- Community-contributed domain knowledge packs
- Integration with more AI models

---

What do you think? Have you tried building memory systems for AI? I'd love to hear your approaches in the comments!

[GitHub]({GITHUB_URL}) | [VS Code Marketplace]({MARKETPLACE_URL})
""",
    }


def get_discord_message(version: str) -> str:
    """Get Discord announcement message."""
    return f"""🎉 **Alex Cognitive Architecture v{version} Released!**

Transform GitHub Copilot into an intelligent learning partner with persistent memory.

**Key Features:**
• 🧠 Memory that survives between sessions
• 💬 Chat participant (@alex)
• 🌙 Neural maintenance protocols
• 🛠️ 150+ Azure AI models

**New in v{version}:**
• Chat Participant API integration
• 5 Language Model Tools
• 5 Custom Agents (Azure, M365, etc.)
• Improved upgrade path

Free & open source!
🔗 {MARKETPLACE_URL}
📦 {GITHUB_URL}
"""


def get_linkedin_post(version: str) -> str:
    """Get LinkedIn post content."""
    return f"""🚀 Excited to announce the release of Alex Cognitive Architecture v{version}!

After months of development, I've created a VS Code extension that transforms GitHub Copilot from a forgetful autocomplete into an intelligent learning partner.

What makes Alex different?

🧠 Persistent Memory - Knowledge survives between sessions
🔄 Meta-Cognitive Awareness - Monitors its own reasoning
🌙 Neural Maintenance - Automated optimization protocols
💬 Chat Integration - Talk directly to @alex in VS Code
🛠️ 150+ AI Models - Azure AI Foundry integration

The architecture is based on cognitive psychology research:
• Working memory (Miller's 7±2 rule)
• Procedural memory (repeatable processes)
• Episodic memory (complex workflows)

It's completely FREE and open source.

🔗 Try it: {MARKETPLACE_URL}
📦 Source: {GITHUB_URL}

I'd love to hear what you think - especially from fellow developers working on AI tooling!

#AI #DeveloperTools #VSCode #GitHubCopilot #OpenSource #Productivity
"""


# =============================================================================
# PLATFORM PUBLISHERS
# =============================================================================

class RedditPublisher:
    """Publish to Reddit using PRAW."""
    
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT", "Alex Announcer/1.0"),
            username=os.getenv("REDDIT_USERNAME"),
            password=os.getenv("REDDIT_PASSWORD"),
        )
    
    def post(self, subreddit: str, version: str, dry_run: bool = False) -> Optional[str]:
        """Post to a subreddit. Returns post URL or None."""
        title = get_reddit_title(version, subreddit)
        body = get_reddit_body(version, subreddit)
        
        if dry_run:
            print(f"\n[DRY RUN] Would post to r/{subreddit}:")
            print(f"  Title: {title}")
            print(f"  Body: {body[:200]}...")
            return None
        
        try:
            sub = self.reddit.subreddit(subreddit)
            submission = sub.submit(title, selftext=body)
            print(f"✅ Posted to r/{subreddit}: {submission.url}")
            return submission.url
        except Exception as e:
            print(f"❌ Failed to post to r/{subreddit}: {e}")
            return None


class TwitterPublisher:
    """Publish to Twitter/X using Tweepy."""
    
    def __init__(self):
        self.client = tweepy.Client(
            consumer_key=os.getenv("TWITTER_API_KEY"),
            consumer_secret=os.getenv("TWITTER_API_SECRET"),
            access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
            access_token_secret=os.getenv("TWITTER_ACCESS_SECRET"),
        )
    
    def post_thread(self, version: str, dry_run: bool = False) -> list[str]:
        """Post a thread. Returns list of tweet URLs."""
        tweets = get_twitter_thread(version)
        urls = []
        
        if dry_run:
            print(f"\n[DRY RUN] Would post Twitter thread ({len(tweets)} tweets):")
            for i, tweet in enumerate(tweets, 1):
                print(f"  Tweet {i}: {tweet[:80]}...")
            return []
        
        try:
            previous_id = None
            for i, tweet in enumerate(tweets):
                response = self.client.create_tweet(
                    text=tweet,
                    in_reply_to_tweet_id=previous_id,
                )
                previous_id = response.data["id"]
                url = f"https://twitter.com/i/web/status/{previous_id}"
                urls.append(url)
                print(f"✅ Posted tweet {i + 1}/{len(tweets)}")
            
            print(f"✅ Thread posted: {urls[0]}")
            return urls
        except Exception as e:
            print(f"❌ Failed to post thread: {e}")
            return []


class DevToPublisher:
    """Publish to Dev.to using their API."""
    
    def __init__(self):
        self.api_key = os.getenv("DEVTO_API_KEY")
        self.base_url = "https://dev.to/api"
    
    def post(self, version: str, dry_run: bool = False) -> Optional[str]:
        """Publish article to Dev.to. Returns article URL or None."""
        article = get_devto_article(version)
        
        if dry_run:
            print(f"\n[DRY RUN] Would publish to Dev.to:")
            print(f"  Title: {article['title']}")
            print(f"  Tags: {article['tags']}")
            print(f"  Body: {article['body'][:200]}...")
            return None
        
        try:
            response = requests.post(
                f"{self.base_url}/articles",
                headers={
                    "api-key": self.api_key,
                    "Content-Type": "application/json",
                },
                json={
                    "article": {
                        "title": article["title"],
                        "body_markdown": article["body"],
                        "published": True,
                        "tags": article["tags"],
                    }
                },
            )
            response.raise_for_status()
            data = response.json()
            url = data.get("url", "https://dev.to")
            print(f"✅ Published to Dev.to: {url}")
            return url
        except Exception as e:
            print(f"❌ Failed to publish to Dev.to: {e}")
            return None


class DiscordPublisher:
    """Publish to Discord using webhooks."""
    
    def __init__(self):
        self.webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    
    def post(self, version: str, dry_run: bool = False) -> bool:
        """Post to Discord webhook. Returns success status."""
        message = get_discord_message(version)
        
        if dry_run:
            print(f"\n[DRY RUN] Would post to Discord:")
            print(f"  Message: {message[:200]}...")
            return True
        
        if not self.webhook_url:
            print("⚠️ DISCORD_WEBHOOK_URL not set, skipping Discord")
            return False
        
        try:
            response = requests.post(
                self.webhook_url,
                json={"content": message},
            )
            response.raise_for_status()
            print("✅ Posted to Discord")
            return True
        except Exception as e:
            print(f"❌ Failed to post to Discord: {e}")
            return False


class LinkedInPublisher:
    """LinkedIn requires manual posting - opens browser with pre-filled content."""
    
    def post(self, version: str, dry_run: bool = False) -> bool:
        """Open LinkedIn with post content in clipboard."""
        content = get_linkedin_post(version)
        
        if dry_run:
            print(f"\n[DRY RUN] Would open LinkedIn:")
            print(f"  Content: {content[:200]}...")
            return True
        
        # Copy to clipboard (cross-platform)
        try:
            if sys.platform == "win32":
                subprocess.run(
                    ["powershell", "-Command", f'Set-Clipboard -Value "{content}"'],
                    check=True,
                    capture_output=True,
                )
            elif sys.platform == "darwin":
                subprocess.run(["pbcopy"], input=content.encode(), check=True)
            else:
                subprocess.run(
                    ["xclip", "-selection", "clipboard"],
                    input=content.encode(),
                    check=True,
                )
            
            # Open LinkedIn share page
            webbrowser.open("https://www.linkedin.com/feed/?shareActive=true")
            print("✅ LinkedIn opened - paste from clipboard (Ctrl+V)")
            return True
        except Exception as e:
            print(f"⚠️ Could not copy to clipboard: {e}")
            print(f"LinkedIn content:\n{content}")
            return False


# =============================================================================
# MAIN
# =============================================================================

def get_current_version() -> str:
    """Get version from extension repo via GitHub API."""
    try:
        response = requests.get(
            "https://raw.githubusercontent.com/fabioc-aloha/Alex_Plug_In/main/package.json",
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        version = data.get("version", "0.0.0")
        print(f"📦 Fetched version {version} from GitHub")
        return version
    except Exception as e:
        print(f"⚠️ Could not fetch from GitHub: {e}")
        print("   Using --version argument or defaulting to 0.0.0")
        return "0.0.0"


def main():
    parser = argparse.ArgumentParser(
        description="Announce Alex releases to multiple platforms",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Dry run all platforms (preview what will be posted)
    python announce.py --platform all --dry-run

    # Post to Reddit only
    python announce.py --platform reddit --subreddit vscode

    # Post to all platforms
    python announce.py --platform all --version 2.0.0

    # Post Twitter thread
    python announce.py --platform twitter

Platforms: reddit, twitter, devto, discord, linkedin, all
        """,
    )
    
    parser.add_argument(
        "--platform",
        choices=["reddit", "twitter", "devto", "discord", "linkedin", "all"],
        required=True,
        help="Platform to post to",
    )
    parser.add_argument(
        "--version",
        default=None,
        help="Version to announce (default: read from package.json)",
    )
    parser.add_argument(
        "--subreddit",
        default="vscode",
        help="Subreddit for Reddit posts (default: vscode)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview posts without actually publishing",
    )
    parser.add_argument(
        "--all-subreddits",
        action="store_true",
        help="Post to all configured subreddits (use with caution)",
    )
    
    args = parser.parse_args()
    
    version = args.version or get_current_version()
    print(f"📢 Announcing Alex v{version}")
    print(f"   Dry run: {args.dry_run}")
    print()
    
    results = {}
    
    # Reddit
    if args.platform in ["reddit", "all"]:
        reddit = RedditPublisher()
        if args.all_subreddits:
            subreddits = ["vscode", "github", "programming", "artificial", "ChatGPT"]
            for sub in subreddits:
                results[f"reddit/{sub}"] = reddit.post(sub, version, args.dry_run)
        else:
            results["reddit"] = reddit.post(args.subreddit, version, args.dry_run)
    
    # Twitter
    if args.platform in ["twitter", "all"]:
        twitter = TwitterPublisher()
        results["twitter"] = twitter.post_thread(version, args.dry_run)
    
    # Dev.to
    if args.platform in ["devto", "all"]:
        devto = DevToPublisher()
        results["devto"] = devto.post(version, args.dry_run)
    
    # Discord
    if args.platform in ["discord", "all"]:
        discord = DiscordPublisher()
        results["discord"] = discord.post(version, args.dry_run)
    
    # LinkedIn
    if args.platform in ["linkedin", "all"]:
        linkedin = LinkedInPublisher()
        results["linkedin"] = linkedin.post(version, args.dry_run)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Summary")
    print("=" * 50)
    for platform, result in results.items():
        status = "✅" if result else "❌"
        print(f"  {status} {platform}")
    
    if args.dry_run:
        print("\n⚠️ This was a dry run. No posts were actually made.")
        print("   Remove --dry-run to post for real.")


if __name__ == "__main__":
    main()

