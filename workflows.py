from github import Github
import requests
import yaml
import os

# Set your GitHub personal access token and organization name
GITHUB_TOKEN = "your_github_token"
ORG_NAME = "your_org_name"

# Initialize GitHub API client
g = Github(GITHUB_TOKEN)

def get_workflow_files(repo):
    """Fetches workflow files from a repository."""
    try:
        contents = repo.get_contents(".github/workflows")
        return [file for file in contents if file.name.endswith(".yml") or file.name.endswith(".yaml")]
    except Exception:
        return []  # No workflows found

def extract_actions_from_yaml(yaml_content):
    """Parses a workflow YAML file to extract GitHub Actions used."""
    actions = set()
    try:
        workflow = yaml.safe_load(yaml_content)
        jobs = workflow.get("jobs", {})
        for job in jobs.values():
            steps = job.get("steps", [])
            for step in steps:
                if isinstance(step, dict) and "uses" in step:
                    actions.add(step["uses"])
    except yaml.YAMLError:
        pass  # Ignore YAML parsing errors
    return actions

def get_actions_in_repo(repo):
    """Gets all actions used in a given repository."""
    actions = set()
    workflow_files = get_workflow_files(repo)
    
    for file in workflow_files:
        file_content = repo.get_contents(file.path).decoded_content.decode("utf-8")
        actions.update(extract_actions_from_yaml(file_content))
    
    return actions

def get_all_actions_in_org():
    """Fetches all actions used across all repositories in an organization."""
    actions_set = set()
    org = g.get_organization(ORG_NAME)
    
    for repo in org.get_repos():
        print(f"Checking {repo.full_name}...")
        repo_actions = get_actions_in_repo(repo)
        actions_set.update(repo_actions)
    
    return actions_set

if __name__ == "__main__":
    actions = get_all_actions_in_org()
    print("\nAll Actions Used in Organization:")
    for action in sorted(actions):
        print(action)
