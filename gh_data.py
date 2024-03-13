import json
import requests
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# GitHub GraphQL endpoint
url = 'https://api.github.com/graphql'

# Personal access token (Replace with your token)
token = '<YOUR_TOKEN>'

# GitHub organization name (Replace with your organization)
organization = '<YOUR_ORGANIZATION>'

# GitHub username (Replace with your username)
username = '<YOUR_USERNAME>'

# Output JSON file name for actions information
output_actions_json_file = 'actions_info.json'

# Output JSON file name for summary report
output_summary_json_file = 'summary_report.json'

# GraphQL query to fetch all repositories in the organization
query_repos = gql('''
    query {
        organization(login: "%s") {
            repositories(first: 100) {
                nodes {
                    name
                    workflows(first: 100) {
                        nodes {
                            name
                            path
                            workflowRuns(first: 1, orderBy: {field: CREATED_AT, direction: DESC}) {
                                nodes {
                                    workflowSteps(first: 100) {
                                        nodes {
                                            name
                                            uses
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
''' % organization)

# Set up GraphQL client
transport = RequestsHTTPTransport(
    url=url,
    headers={'Authorization': 'Bearer %s' % token},
    use_json=True
)

client = Client(transport=transport, fetch_schema_from_transport=True)

# Execute the query
result = client.execute(query_repos)

# Organize actions information
actions_info = {}

for repo in result['organization']['repositories']['nodes']:
    for workflow in repo['workflows']['nodes']:
        for run in workflow['workflowRuns']['nodes']:
            for step in run['workflowSteps']['nodes']:
                action_info = {
                    'workflow': workflow['name'],
                    'workflow_path': workflow['path'],
                    'step_name': step['name'],
                    'uses': step['uses']
                }

                repo_name = repo['name']
                if repo_name not in actions_info:
                    actions_info[repo_name] = []

                actions_info[repo_name].append(action_info)

# Write actions information to JSON file
with open(output_actions_json_file, 'w') as json_file:
    json.dump(actions_info, json_file, indent=2)

print(f"Actions info has been written to: {output_actions_json_file}")

# Generate summary report
summary_report = []

for repo_name, actions in actions_info.items():
    repo_report = {'repository': repo_name, 'workflows': []}
    for action in actions:
        workflow_info = {
            'workflow': action['workflow'],
            'workflow_path': action['workflow_path'],
            'step_name': action['step_name'],
            'uses': action['uses']
        }
        repo_report['workflows'].append(workflow_info)

    summary_report.append(repo_report)

# Write summary report to JSON file
with open(output_summary_json_file, 'w') as json_file:
    json.dump(summary_report, json_file, indent=2)

print(f"Summary report has been written to: {output_summary_json_file}")
