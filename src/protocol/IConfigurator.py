from abc import ABC, abstractmethod

from ..model.node_types.Server import Server


class IConfigurator(ABC):
    """
    Interface for Configurator objects
    """

    def configure(self, lab, topology):
        """
        write the protocol configurations for each node in topology
        :param lab: a Laboratory object (used to take information about the laboratory dir)
        :param topology: a FatTree object that represents a clos topology
        :return:
        """
        for pod_name, pod in topology.pods.items():
            for node_name, node in pod.items():
                if type(node) != Server:
                    self._configure_node(lab, node)

        for node_name, node in topology.aggregation_layer.items():
            self._configure_node(lab, node)

    @abstractmethod
    def _configure_node(self, lab, node):
        """
        abstract method, write the protocol configuration for the node
        :param lab: a Laboratory object (used to take information about the laboratory dir)
        :param node: a FatTree object that represents a clos topology
        :return:
        """
        raise NotImplementedError("You must implement `_configure_node` method.")
