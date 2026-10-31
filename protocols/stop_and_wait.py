# StopAndWait.py
import time
from datetime import datetime

from packet import Packet
from protocols.base_protocol import BaseProtocol

# stop_and_wait.py
from rdt_session import RDTSession


class StopAndWait(BaseProtocol):
    MAX_RETRIES = 5

    def __init__(self, session: RDTSession) -> None:
        """Inicializa com a sessão e janela de tamanho 1 (um segmento por RTT)"""
        super().__init__(session, 1, "saw")

    def run(self, group: str, segment_size: int, file_type: str):
        """
        Solicita transferência do arquivo por meio de enviar REQ  esperar
        DATA com seq correspondente
        """
        total = self._connect(group, segment_size, file_type)
        seq = 0
        total_retries = 0

        # Enquanto há DATA para receber
        while seq < total:
            retries = 0
            req_sent_time = time.perf_counter()

            # Tenta REQ (seq) até 'MAX_RETRIES' vezes
            while retries < self.MAX_RETRIES:
                try:
                    self.session.send_req(seq)
                    segment: Packet = self._get_next_segment(seq)
                    rsp_time = time.perf_counter()

                    # métricas e salvar
                    rtt_ms = (rsp_time - req_sent_time) * 1000.0

                    if self.metrics_collector:
                        self.metrics_collector.collect(
                            seq,
                            rtt_ms,
                            segment.payload_size,
                            retries,
                            self.session.timeout,
                            self.session.was_dropped(seq),
                        )

                        self.metrics_collector.log_progress(seq + 1)

                    self.file_buffer[seq] = segment.payload

                    seq += 1
                    break  # sai do loop em caso de sucesso

                except TimeoutError:
                    retries += 1
                    total_retries += 1

            else:
                # executado em caso de MAX_RETRIES
                print(f"[ERRO] Limite de retries atingido no pacote {seq}")
                return
