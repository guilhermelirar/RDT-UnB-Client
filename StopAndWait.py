# StopAndWait.py
from RDTSession import RDTSession
from socket import timeout as TimeoutError
import time

from file_manager import save_downloaded_file

class StopAndWait:
    MAX_RETRIES = 5

    def __init__(self, session: RDTSession) -> None:
        self.session = session

    @staticmethod
    def get_rtt_ms(start: float, end: float) -> float:
        return (end - start) * 1000.0

    def run(self, group: str, segment_size: int, file_type: str):
        log_list = []
        file_buffer = []
        ok_pkt = self.session.connect(group, segment_size, file_type)

        if not ok_pkt:
            print("Conexão não pode ser estabelecida...")
            return []

        print(ok_pkt)

        total = ok_pkt.get("total_segments")
        if not (isinstance(total, int) and total > 0):
            print("Não há segmentos para obter...")
            return [] 
        
        seq = 0
        retries = 0
        start_rtt = 0
        while (seq < total):
            try:
                # enviar e REQ e receber DATA 
                self.session.send_req(seq)
                if retries == 0:
                    start_rtt = time.perf_counter()

                segment = self.session.receive_packet()
                timestamp = time.perf_counter()
                
                print("[LOG]", segment)

                if segment.type == "DATA" and segment.get("seq") == seq:
                    # métricas
                    rtt_ms = self.get_rtt_ms(start_rtt, timestamp)
                    throughput_kbps = segment.payload_size / \
                            ((rtt_ms / 1000.0) * 1024)

                    log_list.append({
                        "segment": seq,
                        "timestamp": timestamp,
                        "size_bytes": segment.payload_size,
                        "rtt_ms": rtt_ms, 
                        "timeout_ms": self.session.timeout * 1000.0,
                        "throughput_kbps": throughput_kbps,
                        "retransmissions": retries,
                        "timeout_ocurred": 0 if retries == 0 else 1,
                        "window_size": 1,
                        "protocol": "saw"
                    })
                    
                    file_buffer.append(segment.payload)
                    # self.session.send_ack(seq)

                    retries = 0 # Para próximo seq
                    seq += 1

            except TimeoutError:
                retries += 1
                print(f"[TIMEOUT] seq={seq}", 
                      f"tentativa {retries}/{self.MAX_RETRIES}")
                if retries == self.MAX_RETRIES:
                    return log_list
            
        calculated_md5 = save_downloaded_file(file_buffer,
            f"downloaded_{group}_{file_type}.bin") 
        
        if (calculated_md5 != ok_pkt.get("checksum")):
            print(f"[ERROR] checksum incorreto")

        return log_list
