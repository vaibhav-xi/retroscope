from abc import ABC, abstractmethod

from render_es2.render_packet import RenderPacket


class RenderPass(ABC):
    """
    Base class for every render pass.
    """

    @abstractmethod
    def execute(
        self,
        packet: RenderPacket,
    ) -> None:
        pass