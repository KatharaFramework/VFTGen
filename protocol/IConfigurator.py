from abc import ABC, abstractmethod

from model.node_types.Server import Server


class IConfigurator(ABC):
    def configure(self, lab, topology):
        for pod_name, pod in topology.pods.items():
            for node_name, node in pod.items():
                if type(node) != Server:
                    self._configure_node(lab, node)

        for node_name, node in topology.aggregation_layer.items():
            self._configure_node(lab, node)

    @abstractmethod
    def _configure_node(self, lab, node):
        raise NotImplementedError("You must implement `_configure_node` method.")
