import os
import xml.etree.ElementTree as ET

# Load the JUnit XML file
test_report_file = 'test-results.xml'  # Adjust this path if needed
tree = ET.parse(test_report_file)
root = tree.getroot()

# Extract failures
failure_summary = "### Unit Test Failures:\n\n"
failures_found = False

for testcase in root.iter("testcase"):
    for failure in testcase.iter("failure"):
        failures_found = True
        test_name = testcase.get("name")
        classname = testcase.get("classname")
        message = failure.get("message", "No message")
        failure_summary += f"- **{classname}.{test_name}**: {message}\n"

# Check if there are any failures
if not failures_found:
    failure_summary += "All tests passed successfully."

# Truncate the summary if it’s too long
if len(failure_summary) > 65536:  # GitHub has a 65,536 character limit for comments
    failure_summary = failure_summary[:65500] + "\n... Output truncated due to length ..."

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
    'body': failure_summary
}

response = requests.post(url, headers=headers, json=data)

if response.status_code == 201:
    print("Comment posted successfully.")
else:
    print(f"Failed to post comment: {response.status_code}")
