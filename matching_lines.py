import requests
import json
import time

# GitHub personal access token (Ensure it has 'repo' and 'read:org' permissions)
GITHUB_TOKEN = "your_github_token_here"

# Headers for authentication
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3.text-match+json"  # Enables text matching
}

# List of organizations and search terms
org_list = ["new_org", "old_org"]
search_strings = ["tj-actions/", "reviewdog/"]
result_file = "result_file.txt"

# GitHub Search API URL
GITHUB_SEARCH_URL = "https://api.github.com/search/code"

def search_code(query, page=1):
    """Searches for code in GitHub using the REST API with pagination."""
    params = {
        "q": query,
        "per_page": 100,
        "page": page
    }
    
    try:
        response = requests.get(GITHUB_SEARCH_URL, headers=HEADERS, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

def fetch_file_content(file_url):
    """Fetches the raw content of a file from GitHub."""
    raw_url = file_url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
    
    try:
        response = requests.get(raw_url, headers=HEADERS)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Could not fetch file: {file_url} - {e}")
        return None

# Clear the results file before writing new results
with open(result_file, "w") as f:
    f.write("")

# Iterate through search terms and organizations
for search_string in search_strings:
    print(f"🔍 Searching for: {search_string}")
    
    for org in org_list:
        print(f"📂 Searching in organization: {org}")
        
        search_results = []
        page = 1

        while True:
            # Construct search query: 'org:<organization> "<search_string>" language:yaml'
            query = f'org:{org} "{search_string}" language:yaml'

            # Perform search request
            data = search_code(query, page)

            # Validate response
            if not data or "items" not in data:
                print(f"⚠️ No results or error occurred for {org}.")
                break
            
            # Process search results
            for item in data["items"]:
                repo_name = item["repository"]["full_name"]
                repo_url = item["repository"]["html_url"]
                file_path = item["path"]
                file_url = item["html_url"]

                # Try extracting matching lines from API (if available)
                if "text_matches" in item:
                    matching_lines = [match["fragment"] for match in item["text_matches"]]
                else:
                    # If text_matches is missing, fetch raw content and extract matches
                    file_content = fetch_file_content(file_url)
                    matching_lines = []
                    
                    if file_content:
                        for line in file_content.split("\n"):
                            if search_string in line:
                                matching_lines.append(line.strip())

                search_results.append({
                    "repo": repo_name,
                    "repo_url": repo_url,
                    "file_path": file_path,
                    "file_url": file_url,
                    "matching_lines": matching_lines
                })

            print(f"📄 Page {page}: Found {len(data['items'])} results.")

            # Check if we need to continue paginating
            if len(data["items"]) < 100:
                break  # Last page reached
            else:
                page += 1
                time.sleep(1)  # Prevent hitting GitHub rate limits

        # Save results to file
        with open(result_file, "a") as f:
            f.write(f"{org}: {json.dumps(search_results, indent=2)}\n")

        print(f"✅ Completed search for {org}, found {len(search_results)} results.\n")

print(f"🎯 Results saved in {result_file}")
