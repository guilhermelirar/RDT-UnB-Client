# StopAndWait.py
import time

from datetime import datetime
from packet import Packet
from protocols.base_protocol import BaseProtocol
from rdt_session import RDTSession
from socket import timeout as TimeoutError

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
        start_time = time.perf_counter()

        # Enquanto há DATA para receber
        while seq < total:
            retries = 0
            req_sent_time = time.perf_counter()
            req_timestamp = datetime.now().isoformat()
            
            # Tenta REQ (seq) até 'MAX_RETRIES' vezes
            while retries < self.MAX_RETRIES:
                try:
                    self.session.send_req(seq)
                    segment: Packet = self._get_next_segment(seq)
                    rsp_time = time.perf_counter()
                    
                    # métricas e salvar  
                    rtt_ms = (rsp_time - req_sent_time) * 1000.0
                    self.collect_metrics(
                        seq, req_timestamp, rtt_ms, 
                        segment.payload_size, retries
                    )

                    self.file_buffer[seq] = segment.payload

                    seq += 1
                    self.log_progress(seq, total, start_time, total_retries)
                    break # sai do loop em caso de sucesso 

                except TimeoutError:
                    retries += 1
                    total_retries += 1 

            else:
                # executado em caso de MAX_RETRIES 
                print(f"[ERRO] Limite de retries atingido no pacote {seq}")
                return
    
    
    
