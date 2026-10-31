# metrics.py
import time
from datetime import datetime


class MetricsCollector:
    """
    Classe para coleta de métricas durante obtenção de arquivos no RDT
    """

    def __init__(
        self,
        total_segments: int,
        window_size: int,
        protocol_name: str,
        segment_size: int = 512,
    ):
        # Inicializa informações básicas a respeito do protocolo atual
        self.total_segments = total_segments
        self.window_size = window_size
        self.protocol_name = protocol_name
        self.metrics: list[dict | None] = [None] * total_segments
        self.segment_size = segment_size

        # marcação do início da transferência (para resumo)
        self.start_of_transfer_time: float = time.perf_counter()
        self.end_of_transfer_time: float = 0.0

        # controle de taxa de atualização de progresso
        self._last_print_time: float = 0.0
        self._min_print_interval: float = 0.1

        # metricas globais
        self._total_retries = 0

    def collect(
        self,
        seq: int,
        rtt_ms: float,
        payload_size: int,
        retries: int,
        timeout_s: float,
        was_dropped: bool,
    ):
        # Criar o dicionário de métricas conforme especificação do trabalho
        throughput_kbps = (payload_size * 8.0) / rtt_ms if rtt_ms > 0 else 0.0
        self.metrics[seq] = {
            "segment": seq,
            "timestamp": datetime.now().isoformat(),
            "size_bytes": payload_size,
            "rtt_ms": rtt_ms,
            "timeout_ms": timeout_s * 1000.0,
            "throughput_kbps": throughput_kbps,
            "retransmissions": retries,
            "timeout_ocurred": 1 if retries > 0 else 0,
            "window_size": self.window_size,
            "protocol": self.protocol_name,
            "simulated_loss": 1 if was_dropped else 0,
        }

        self._total_retries += retries

    def print_summary(self):
        # Exibe métricas globais de forma resumida
        print(f"\nRESUMO {self.protocol_name.upper()} | WIN {self.window_size}")
        total_transfer_time = self.end_of_transfer_time - self.start_of_transfer_time

        if total_transfer_time <= 0:
            print("\tTransferência não realizada")
            return

        rtts = [m["rtt_ms"] for m in self.metrics if m and "rtt_ms" in m]
        avg_rtt = sum(rtts) / len(rtts) if rtts else 0.0

        throughput_kbps = (self.segment_size * self.total_segments * 8.0) / (
            total_transfer_time * 1000.0
        )
        print(f"\tRTT médio: {avg_rtt:.2f} ms")
        print(f"\tTempo total: {total_transfer_time:.2f} s")
        print(f"\tThroughput: {throughput_kbps:.2f} kbps")
        print(f"\tTotal de retransmissões: {self._total_retries}")

    def log_progress(self, completed_segments: int):
        if self.total_segments <= 0:
            return

        now = time.perf_counter()
        is_last = completed_segments == self.total_segments

        # Rate-limiting: só printa se passou o intervalo de tempo OU se for o último segmento
        if not is_last and (now - self._last_print_time) < self._min_print_interval:
            return

        self._last_print_time = now
        elapsed = max(0.0001, now - self.start_of_transfer_time)
        percent = (completed_segments / self.total_segments) * 100

        throughput_kbps = (8 * self.segment_size * completed_segments) / (
            elapsed * 1000.0
        )

        print(
            f"\r[{self.protocol_name.upper()} | Win {self.window_size}] "
            f"Progress: {percent:5.1f}% ({throughput_kbps:8.2f} kbps) "
            f"| Retries: {self._total_retries}",
            end="",
            flush=True,
        )

        if is_last:
            self.end_of_transfer_time = time.perf_counter()
            print()
