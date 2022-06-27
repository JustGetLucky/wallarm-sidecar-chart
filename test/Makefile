KUBE_CLUSTER_NAME=wallarm-sidecar-chart
KUBE_CONTEXT=kind-$(KUBE_CLUSTER_NAME)

all: lint create_cluster install_chart run_test delete_cluster

lint:
	helm lint ../. --debug

create_cluster:
	@kind create cluster --name $(KUBE_CLUSTER_NAME) --config kind/kind.yaml -v 1

install_chart:
	@helm install wallarm-sidecar ../. -f ../test-values.yaml --kube-context $(KUBE_CONTEXT) --namespace wallarm-sidecar --create-namespace --wait

run_test:
	@pytest --kube_context $(KUBE_CONTEXT)

upgrade_chart:
	@helm upgrade wallarm-sidecar ../. -f ../test-values.yaml --kube-context $(KUBE_CONTEXT) --namespace wallarm-sidecar --wait

delete_cluster:
	@kind delete cluster --name $(KUBE_CLUSTER_NAME)

.PHONY: create_cluster install_chart run_test upgrade_chart delete_cluster lint