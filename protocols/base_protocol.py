import time
from abc import abstractmethod

from cli import MAX_SEGMENT_SIZE
from metrics_collector import MetricsCollector
from packet import Packet
from rdt_session import RDTSession


class BaseProtocol:
    MAX_RETRIES = 5

    def __init__(self, session: RDTSession, window_size: int, name: str) -> None:
        self.session = session
        self.file_buffer: list[bytes] = []
        self.window_size: int = window_size
        self.name = name
        self.progress: int = 0
        self.total_download_time: float = 0.0
        self.metrics_collector: MetricsCollector | None = None

    def _connect(self, group: str, segment_size: int, file_type: str) -> int:
        ok_pkt = self.session.connect(group, segment_size, file_type)
        if not ok_pkt:
            return 0

        total = ok_pkt.total_segments
        self.file_buffer = [b""] * total
        self.metrics_collector = MetricsCollector(total, self.window_size, self.name)
        return total

    def finalize_transfer(self, md5: str) -> bool:
        for _ in range(self.MAX_RETRIES):
            self.session.send_fin(md5)
            try:
                done = self.session.receive_packet()

                if done.type == "DONE" and done.get("ok") == 1:
                    return True
            except TimeoutError:
                continue

        return False

    def _get_next_segment(self, seq: int) -> Packet:
        while True:
            seg: Packet = self.session.receive_packet()

            # retorna apenas se é de fato um pacote de dados.
            # se não, limpa o buffer até encontrar ou timeout()
            if seg.type == "DATA" and seg.seq == seq:
                return seg

    def get_content(self):
        return b"".join(self.file_buffer)

    @abstractmethod
    def run(self, group: str, segment_size: int, file_type: str):
        raise NotImplementedError
