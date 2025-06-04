# Migration Checklist: ARC v0.6.1 → v0.11.1

## ✅ Pre-Migration Prep
- [ ] **Review Changelog**: Check [ARC Release Notes](https://github.com/actions/actions-runner-controller/releases)
- [ ] **Backup Existing Setup**:
  - Export current `values.yaml`
  - Backup secrets, GitHub App keys, cluster configs
- [ ] **Ensure Helm v3+** is installed
- [ ] **Verify cluster access and namespace permissions**

## 🛠 Update Helm Chart Components
- [ ] Update Helm repo:
  ```bash
  helm repo add actions-runner-controller https://actions-runner-controller.github.io/actions-runner-controller
  helm repo update
  ```
- [ ] Split controller, listener, and runner scale set:
  - `gha-runner-scale-set-controller`
  - `gha-runner-scale-set-listener`
  - `gha-runner-scale-set`
- [ ] Update `values.yaml` for each component

## 🔐 Migrate to GitHub App Authentication
- [ ] Register GitHub App and capture:
  - App ID
  - Client ID
  - Installation ID
  - Private key (PEM)
- [ ] Create Kubernetes Secret:
  ```bash
  kubectl create secret generic controller-manager \
    --from-file=github_app_private_key=<key.pem> \
    --from-literal=github_app_id=<id> \
    --from-literal=github_app_installation_id=<id> \
    --from-literal=github_app_client_id=<id>
  ```

## 🚀 Enable New Features (Optional)
- [ ] Enable Container Mode:
  ```yaml
  containerMode:
    enabled: true
  ```
- [ ] Enable Prometheus Metrics:
  ```yaml
  metrics:
    enabled: true
    serviceMonitor:
      enabled: true
  ```

## ⚙️ Configure Autoscaling
- [ ] Choose between Kubernetes HPA or KEDA
- [ ] Configure scale values in runner set:
  ```yaml
  minReplicas: 1
  maxReplicas: 10
  scaleDownDelaySeconds: 30
  ```

## 🔍 Post-Migration Validation
- [ ] Verify pods: controller, listener, runners
- [ ] Check Prometheus and logs
- [ ] Trigger GitHub workflows and validate full flow
- [ ] Confirm autoscaling is functioning

## 🧪 Test in Staging
- [ ] Deploy in test cluster
- [ ] Validate workflows and container isolation
- [ ] Monitor scale events and performance

## 🚨 Cleanup
- [ ] Remove old v0.6.1 deployments
- [ ] Archive outdated Helm releases
- [ ] Clean unused secrets or service accounts
