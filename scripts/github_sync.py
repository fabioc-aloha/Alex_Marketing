# GitHub API URLs for fetching from main extension repo
EXTENSION_REPO = "fabioc-aloha/Alex_Plug_In"
PACKAGE_JSON_URL = f"https://raw.githubusercontent.com/{EXTENSION_REPO}/main/package.json"
CHANGELOG_URL = f"https://raw.githubusercontent.com/{EXTENSION_REPO}/main/CHANGELOG.md"

# =============================================================================
# GITHUB SYNC - Fetch info from extension repo
# =============================================================================

def fetch_extension_version() -> str:
    """Fetch current version from extension repo's package.json."""
    try:
        response = requests.get(PACKAGE_JSON_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("version", "0.0.0")
    except Exception as e:
        print(f"⚠️ Could not fetch version from GitHub: {e}")
        return "0.0.0"


def fetch_changelog() -> str:
    """Fetch changelog from extension repo."""
    try:
        response = requests.get(CHANGELOG_URL, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"⚠️ Could not fetch changelog from GitHub: {e}")
        return ""


def get_latest_changes(changelog: str) -> str:
    """Extract the latest version's changes from changelog."""
    if not changelog:
        return ""
    
    lines = changelog.split("\n")
    in_latest = False
    changes = []
    
    for line in lines:
        if line.startswith("## [") and not in_latest:
            in_latest = True
            continue
        elif line.startswith("## [") and in_latest:
            break
        elif in_latest:
            changes.append(line)
    
    return "\n".join(changes).strip()
