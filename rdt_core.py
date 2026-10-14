# rdt_core.py
import socket, time
from argparse import Namespace
from dataclasses import dataclass

MAX_SEGMENT_SIZE = 512

@dataclass
class RDTConfig:
    server: str
    file_type: str
    group: str
    port: int = 8080

def request(data: bytes,
            server: tuple[str, int], 
            skt: socket.socket, 
            timeout = 5.0, max_attempts: int = 1) -> tuple[bytes | None, float]:
    """
    Envia requisição ao servidor especificado, e retorna tupla 
    com a resposta em bytes e o RTT da comunicação. 
    Em caso de exceder número de tentativas, a resposta será None
    """
    rtt_ms: float = 0.0

    attempt = 0
    while (attempt < max_attempts):
        try:
            start = time.time()
            skt.sendto(data, server)
            skt.settimeout(timeout)
            
            data_response, _ = skt.recvfrom(512)

            end = time.time()
            rtt_ms = (end - start) * 1000.0
            print("RTT (ms):", rtt_ms)
            return data_response, timeout

        except socket.timeout:
            print(f"TIMEOUT ({timeout} ms) at attempt {attempt+1/max_attempts}")
            data_response = None

    return None, timeout


def send_hello(cfg: RDTConfig, skt: socket.socket, timeout = 5.0):
    header = ['HELLO', 
              f'grupo={cfg.group}',
              f'segment_size={MAX_SEGMENT_SIZE}',
              f'file={cfg.file_type}']
    
    header_bytes = '|'.join(header).encode()
    
    response, rtt = request(header_bytes, 
                          (cfg.server, cfg.port), 
                          skt, timeout, 5)
   
    if response:
        return response.decode(), rtt

    return None, rtt

def parse_hello(data: str) -> dict:
    fields = data.split('|')
    d = {"label": data[0]}

    for f in fields[1:]:
        key = f.split('=')[0]
        value = f.split('=')[1]

        d[key] = value
        

    return d

def run_rdt(args: Namespace):
    config = RDTConfig(server=args.server, 
                       file_type=args.file, 
                       group=args.group)
    
    skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)   
    data, rtt = send_hello(config, skt, 0.5)
   
    if data:
        print(parse_hello(data))
