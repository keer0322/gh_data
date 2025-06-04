# Pain Points of Actions Runner Controller (ARC) v0.6.1

This document outlines the major limitations and pain points experienced when using ARC version 0.6.1.

---

## 🚧 Key Pain Points

### 1. 🧱 Monolithic Architecture
- Listener functionality is bundled with the controller.
- No separation of concerns between job detection and runner orchestration.
- Difficult to scale components independently.

### 2. 🚫 No Container Mode Support
- Jobs run in persistent Kubernetes pods, not ephemeral containers.
- Leads to:
  - Slower runner spin-up times
  - Higher resource usage
  - Increased complexity for security hardening

### 3. 🔍 Limited Observability & Metrics
- Minimal built-in Prometheus metrics.
- Missing metrics:
  - Job queue depth
  - Runner status transitions
  - Job duration
- Hinders proactive monitoring and autoscaling.

### 4. 🔐 Manual Token Management
- Uses PAT (Personal Access Token) by default.
- Lacks secure GitHub App integration for automated token handling.
- Token rotation and security are manual and error-prone.

### 5. ⚙️ Basic Autoscaling
- Uses Kubernetes HPA based on CPU/memory usage.
- No support for event-driven scaling based on GitHub job activity.
- Slow to react to spikes in job demand.

### 6. 🧪 Inefficient Runner Lifecycle Management
- No graceful shutdown for runners during scale-down.
- Risk of terminating runners mid-job.
- Potential for zombie runners to remain registered with GitHub.

### 7. 📂 Tight-Coupled Helm Chart Structure
- Single chart bundles controller, CRDs, and runner logic.
- Lacks modularity and flexibility.
- Makes upgrades and customizations more complex.

### 8. 💥 Workflow Failures Under Load
- Without advanced scaling, runners are unavailable during traffic spikes.
- Leads to job queuing, delays, and possible workflow timeouts.

### 9. 🔁 No Job Isolation
- Jobs share the same runner environment.
- Risks:
  - Cross-job contamination
  - Security and data leakage issues in shared clusters

### 10. 🧹 Manual Debugging and Cleanup
- No built-in garbage collection for dead or crashed runners.
- Log aggregation requires additional setup.

---

## 📌 Summary

ARC v0.6.1 served as a functional starting point for Kubernetes-based GitHub Actions runners, but its limitations in scalability, observability, and security make it unsuitable for modern production workloads. Upgrading to v0.11.1 or higher is highly recommended.

