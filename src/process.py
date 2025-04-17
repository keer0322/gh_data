def flatten_workflow_run(event):
    wr = event.get("workflow_run", {})
    repo = event.get("repository", {})
    sender = event.get("sender", {})

    return {
        "event_type": "workflow_run",
        "run_id": wr.get("id"),
        "run_number": wr.get("run_number"),
        "name": wr.get("name"),
        "branch": wr.get("head_branch"),
        "status": wr.get("status"),
        "conclusion": wr.get("conclusion"),
        "created_at": wr.get("created_at"),
        "updated_at": wr.get("updated_at"),
        "duration_sec": _calculate_duration(wr.get("created_at"), wr.get("updated_at")),
        "run_attempt": wr.get("run_attempt"),
        "url": wr.get("html_url"),
        "repo": repo.get("full_name"),
        "triggered_by": sender.get("login"),
    }

def flatten_workflow_job(event):
    wj = event.get("workflow_job", {})
    repo = event.get("repository", {})

    return {
        "event_type": "workflow_job",
        "job_id": wj.get("id"),
        "run_id": wj.get("run_id"),
        "name": wj.get("name"),
        "status": wj.get("status"),
        "conclusion": wj.get("conclusion"),
        "started_at": wj.get("started_at"),
        "completed_at": wj.get("completed_at"),
        "duration_sec": _calculate_duration(wj.get("started_at"), wj.get("completed_at")),
        "runner": wj.get("runner_name"),
        "runner_group": wj.get("runner_group_name"),
        "repo": repo.get("full_name"),
    }


from datetime import datetime

def _calculate_duration(start, end):
    if not start or not end:
        return None
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    return int((datetime.strptime(end, fmt) - datetime.strptime(start, fmt)).total_seconds())

def flatten_check_run(event):
    cr = event.get("check_run", {})
    repo = event.get("repository", {})
    sender = event.get("sender", {})

    return {
        "event_type": "check_run",
        "check_run_id": cr.get("id"),
        "name": cr.get("name"),
        "status": cr.get("status"),
        "conclusion": cr.get("conclusion"),
        "started_at": cr.get("started_at"),
        "completed_at": cr.get("completed_at"),
        "duration_sec": _calculate_duration(cr.get("started_at"), cr.get("completed_at")),
        "external_id": cr.get("external_id"),
        "url": cr.get("html_url"),
        "repo": repo.get("full_name"),
        "triggered_by": sender.get("login"),
    }

def flatten_check_suite(event):
    cs = event.get("check_suite", {})
    repo = event.get("repository", {})
    sender = event.get("sender", {})

    return {
        "event_type": "check_suite",
        "check_suite_id": cs.get("id"),
        "status": cs.get("status"),
        "conclusion": cs.get("conclusion"),
        "created_at": cs.get("created_at"),
        "updated_at": cs.get("updated_at"),
        "duration_sec": _calculate_duration(cs.get("created_at"), cs.get("updated_at")),
        "branch": cs.get("head_branch"),
        "commit_sha": cs.get("head_sha"),
        "url": cs.get("url"),
        "repo": repo.get("full_name"),
        "triggered_by": sender.get("login"),
    }

