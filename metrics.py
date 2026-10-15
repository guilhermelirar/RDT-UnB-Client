# metrics.py
import csv
from datetime import datetime

def gen_name(group: str, protocol: str) -> str:
    now = datetime.now()
    timestamp_str = now.strftime("%Y%m%d_%H%M%S")

    file_name = f"metrics_{group}_{protocol}_{timestamp_str}.csv"
    return file_name

def save_metrics_csv(log_list: list[dict], group: str, protocol: str):
    file_name = gen_name(group, protocol)
    if not log_list:
        print("[AVISO] Nenhuma métrica para salvar")
        return

    cols = list(log_list[0].keys())

    with open(file_name, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=cols)
        writer.writeheader()
        writer.writerows(log_list)

    print(f"[CSV] Logs de métricas salvos com sucesso em '{file_name}'!")
