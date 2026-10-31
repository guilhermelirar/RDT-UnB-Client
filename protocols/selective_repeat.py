# selective_repeat.py
import time
from datetime import datetime

from packet import Packet
from protocols.base_protocol import BaseProtocol
from rdt_session import RDTSession


class SelectiveRepeat(BaseProtocol):
    MAX_RETRIES = 5

    def __init__(self, session: RDTSession, window_size: int) -> None:
        super().__init__(session, window_size, "sr")
        self.timeout = 0.5

    def run(self, group: str, segment_size: int, file_type: str):
        total = self._connect(group, segment_size, file_type)
        self.session.set_timeout(0.1)

        # vetores importantes para métrica
        first_sent: list[float] = [0.0] * total
        last_sent: list[float] = [0.0] * total
        retries_by_segment: list[int] = [0] * total

        base = 0  # base da janela e primerio seq a receber
        received = 0  # nº segmentos recebido
        next_seq_num = 0
        total_retries = 0

        while received != total:
            # deslizar janela

            while next_seq_num < base + self.window_size and next_seq_num < total:
                self.session.send_req(next_seq_num)
                first_sent[next_seq_num] = time.perf_counter()
                last_sent[next_seq_num] = time.perf_counter()
                next_seq_num += 1

            window = range(base, min(base + self.window_size, total))

            # requisitar os segmentos da janela em caso de timeout
            for seq in window:
                timeout = (time.perf_counter() - last_sent[seq]) > self.timeout
                if timeout and not self.file_buffer[seq]:
                    self.session.send_req(seq)
                    retries_by_segment[seq] += 1
                    total_retries += 1
                    last_sent[seq] = time.perf_counter()

            # espera receber o segmento desejado
            try:
                seg: Packet = self.session.receive_packet()

                if (
                    seg.type != "DATA"
                    or not (base <= seg.seq < base + self.window_size)
                    or self.file_buffer[seg.seq]
                ):
                    continue

                # atualizar métrica
                rtt_ms = (time.perf_counter() - first_sent[seg.seq]) * 1000.0

                if self.metrics_collector:
                    self.metrics_collector.collect(
                        seg.seq,
                        rtt_ms,
                        seg.payload_size,
                        retries_by_segment[seg.seq],
                        self.timeout,  # timeout não é da sessão
                        self.session.was_dropped(seg.seq),
                    )

                    self.metrics_collector.log_progress(base + 1)

                # Salvar no buffer
                self.file_buffer[seg.seq] = seg.payload

                # mover janela e requisitar mais um pacote
                received += 1

                # deslizar janela
                while base < total and self.file_buffer[base]:
                    base += 1

            except TimeoutError:  # timeout na base -> retry da janela atual
                pass
