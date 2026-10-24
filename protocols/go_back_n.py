# StopAndWait.py
import time
from datetime import datetime
from socket import timeout as TimeoutError

from packet import Packet
from rdt_session import RDTSession


class GoBackN:
    MAX_RETRIES = 5

    def __init__(self, session: RDTSession) -> None:
        self.session = session
        self.metrics = []
        self.file_buffer = []
        self.expectedmd5: str = ""
        self.window_size: int = 16
        self.protocol_name = "gbn"

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
                "protocol": self.protocol_name,
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

        return total

    def _get_next_segment(self, seq: int) -> Packet:
        while True:
            seg: Packet = self.session.receive_packet()

            # retorna apenas se é de fato um pacote de dados.
            # se não, limpa o buffer até encontrar ou timeout()
            if seg.type == "DATA" and seg.seq == seq:
                return seg

    def run(self, group: str, segment_size: int, file_type: str):
        total = self._connect(group, segment_size, file_type)

        # vetores importantes para métrica
        time_sent: list[float] = [0.0] * total
        retries_by_segment: list[int] = [0] * total

        base = 0  # base da janela e primerio seq a receber
        retries_this_window = 0  # retries do seq atual enquanto base
        received = 0  # nº segmentos recebido
        next_seq_num = 0

        while received != total:
            # requisitar todos os segumentos da janela
            while next_seq_num < base + self.window_size and next_seq_num < total:
                self.session.send_req(next_seq_num)

                # atualizando métricas
                if retries_this_window:
                    retries_by_segment[next_seq_num] += 1
                else:
                    time_sent[next_seq_num] = time.perf_counter()

                next_seq_num += 1

            # espera receber o segmento desejado
            try:
                seg = self._get_next_segment(base)

                # atualizar métrica
                rtt_ms = (time.perf_counter() - time_sent[base]) * 1000.0
                timestamp = datetime.now().isoformat()

                self.collect_metrics(
                    base, timestamp, rtt_ms, seg.payload_size, retries_by_segment[base]
                )

                self.file_buffer.append(seg.payload)

                print(f"received {base}/{total}")

                # mover janela e requisitar mais um pacote
                received += 1
                base += 1
                retries_this_window = 0

            except TimeoutError:  # timeout na base -> retry da janela atual
                if retries_this_window == self.MAX_RETRIES:
                    return

                retries_this_window += 1
                print(f"(Timeout) tentando novamente janela de base '{base}'")
                next_seq_num = base
