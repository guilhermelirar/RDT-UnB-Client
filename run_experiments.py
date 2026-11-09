import subprocess
import time

GROUP = "grupo13"

def run_cmd(cmd):
    print(f"\n[EXECUTANDO] {' '.join(cmd)}")
    subprocess.run(cmd)
    time.sleep(1) # pausa curta entre testes

def main():
    # -------------------------------------------------------------
    # 1. VISÃO INTEGRADA (Seção 5 do Relatório - Arquivo 'small ')
    # Cenários: SAW (W=1), GBN (W=16 Fixo/Adapt), SR (W=16 Fixo/Adapt)
    # -------------------------------------------------------------
    base_args = ["python", "client.py", "--group", GROUP, "--file", "small"]

    # SAW Fixo e com perda
    run_cmd(base_args + ["-p", "saw", "-w", "1", "-l", "0"])
    run_cmd(base_args + ["-p", "saw", "-w", "1", "-l", "5"])

    # GBN Fixo e co mperdas
    run_cmd(base_args + ["-p", "gbn", "-w", "16", "-l", "0"])
    run_cmd(base_args + ["-p", "gbn", "-w", "16", "-l", "5"])
    run_cmd(base_args + ["-p", "gbn", "-w", "16", "-l", "10"])

    # SR Fixo e Adaptativo (sem perda, para baseline da Seção 5)
    run_cmd(base_args + ["-p", "sr", "-w", "16", "-l", "0"])
    run_cmd(base_args + ["-p", "sr", "-w", "16", "-l", "0", "--adaptive"])


    # 2. COMPARAÇÃO FIXO vs ADAPTATIVO SOB PERDA (Seção 3 do Relatório)
    # SR em 5% e 10% de perda (arquivo 'large' ou 'medium')
    # -------------------------------------------------------------
    for loss in [5, 10]:
        # Fixo
        run_cmd(base_args + ["-p", "sr", "-w", "16", "-l", str(loss)])
        # Adaptativo
        run_cmd(base_args + ["-p", "sr", "-w", "16", "-l", str(loss), "--adaptive"])

    # -------------------------------------------------------------
    # VARIAÇÃO DE JANELA (W=4 e W=8) - Timeout Fixo (Loss 0%)
    # -------------------------------------------------------------
    for w in [4, 8]:
        run_cmd(base_args + ["-p", "gbn", "-w", str(w), "-l", "0"])
        run_cmd(base_args + ["-p", "sr", "-w", str(w), "-l", "0"])

    # -------------------------------------------------------------
    # 3. SENSIBILIDADE DE ALFA E BETA (Seção 2 do Relatório)
    # Testar valores diferentes para provar a escolha de alfa e beta
    # -------------------------------------------------------------
    # Padrão TCP (alfa=0.125, beta=0.25) -> Já foi rodado acima
    # Cenário Reativo (alfa=0.25, beta=0.50)
    run_cmd(base_args + ["-p", "sr", "-w", "16", "-l", "5", "--adaptive", "--alpha", "0.25", "--beta", "0.50"])
    # Cenário Conservador (alfa=0.05, beta=0.10)
    run_cmd(base_args + ["-p", "sr", "-w", "16", "-l", "5", "--adaptive", "--alpha", "0.05", "--beta", "0.10"])

if __name__ == "__main__":
    main()
