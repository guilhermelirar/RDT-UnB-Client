import csv
from pathlib import Path
from datetime import datetime
import pandas as pd

METRICS_DIR = Path("metrics")
rows = []

for csv_file in METRICS_DIR.rglob("*.csv"):
    df = pd.read_csv(csv_file)
    if df.empty:
        continue

    # Extrai informações do CSV
    protocol = df["protocol"].iloc[0]
    window = df["window_size"].iloc[0]

    # Descobre o loss e se era adaptativo pelo nome do arquivo/caminho
    path_str = str(csv_file)
    is_adaptive = "adaptive" in path_str

    # Calcula total de retries
    total_retries = df["retransmissions"].sum()

    # Calcula o tempo total usando o primeiro e o último timestamp do log
    t_start = datetime.fromisoformat(df["timestamp"].iloc[0])
    t_end = datetime.fromisoformat(df["timestamp"].iloc[-1])
    total_time_s = (t_end - t_start).total_seconds()

    total_bytes = df["size_bytes"].sum()
    throughput_kbps = (total_bytes * 8 / 1000) / total_time_s if total_time_s > 0 else 0

    rows.append({
        "file": csv_file.name,
        "protocol": protocol,
        "mode": "adaptive" if is_adaptive else "fixed",
        "window": window,
        "total_time_s": round(total_time_s, 2),
        "total_retries": int(total_retries),
        "throughput_kbps": round(throughput_kbps, 2)
    })

summary_df = pd.DataFrame(rows)
summary_df.to_csv("summary_reconstructed.csv", index=False)
print("Resumo reconstruído com sucesso a partir dos CSVs salvos!")
print(summary_df.to_string())
