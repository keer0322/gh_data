import requests
import json
import time

# Set your GitHub organization name
ORG_NAME = "your-organization-name"
GITHUB_TOKEN = "your-github-token"  # Generate from https://github.com/settings/tokens
OUTPUT_FILE = "repos.json"

# GitHub API URL for listing repositories
BASE_URL = f"https://api.github.com/orgs/{ORG_NAME}/repos"

# Headers with authentication token
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def fetch_repos():
    """Fetch all repositories along with their last updated date from a GitHub organization."""
    repos = []
    page = 1
    per_page = 100  # Maximum per request

    while True:
        print(f"Fetching page {page}...")
        params = {"per_page": per_page, "page": page, "sort": "updated"}
        response = requests.get(BASE_URL, headers=HEADERS, params=params)

        if response.status_code != 200:
            print(f"❌ Error: {response.status_code} - {response.json().get('message')}")
            break

        data = response.json()
        if not data:
            break  # No more repositories to fetch

        # Extract repo name and last updated date
        for repo in data:
            repos.append({
                "name": repo["name"],
                "updated_at": repo["updated_at"]
            })

        # Pagination handling
        page += 1
        time.sleep(1)  # Avoid rate limiting

        # Stop if we've reached 6000 repositories
        if len(repos) >= 6000:
            break

    # Save to file
    with open(OUTPUT_FILE, "w") as f:
        json.dump(repos, f, indent=4)

    print(f"✅ Successfully fetched {len(repos)} repositories. Data saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    fetch_repos()
