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
            timeout = 5.0) -> tuple[bytes | None, float]:
    """
    Envia requisição ao servidor especificado, e retorna tupla 
    com a resposta em bytes e o RTT da comunicação. Em caso de timeout,
    a resposta será None
    """
    rtt_ms: float = 0.0

    try:
        start = time.time()
        skt.sendto(data, server)
        skt.settimeout(timeout)
        
        data_response, _ = skt.recvfrom(512)

        end = time.time()
        rtt_ms = (end - start) * 1000.0
        print("RTT (ms):", rtt_ms)

    except socket.timeout:
        data_response = None

    return data_response, rtt_ms

def send_hello(cfg: RDTConfig, skt: socket.socket, timeout = 5.0):
    header = ['HELLO', 
              f'grupo={cfg.group}',
              f'segment_size={MAX_SEGMENT_SIZE}',
              f'file={cfg.file_type}']
    
    header_bytes = '|'.join(header).encode()
    
    response, _ = request(header_bytes, (cfg.server, cfg.port), skt, timeout)
    if response:
        print("Hello response:", response.decode())
    else:
        print("TIMEOUT")

def run_rdt(args: Namespace):
    config = RDTConfig(server=args.server, 
                       file_type=args.file, 
                       group=args.group)
    
    skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)   
    send_hello(config, skt, 0.5)
      
