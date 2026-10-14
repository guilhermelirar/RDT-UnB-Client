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

    def connect(self, group: str, 
                segment_size: int, file_type: str) -> Packet | None:
        """
        Envia a mensagem de HELLO para registrar o grupo e negociar o 
        segment_size
        """
        max_retries = 5
        packet = Packet.hello(group, segment_size, file_type)

        for att in range(max_retries):
            try:
                start = time.time()
                self.sock.sendto(packet.encode(), self.server)
                data, _ = self.sock.recvfrom(1024)
                end = time.time()
                rtt_ms = (end - start) * 1000.0
                    
                print(f"[HELLO/OK] Conexão estabelecida (RTT: {rtt_ms} ms)")
                response = Packet.parse(data)
                return response

            except socket.timeout:
                print(f"[HELLO (Timeout)] {att+1}/{max_retries}...")

            except ValueError:
                print(f"[BAD PACKET] pacote mal formado")


    def send_req(self, seq: int) -> float:
        """
        Envia uma requisição para o servidor da sessão, solicitando o segmento
        de número de sequência seq 
        """
        request = Packet.req(seq)
        self.sock.sendto(request.encode(), self.server)
        return time.time()


    def receive_packet(self) -> Packet:
        """
        Retorna um pacote de dados do servidor, ou levanta exceção em caso 
        de timeout
        """
        data, _ = self.sock.recvfrom(1024)
        return Packet.parse(data)
