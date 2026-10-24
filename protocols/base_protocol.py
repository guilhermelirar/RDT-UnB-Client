from abc import abstractmethod
import time
from rdt_session import RDTSession
from packet import Packet

class BaseProtocol:
    MAX_RETRIES = 5

    def __init__(self, session: RDTSession, 
                 window_size: int, name: str) -> None:
        self.session = session
        self.metrics = []
        self.file_buffer = []
        self.expectedmd5: str = ""
        self.window_size: int = window_size
        self.name = name
        self.progress: int = 0

    def collect_metrics(
        self,
        seq: int,
        timestamp: str,
        rtt_ms: float,
        payload_size: int,
        retries: int,
    ):
        throughput_kbps = payload_size * 8.0 / rtt_ms

        self.metrics.append(
            {
                "segment": seq,
                "timestamp": timestamp,
                "size_bytes": payload_size,
                "rtt_ms": rtt_ms,
                "timeout_ms": self.session.timeout * 1000.0,
                "throughput_kbps": throughput_kbps,
                "retransmissions": retries,
                "timeout_ocurred": 0 if retries == 0 else 1,
                "window_size": self.window_size,
                "protocol": self.name,
            }
        )

    def _connect(self, group: str, segment_size: int, file_type: str) -> int:
        ok_pkt = self.session.connect(group, segment_size, file_type)

        if not ok_pkt:
            print("Conexão não pode ser estabelecida...")
            return 0

        print(ok_pkt)
        self.expectedmd5 = str(ok_pkt.get("checksum"))

        total = ok_pkt.get("total_segments")
        if not (isinstance(total, int) and total > 0):
            print("Não há segmentos para obter...")
            return 0

        self.file_buffer = [b""] * total
        return total

    def _get_next_segment(self, seq: int) -> Packet:
        while True:
            seg: Packet = self.session.receive_packet()

            # retorna apenas se é de fato um pacote de dados.
            # se não, limpa o buffer até encontrar ou timeout()
            if seg.type == "DATA" and seg.seq == seq:
                return seg

    def log_progress(self, seq: int, 
                     total_segments: int, 
                     start_time: float,
                     total_retries: int):
        
        if total_segments <= 0:
            return

        pct_int = (seq * 100) // total_segments
        is_last = (seq == total_segments)

        if pct_int == self.progress and not is_last:
            return

        self.progress = pct_int

        elapsed = max(0.0001, time.perf_counter() - start_time)
        percent_float = (seq / total_segments) * 100

        throughput_kbps = (8 * 512 * seq) / (elapsed * 1000.0)

        print(
            f"\r[{self.name.upper()} | Win {self.window_size}] "
            f"Progress: {percent_float:5.1f}% ({throughput_kbps:8.2f} kbps) "
            f"| Retries: {total_retries}",
            end="",
            flush=True
        )

        if is_last:
            print()

    @abstractmethod
    def run(self, group: str, segment_size: int, file_type: str):
        raise NotImplemented

