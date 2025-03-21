import requests
import csv
import time

# GitHub Enterprise Base URL (Modify this)
GITHUB_ENTERPRISE_URL = "https://your-github-enterprise.com"

# GitHub Admin Token (Must have 'admin:enterprise' permission)
GITHUB_TOKEN = "your_github_admin_token_here"

# Headers for API requests
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Output CSV file
OUTPUT_FILE = "user_emails.csv"

# Pagination settings
PER_PAGE = 100
PAGE = 1

# List to store user data
users_data = []

def fetch_users(page):
    """Fetch a page of users from GitHub Enterprise."""
    url = f"{GITHUB_ENTERPRISE_URL}/api/v3/admin/users?per_page={PER_PAGE}&page={page}"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching users: {e}")
        return []

print("🔍 Fetching users from GitHub Enterprise...")

while True:
    users = fetch_users(PAGE)
    
    # If no users are returned, stop pagination
    if not users:
        break
    
    # Process and store user data
    for user in users:
        username = user.get("login", "N/A")
        email = user.get("email", "No Email Available")  # Some emails may be private
        users_data.append([username, email])

    print(f"📄 Processed Page {PAGE}, Fetched {len(users)} users.")
    
    PAGE += 1
    time.sleep(1)  # Prevent rate limits

# Save results to CSV
with open(OUTPUT_FILE, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Username", "Email"])
    writer.writerows(users_data)

print(f"✅ User email list saved in {OUTPUT_FILE}")
