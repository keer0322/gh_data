import os
import re

# Read the Gradle lint output
with open('lint-output.txt', 'r') as f:
    lines = f.readlines()

# Filter for failure or warning lines
failure_lines = []
capture = False
for line in lines:
    # Identify sections where lint errors are described
    if "Lint rule violations were found" in line or "warning" in line.lower() or "error" in line.lower():
        capture = True
    elif capture and line.strip() == "":  # Stop capturing at blank lines after the issues
        capture = False
    
    # Capture only relevant lines during error section
    if capture:
        failure_lines.append(line.strip())

# Format the output as an HTML preformatted block for the PR comment
comment_body = "### Gradle Lint Failures:\n\n"
if failure_lines:
    comment_body += "<pre>\n" + "\n".join(failure_lines) + "\n</pre>"
else:
    comment_body += "No lint failures found."

# Truncate the comment if it’s too long
if len(comment_body) > 65536:  # GitHub has a 65536 character limit
    comment_body = comment_body[:65500] + "\n... Output truncated due to length ..."

# Post to the Pull Request (via GitHub API)
import requests

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
REPO = os.getenv('GITHUB_REPO')
PR_NUMBER = os.getenv('PR_NUMBER')

url = f"https://api.github.com/repos/{REPO}/issues/{PR_NUMBER}/comments"
headers = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Content-Type': 'application/json'
}
data = {
    'body': comment_body
}

response = requests.post(url, headers=headers, json=data)

if response.status_code == 201:
    print("Comment posted successfully.")
else:
    print(f"Failed to post comment: {response.status_code}")
