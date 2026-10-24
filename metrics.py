import csv
from datetime import datetime
from pathlib import Path

METRICS_DIR = Path("metrics")

def gen_name(group: str, protocol: str) -> str:
    now = datetime.now()
    timestamp_str = now.strftime("%Y%m%d_%H%M%S")
    file_name = f"metrics_{group}_{protocol}_{timestamp_str}.csv"
    return file_name

def save_metrics_csv(log_list: list[dict], group: str, 
                     protocol: str, file_type: str, loss: int, window: int = 1):
    if not log_list:
        print("[AVISO] Nenhuma métrica para salvar")
        return

    # 1. Monta o caminho da SUBPASTA do experimento
    if protocol.lower() == "saw":
        folder = METRICS_DIR / "saw" / file_type / f"loss_{loss}"
    else:
        folder = METRICS_DIR / protocol.lower() / f"win_{window}" / file_type / f"loss_{loss}"
    
    folder.mkdir(parents=True, exist_ok=True)

    # 2. Gera o NOME OBRIGATÓRIO exigido pela especificação
    file_name = gen_name(group, protocol)
    
    # 3. Caminho final do arquivo dentro da subpasta do experimento
    full_path = folder / file_name

    cols = list(log_list[0].keys())

    with open(full_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=cols)
        writer.writeheader()
        writer.writerows(log_list)

    print(f"[CSV] Logs salvos em '{full_path}'!")
