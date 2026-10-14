import socket, time
from Packet import Packet

class RDTSession:
    """
    Classe que encapsula uma sessão do RDT, com uma configuração 
    de servidor e porta de destino, e lida com envio e recepção
    de mensagens, utilizando um socket UDP
    """

    def __init__(self, server, timeout = 2.0) -> None:
        """
        Configura endereço ip:porta do servidor de destino, e cria o 
        objeto socket UDP com o timeout configurado
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        self.sock.settimeout(timeout)
        self.server: tuple[str, int] = server 
        self.max_retries: int = 5

    def connect(self, group: str, 
                segment_size: int, file_type: str) -> Packet | None:
        """
        Envia a mensagem de HELLO para registrar o grupo e negociar o 
        segment_size
        """
        packet = Packet.hello(group, segment_size, file_type)
        

        start = time.time()
        self.sock.sendto(packet.encode(), self.server)
        
        for att in range(self.max_retries):
            try:
                data, _ = self.sock.recvfrom(1024)
                end = time.time()
                rtt_ms = (end - start) * 1000.0
                    
                print(f"[HELLO/OK] Conexão estabelecida (RTT: {rtt_ms} ms)")
                response = Packet.parse(data)
                return response

            except socket.timeout:
                print(f"[HELLO (Timeout)] {att+1}/{self.max_retries}...")

            except ValueError:
                print(f"[BAD PACKET] pacote mal formado")


    def send_req(self, seq: int):
        """
        Envia uma requisição para o servidor da sessão, solicitando o segmento
        de número de sequência seq 
        """
        pass

    def receive_packet(self):
        """
        Retorna um pacote de dados do servidor, ou levanta exceção em caso 
        de timeout
        """
        pass
