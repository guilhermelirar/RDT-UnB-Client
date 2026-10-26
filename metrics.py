import csv
from datetime import datetime
from pathlib import Path

METRICS_DIR = Path("metrics")

def gen_name(group: str, protocol: str, loss: int) -> str:
    now = datetime.now()
    timestamp_str = now.strftime("%Y%m%d_%H%M%S")
    file_name = f"metrics_{group}_{protocol}_{timestamp_str}_loss{loss}.csv"
    return file_name

def save_metrics_csv(log_list: list, group: str, 
                     protocol: str, file_type: str, loss: int, window: int = 1):
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

    cols = list(log_list[0].keys())

    with open(full_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=cols)
        writer.writeheader()
        writer.writerows(log_list)

    print(f"[CSV] Logs salvos em '{full_path}'!")
    return full_path
