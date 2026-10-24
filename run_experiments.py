import subprocess


protocols = ["saw", "gbn"]
wsizes = [4, 8, 16]
losses = [5, 10]
files = ["small", "medium", "large"]

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

    subprocess.run(cmd)

run_experiment("gbn", wsizes[0], files[0], losses[0])
