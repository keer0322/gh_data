# GitHub Actions Runner Controller (ARC) - Component Overview

This document explains the core components of the [Actions Runner Controller (ARC)](https://github.com/actions/actions-runner-controller), which enables scalable, Kubernetes-native GitHub Actions self-hosted runners.

---

## 🧠 Component Summary

| Component  | Purpose                                   | Runs As                      |
|------------|-------------------------------------------|------------------------------|
| **Controller** | Manages lifecycle of runner pods         | Kubernetes Deployment (Pod)  |
| **Listener**   | Listens for GitHub workflow job events  | Kubernetes Deployment (Pod)  |
| **Runner**     | Executes the actual GitHub Action jobs  | Kubernetes Pod (ephemeral)   |

---

## 📦 gha-runner-scale-set-controller (Controller)

### 🔍 Description
The controller is the central orchestrator. It is a Kubernetes operator responsible for managing the lifecycle of runner pods based on job events and scaling configuration.

### 🔧 Key Responsibilities
- Watches custom resources (e.g., `RunnerDeployment`, `RunnerReplicaSet`, `RunnerScaleSet`)
- Provisions and deletes runner pods based on demand
- Registers runner pods with GitHub using GitHub App tokens
- Performs health checks and status reconciliation
- Exposes Prometheus metrics (runners registered, errors, queue depth, etc.)

### 🔗 Flow
1. Receives CRD events from listener or autoscaler
2. Creates or deletes runner pods
3. Registers runners with GitHub
4. Deletes runner pods post job execution

---

## 🛰️ gha-runner-scale-set-listener (Listener)

### 🔍 Description
The listener monitors GitHub for incoming workflow job events. It detects pending jobs for a given scale set and informs the controller to scale runners accordingly.

### 🔧 Key Responsibilities
- Polls GitHub for queued workflow jobs
- Filters jobs by runner group/scale set labels
- Notifies controller to scale up runners
- Implements backoff, retry, and error handling
- Exposes Prometheus metrics for queue depth, polling intervals, etc.

### 🔗 Flow
1. Connects to GitHub using GitHub App credentials
2. Detects pending jobs for runner scale sets
3. Sends scaling signals to the controller
4. Helps enable event-driven autoscaling

---

## ⚙️ gha-runner-scale-set (Runner Pods)

### 🔍 Description
Runner pods are the actual ephemeral workloads that execute GitHub Actions jobs. Each pod is registered as a GitHub runner and terminated after job completion.

### 🔧 Key Responsibilities
- Connects to GitHub runner API and polls for a job
- Downloads and executes job steps (actions)
- Logs job output to GitHub
- Terminates after job finishes (in ephemeral mode)

### 🔗 Flow
1. Spawned by the controller
2. Registers with GitHub
3. Executes assigned job
4. Shuts down and is deleted

---

## 🧬 Example Lifecycle

```text
[ GitHub Workflow Dispatch ]
          ↓
    [ Listener Pod ]
          ↓
Sends CR update to Controller
          ↓
[ Controller ] creates runner pod
          ↓
[ Runner Pod ] registers with GitHub
          ↓
Executes job → Shuts down
```

---

## 📊 Metrics Overview

| Component  | Metrics Scope                           |
|------------|-----------------------------------------|
| Controller | Runner lifecycle, job errors, states    |
| Listener   | Polling frequency, job queue depth      |
| Runner     | Job execution duration, failures        |

---

## 🛡️ Security & Auth

- Uses **GitHub App** for secure runner registration and event polling
- Secrets are stored in Kubernetes Secrets and mounted into pods
- Supports fine-grained runner group scoping

---

## 📚 References

- GitHub ARC: https://github.com/actions/actions-runner-controller
- GitHub Actions Docs: https://docs.github.com/actions
- Prometheus Integration: https://github.com/actions/actions-runner-controller/tree/main/docs/metrics

