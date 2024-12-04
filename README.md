## Prerequisites

- Minikube cluster
- [Helm](https://helm.sh/) installed and configured
- `kubectl` installed and configured
- Bitnami Helm repository:
- Custom `values.yaml`
- SealedSecret 
- Grafana Loki

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
```