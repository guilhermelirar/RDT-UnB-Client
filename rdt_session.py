import random
import socket
import time

from packet import Packet


class RDTSession:
    """
    Classe que encapsula uma sessão do RDT, com uma configuração
    de servidor e porta de destino, e lida com envio e recepção
    de mensagens, utilizando um socket UDP
    """

    def __init__(self, server, timeout=1.0, simulated_loss: int = 0) -> None:
        """
        Configura endereço ip:porta do servidor de destino, e cria o
        objeto socket UDP com o timeout configurado
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        self.timeout = timeout
        self.sock.settimeout(timeout)
        self.server: tuple[str, int] = server
        self.loss = simulated_loss
        self.dropped_seq = set()

    def set_timeout(self, timeout: float):
        self.timeout = timeout
        self.sock.settimeout(timeout)

    def connect(self, group: str, segment_size: int, file_type: str) -> Packet | None:
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
                print(f"[HELLO (Timeout)] {att + 1}/{max_retries}...")

            except ValueError:
                print(f"[BAD PACKET] pacote mal formado")

    def was_dropped(self, seq: int) -> bool:
        return seq in self.dropped_seq

    def send_req(self, seq: int):
        """
        Envia uma requisição para o servidor da sessão, solicitando o segmento
        de número de sequência seq
        """
        if random.random() < (self.loss / 100):
            return self.dropped_seq.add(seq)

        request = Packet.req(seq)
        self.sock.sendto(request.encode(), self.server)

    def send_ack(self, seq: int):
        """
        Envia um ACK com o número de sequencia do segmento recebido
        """
        request = Packet.ack(seq)
        self.sock.sendto(request.encode(), self.server)

    def send_fin(self, md5: str):
        request = Packet.fin(md5)
        self.sock.sendto(request.encode(), self.server)

    def receive_packet(self) -> Packet:
        """
        Espera por um pacote no socket, e em caso de recebimento,
        retorna um objeto Packet e um float correspondente ao tempo
        que o pacote foi recebido. Em caso de timeout, lança uma exceção
        """
        data, _ = self.sock.recvfrom(1024)
        return Packet.parse(data)

    def close(self):
        self.sock.close()
