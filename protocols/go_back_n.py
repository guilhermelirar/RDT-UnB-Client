# go_back_n.py
import time
from datetime import datetime

from packet import Packet
from protocols.base_protocol import BaseProtocol
from rdt_session import RDTSession


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
        total_retries = 0

        while received != total:
            # requisitar todos os segumentos da janela
            while next_seq_num < base + self.window_size and next_seq_num < total:
                self.session.send_req(next_seq_num)

                # atualizando métricas
                if retries_this_window:
                    retries_by_segment[next_seq_num] += 1
                    total_retries += 1
                else:
                    time_sent[next_seq_num] = time.perf_counter()

                next_seq_num += 1

            # espera receber o segmento desejado
            try:
                seg: Packet = self._get_next_segment(base)

                # atualizar métrica
                rtt_ms = (time.perf_counter() - time_sent[base]) * 1000.0
                if self.metrics_collector:
                    self.metrics_collector.collect(
                        base,
                        rtt_ms,
                        seg.payload_size,
                        retries_by_segment[base],
                        self.session.timeout,
                        self.session.was_dropped(base),
                    )

                    self.metrics_collector.log_progress(base + 1)

                # Salvar no buffer
                self.file_buffer[base] = seg.payload

                # mover janela e requisitar mais um pacote
                received += 1
                base += 1
                retries_this_window = 0

            except TimeoutError:  # timeout na base -> retry da janela atual
                if retries_this_window == self.MAX_RETRIES:
                    return

                retries_this_window += 1
                next_seq_num = base
