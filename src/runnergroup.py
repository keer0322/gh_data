import requests

# ---- CONFIG ----
GITHUB_TOKEN = "ghp_XXX"  # Replace with your token
ORG = "your-org"
REPO = "your-repo"
RUNNER_GROUP_ID = 123456  # Replace with your runner group ID

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}


def get_runner_ids_in_group(org, group_id):
    url = f"https://api.github.com/orgs/{org}/actions/runner-groups/{group_id}/runners"
    runner_ids = set()

    while url:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()

        for runner in data.get("runners", []):
            runner_ids.add(runner["id"])

        url = response.links.get("next", {}).get("url")

    return runner_ids


def get_workflow_runs(org, repo):
    url = f"https://api.github.com/repos/{org}/{repo}/actions/runs"
    runs = []

    while url:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()

        runs.extend(data.get("workflow_runs", []))
        url = response.links.get("next", {}).get("url")

    return [run["id"] for run in runs]


def get_jobs_for_run(org, repo, run_id):
    url = f"https://api.github.com/repos/{org}/{repo}/actions/runs/{run_id}/jobs"
    jobs = []

    while url:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()

        jobs.extend(data.get("jobs", []))
        url = response.links.get("next", {}).get("url")

    return jobs


def main():
    print("Fetching runners in group...")
    group_runner_ids = get_runner_ids_in_group(ORG, RUNNER_GROUP_ID)
    print(f"Found {len(group_runner_ids)} runners in group.")

    print("Fetching workflow runs...")
    run_ids = get_workflow_runs(ORG, REPO)
    print(f"Found {len(run_ids)} runs.")

    matched_jobs = []

    for run_id in run_ids:
        print(f"Checking jobs in run: {run_id}")
        jobs = get_jobs_for_run(ORG, REPO, run_id)

        for job in jobs:
            runner_id = job.get("runner_id")
            if runner_id in group_runner_ids:
                matched_jobs.append({
                    "run_id": run_id,
                    "job_id": job["id"],
                    "job_name": job["name"],
                    "runner_id": runner_id,
                    "runner_name": job.get("runner_name"),
                    "status": job["status"],
                    "conclusion": job["conclusion"]
                })

    print(f"\nMatched {len(matched_jobs)} jobs run on runners in group:")
    for job in matched_jobs:
        print(job)


if __name__ == "__main__":
    main()
