# StopAndWait.py
import time
from datetime import datetime
from socket import timeout as TimeoutError

from packet import Packet
from rdt_session import RDTSession
from protocols.base_protocol import BaseProtocol

class GoBackN(BaseProtocol):
    MAX_RETRIES = 5

    def __init__(self, session: RDTSession, window_size: int) -> None:
        super().__init__(session, window_size, "gbn")
        
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
                seg: Packet = self._get_next_segment(base)

                # atualizar métrica
                rtt_ms = (time.perf_counter() - time_sent[base]) * 1000.0
                timestamp = datetime.now().isoformat()

                self.collect_metrics(
                    base, timestamp, rtt_ms, seg.payload_size, retries_by_segment[base]
                )

                # Salvar no buffer
                self.file_buffer[base] = seg.payload

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
