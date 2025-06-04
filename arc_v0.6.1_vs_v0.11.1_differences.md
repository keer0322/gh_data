# Detailed Comparison: ARC v0.6.1 vs v0.11.1

This document outlines the key architectural and functional differences between Actions Runner Controller (ARC) versions **v0.6.1** and **v0.11.1**.

---

## 📌 Summary Table

| Feature                         | v0.6.1                         | v0.11.1                              |
|---------------------------------|--------------------------------|--------------------------------------|
| **Listener Pod**                | ❌ Bundled with controller     | ✅ Dedicated `gha-runner-scale-set-listener` pod |
| **GitHub App Authentication**   | ⚠️ Optional, less robust      | ✅ Native and recommended method     |
| **Container Mode Support**      | ❌ Not supported               | ✅ Optional per-job container mode   |
| **Autoscaling**                 | Basic Kubernetes HPA           | ✅ Advanced autoscaling (KEDA & HPA) |
| **Prometheus Metrics**          | ⚠️ Limited, custom setup       | ✅ Built-in metrics endpoints        |
| **Helm Chart Design**           | Monolithic                     | ✅ Modular (controller, listener, runners) |
| **Webhooks Handling**           | Manual or limited              | ✅ Listener handles GitHub webhooks  |
| **Runner Lifecycle Management** | Basic                          | ✅ Enhanced (graceful shutdown, draining) |
| **Scaling Events**              | Less dynamic                   | ✅ Reactive to webhook/job events    |

---

## 🧱 Architectural Changes

### v0.6.1
- Single controller manages both GitHub webhook and runner orchestration.
- Limited observability and scaling responsiveness.
- No support for container-based runner isolation.
- GitHub App tokens and registration handled manually.

### v0.11.1
- **Decoupled architecture**: `controller`, `listener`, and `runner scale set` are separate Kubernetes workloads.
- Webhooks from GitHub go to the `listener`, which signals the controller to scale up runners.
- **Metrics exposed** via Prometheus for controller, listener, and runners.
- Optional **containerMode** runs each job in a sandboxed container, not a long-lived runner pod.

---

## 🚀 Functional Improvements

| Area            | v0.6.1                        | v0.11.1                                           |
|-----------------|-------------------------------|--------------------------------------------------|
| Runner Startup  | Manual, slow                  | Scaled via webhook triggers                      |
| Job Isolation   | Not supported                 | Container mode isolates each job                 |
| Metrics         | Requires manual config        | Available out-of-the-box                         |
| Token Handling  | Static or manually rotated    | Uses GitHub App token automation                 |
| CI/CD Flexibility| Limited templates            | Helm charts support deep customization           |

---

## 🔐 Security & GitHub Integration

- v0.6.1 relied on **PAT (Personal Access Tokens)** or GitHub App with less flexible setup.
- v0.11.1 **fully supports GitHub App** registration and token management via secrets.

---

## 📈 Autoscaling Enhancements

- v0.6.1 used Kubernetes HPA based on CPU/memory metrics.
- v0.11.1 introduces **event-driven autoscaling** using:
  - **KEDA** (based on queue length, GitHub events)
  - **Webhook signal scaling** based on active job count

---

## 📂 Helm Chart Restructuring

| Component                      | v0.6.1                         | v0.11.1                            |
|-------------------------------|--------------------------------|------------------------------------|
| `gha-runner-scale-set`        | ✅ Yes                         | ✅ Yes                              |
| `gha-runner-scale-set-controller` | ✅ Yes                     | ✅ Yes (modularized)                |
| `gha-runner-scale-set-listener`  | ❌ No                        | ✅ New deployment                   |
| Value file complexity          | Medium                         | Higher, but more configurable      |

---

## ✅ Conclusion

ARC v0.11.1 provides significant improvements in **scalability**, **security**, **observability**, and **flexibility** over v0.6.1. The transition is highly recommended for production-grade CI/CD environments using GitHub Actions with Kubernetes-based runners.

