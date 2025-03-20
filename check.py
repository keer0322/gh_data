import requests
import json
import time

# GitHub personal access token (Ensure it has 'repo' and 'read:org' permissions)
GITHUB_TOKEN = "your_github_token_here"

# Headers for authentication
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v4+json"
}

# List of organizations and search strings
org_list = ["new_org", "old_org"]
search_strings = ["tj-actions/", "reviewdog/"]
result_file = "result_file.txt"

# GitHub GraphQL API Endpoint
GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"

def run_graphql_query(query, variables):
    """Executes a GraphQL query and returns the response."""
    response = requests.post(GITHUB_GRAPHQL_URL, json={"query": query, "variables": variables}, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

# GraphQL Query Template with Pagination Support
QUERY_TEMPLATE = """
query($queryString: String!, $first: Int!, $after: String) {
  search(query: $queryString, type: CODE, first: $first, after: $after) {
    pageInfo {
      hasNextPage
      endCursor
    }
    edges {
      node {
        ... on Code {
          repository {
            nameWithOwner
            url
          }
          path
        }
      }
    }
  }
}
"""

# Clear the results file
with open(result_file, "w") as f:
    f.write("")

# Iterate through search terms and organizations
for search_string in search_strings:
    print(f"🔍 Searching for: {search_string}")
    for org in org_list:
        print(f"📂 Searching in organization: {org}")
        
        search_results = []
        after_cursor = None  # Cursor for pagination

        while True:
            # Define search query string
            query_string = f'org:{org} "{search_string}" language:yaml'

            # Run the query
            variables = {"queryString": query_string, "first": 100, "after": after_cursor}
            data = run_graphql_query(QUERY_TEMPLATE, variables)

            if not data or "data" not in data:
                print(f"⚠️ Skipping {org} due to an error.")
                break
            
            # Process search results
            edges = data["data"]["search"]["edges"]
            for edge in edges:
                node = edge["node"]
                repo_name = node["repository"]["nameWithOwner"]
                repo_url = node["repository"]["url"]
                file_path = node["path"]

                search_results.append({
                    "repo": repo_name,
                    "repo_url": repo_url,
                    "path": file_path
                })

            # Pagination handling
            page_info = data["data"]["search"]["pageInfo"]
            if page_info["hasNextPage"]:
                after_cursor = page_info["endCursor"]
                time.sleep(1)  # Avoid hitting GitHub rate limits
            else:
                break

        # Save results to file
        with open(result_file, "a") as f:
            f.write(f"{org}: {json.dumps(search_results, indent=2)}\n")

        print(f"✅ Completed search for {org}, found {len(search_results)} results.\n")

print(f"🎯 Results saved in {result_file}")
