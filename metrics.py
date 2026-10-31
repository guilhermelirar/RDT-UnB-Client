import csv
from datetime import datetime
from pathlib import Path
from typing import Any, cast

from metrics_collector import MetricsCollector

METRICS_DIR = Path("metrics")


def gen_name(group: str, protocol: str, loss: int) -> str:
    now = datetime.now()
    timestamp_str = now.strftime("%Y%m%d_%H%M%S")
    return f"metrics_{group}_{protocol}_{timestamp_str}_loss{loss}.csv"


def save_metrics_csv(
    collector: MetricsCollector | None, group: str, file_type: str, loss: int, window: int = 1
):
    if not collector:
        print("[AVISO] Nenhuma métrica para salvar")
        return None

    log_list = collector.metrics
    protocol = collector.protocol_name

    if not log_list:
        print("[AVISO] Nenhuma métrica para salvar")
        return None

    if protocol.lower() == "saw":
        folder = METRICS_DIR / "saw" / file_type
    else:
        folder = METRICS_DIR / protocol.lower() / f"win_{window}" / file_type

    folder.mkdir(parents=True, exist_ok=True)

    file_name = gen_name(group, protocol, loss)
    full_path = folder / file_name

    first_row = log_list[0]
    if not first_row:
        print("[AVISO] Primeira linha de métrica inválida")
        return None

    cols = cast(list[str], list(first_row.keys()))

    with open(full_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=cols)
        writer.writeheader()
        writer.writerows(cast(list[dict[str, Any]], log_list))

    print(f"[CSV] Logs salvos em '{full_path}'!")
    return full_path
