from datetime import datetime
import subprocess
import time

protocols = ["saw", "gbn"]
wsizes = [4, 8, 16]
losses = [5, 10]
file_types = ["small", "medium", "large"]

def run_experiment(protocol: str, window: int, 
                   file_type: str, loss: int = 0):
    group = "grupo13"
    cmd = [
        "python", "client.py", 
        "--p", protocol, 
        "--g", group, 
        "--file", file_type, 
        "--l", str(loss), 
        "--w", str(window)
    ]
    
    cmd_str = " ".join(cmd)
    print(f"Starting: {cmd_str} (timestamp={datetime.now().isoformat()})")
    
    start = time.perf_counter()
    subprocess.run(cmd)
    end = time.perf_counter()
    
    print(f"Finished '{cmd_str}' ({end - start} s)")

def run_lossless():
    for p in protocols:
        for ft in file_types:
            if p == "saw":
                run_experiment(p, 1, ft, 0)
                continue

            for wsize in wsizes:
                run_experiment(p, wsize, ft, 0)

def run_lossy():

    pass
