# StopAndWait.py
from packet import Packet
from rdt_session import RDTSession
from socket import timeout as TimeoutError
import time

class StopAndWait:
    MAX_RETRIES = 5

    def __init__(self, session: RDTSession) -> None:
        self.session = session
        self.metrics = []
        self.file_buffer = []
        self.expectedmd5: str = ""

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
            if seg.type == "DATA" and seg.get("seq") == seq: 
                return seg
        

    def run(self, group: str, segment_size: int, file_type: str):
        total = self._connect(group, segment_size, file_type)
        seq = 0
        retries = 0
        req_timestamp = 0
        while (seq < total):
            try:
                # enviar e REQ e receber DATA 
                self.session.send_req(seq)
                if retries == 0:
                    req_timestamp = time.perf_counter()

                segment = self._get_next_segment(seq)
                rsp_timestamp = time.perf_counter()
               
                if seq % 256 == 0 or seq == total - 1:
                    print("[LOG]", segment)

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
    
    
    
