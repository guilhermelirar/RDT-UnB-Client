# StopAndWait.py
from RDTSession import RDTSession
from socket import timeout as TimeoutError
import time

class StopAndWait:
    MAX_RETRIES = 5

    def __init__(self, session: RDTSession) -> None:
        self.session = session
        self.metrics = []
        self.file_buffer = []
        self.expectedmd5: str = ""

    @staticmethod
    def get_rtt_ms(start: float, end: float) -> float:
        return (end - start) * 1000.0

    def collect_metrics(self, seq: int, timestamps: tuple[float, float], 
                    payload_size: int, retries: int):
        PROTOCOL = "saw"
        WINDOW_SIZE = 1 
        rtt_ms = (timestamps[1] - timestamps[0]) * 1000.0
        throughput_kbps = payload_size * 8.0 / rtt_ms

        self.metrics.append({
            "segment": seq,
            "timestamp": timestamps[1],
            "size_bytes": payload_size,
            "rtt_ms": rtt_ms, 
            "timeout_ms": self.session.timeout * 1000.0,
            "throughput_kbps": throughput_kbps,
            "retransmissions": retries,
            "timeout_ocurred": 0 if retries == 0 else 1,
            "window_size": WINDOW_SIZE,
            "protocol": PROTOCOL
        })
    
    def run(self, group: str, segment_size: int, file_type: str):
        ok_pkt = self.session.connect(group, segment_size, file_type)

        if not ok_pkt:
            print("Conexão não pode ser estabelecida...")
            return []

        print(ok_pkt)
        self.expectedmd5 = str(ok_pkt.get("checksum"))

        total = ok_pkt.get("total_segments")
        if not (isinstance(total, int) and total > 0):
            print("Não há segmentos para obter...")
            return [] 
        
        seq = 0
        retries = 0
        req_timestamp = 0
        while (seq < total):
            try:
                # enviar e REQ e receber DATA 
                self.session.send_req(seq)
                if retries == 0:
                    req_timestamp = time.perf_counter()

                segment = self.session.receive_packet()
                rsp_timestamp = time.perf_counter()
               
                if seq % 256 == 0 or seq == total - 1:
                    print("[LOG]", segment)

                if segment.type == "DATA" and segment.get("seq") == seq:
                    # métricas
                    timestamps = (req_timestamp, rsp_timestamp)
                    self.collect_metrics(seq, timestamps, 
                                         segment.payload_size, retries)

                    self.file_buffer.append(segment.payload)
                    # self.session.send_ack(seq)

                    retries = 0 # Para próximo seq
                    seq += 1

            except TimeoutError:
                retries += 1
                print(f"[TIMEOUT] seq={seq}", 
                      f"tentativa {retries}/{self.MAX_RETRIES}")
                if retries == self.MAX_RETRIES:
                    return
    
    
    
