import csv
from pathlib import Path
import subprocess
import time

SUMMARY_FILE = Path("experiments_summary.csv")
GROUP = "grupo13"

def append_to_summary(
    protocol: str,
    window: int,
    file_type: str,
    loss: int,
    total_time: float,
):
  if protocol == "saw":
    folder = Path("metrics") / "saw" / file_type
  else:
    folder = Path("metrics") / protocol / f"win_{window}" / file_type

  files = list(folder.glob("*.csv"))
  if not files:
    return

  latest_csv = max(files, key=lambda p: p.stat().st_mtime)

  total_retries = 0
  total_bytes = 0

  with open(latest_csv, mode="r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
      total_retries += int(row["retransmissions"])
      total_bytes += int(row["size_bytes"])

  throughput_kbps = (
      round((total_bytes * 8 / 1000) / total_time, 2) if total_time > 0 else 0
  )

  file_exists = SUMMARY_FILE.exists()
  with open(SUMMARY_FILE, mode="a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    if not file_exists:
      writer.writerow([
          "protocol",
          "window",
          "file_type",
          "loss",
          "total_time_s",
          "total_retries",
          "throughput_kbps",
      ])

    writer.writerow([
        protocol,
        window,
        file_type,
        loss,
        round(total_time, 2),
        total_retries,
        throughput_kbps,
    ])


def run_exp(protocol: str, window: int, file_type: str, loss: int):
  cmd = [
      "python",
      "client.py",
      "--protocol",
      protocol,
      "--group",
      GROUP,
      "--file",
      file_type,
      "--loss",
      str(loss),
      "--window_size",
      str(window),
  ]

  print(f"\n[RODANDO] {protocol.upper()} |", 
        f"Win: {window} | File: {file_type} | Loss: {loss}%")

  start = time.perf_counter()
  subprocess.run(cmd)
  end = time.perf_counter()

  elapsed = end - start
  append_to_summary(protocol, window, file_type, loss, elapsed)


def main():
  for ft in ["small", "medium"]:
    run_exp("saw", 1, ft, 0)
    for w in [4, 8]:
      run_exp("gbn", w, ft, 0)
      run_exp("sr", w, ft, 0)

  for loss in [5, 10]:
    run_exp("saw", 1, "small", loss)
    run_exp("gbn", 8, "small", loss)
    run_exp("sr", 8, "small", loss)


if __name__ == "__main__":
  main()
