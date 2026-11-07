import csv
from datetime import datetime
from pathlib import Path

from metrics_collector import MetricsCollector

METRICS_DIR = Path("metrics")


def gen_name(group: str, protocol: str, loss: int, is_adaptive: bool) -> str:
    now = datetime.now()
    timestamp_str = now.strftime("%Y%m%d_%H%M%S")
    mode = "adaptive" if is_adaptive else "fixed"
    return f"metrics_{group}_{protocol}_{mode}_loss{loss}_{timestamp_str}.csv"


def save_metrics_csv(
    collector: MetricsCollector | None,
    group: str,
    file_type: str,
    loss: int,
    window: int = 1,
    is_adaptive: bool = False,
):
    if not collector or not collector.metrics:
        print("[AVISO] Nenhuma métrica para salvar")
        return None

    protocol = collector.protocol_name.lower()
    mode = "adaptive" if is_adaptive else "fixed"

    # Estrutura de pastas limpa: metrics/protocolo/modo/arquivo/
    folder = METRICS_DIR / protocol / mode / f"win_{window}" / file_type
    folder.mkdir(parents=True, exist_ok=True)

    file_name = gen_name(group, protocol, loss, is_adaptive)
    full_path = folder / file_name

    first_row = collector.metrics[0]
    if not first_row:
        return None

    cols = list(first_row.keys())

    with open(full_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=cols)
        writer.writeheader()
        writer.writerows([m for m in collector.metrics if m is not None])

    print(f"[CSV] Logs salvos em '{full_path}'!")
    return full_path
