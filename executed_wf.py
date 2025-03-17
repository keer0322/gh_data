from github import Github
import requests
import yaml

# Set your GitHub personal access token and organization name
GITHUB_TOKEN = "your_github_token"
ORG_NAME = "your_org_name"

# Initialize GitHub API client
g = Github(GITHUB_TOKEN)

HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}
GITHUB_API_BASE = "https://api.github.com"

def get_workflow_runs(repo):
    """Fetches all workflow runs for a given repository."""
    url = f"{GITHUB_API_BASE}/repos/{repo.full_name}/actions/runs"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("workflow_runs", [])
    return []

def get_workflow_yaml_from_run(run):
    """Fetches the workflow YAML file used in a specific workflow run."""
    url = run["workflow_url"]  # URL to the workflow definition
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        workflow_data = response.json()
        return workflow_data.get("path"), workflow_data.get("id")
    return None, None

def get_workflow_content(repo, workflow_id):
    """Fetches the YAML content of a workflow file by ID."""
    url = f"{GITHUB_API_BASE}/repos/{repo.full_name}/actions/workflows/{workflow_id}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        workflow_data = response.json()
        return repo.get_contents(workflow_data["path"]).decoded_content.decode("utf-8")
    return None

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

def get_all_actions_from_executed_workflows():
    """Gets actions used in executed workflows across all repositories."""
    actions_set = set()
    org = g.get_organization(ORG_NAME)
    
    for repo in org.get_repos():
        print(f"Checking {repo.full_name} for executed workflows...")
        workflow_runs = get_workflow_runs(repo)
        
        for run in workflow_runs:
            workflow_path, workflow_id = get_workflow_yaml_from_run(run)
            if workflow_path and workflow_id:
                workflow_content = get_workflow_content(repo, workflow_id)
                if workflow_content:
                    actions_set.update(extract_actions_from_yaml(workflow_content))
    
    return actions_set

if __name__ == "__main__":
    actions = get_all_actions_from_executed_workflows()
    print("\nAll Actions Used in Executed Workflows:")
    for action in sorted(actions):
        print(action)
