import glob
import os

import matplotlib.pyplot as plt
import pandas as pd

# Criar pasta para salvar as figuras se não existir
os.makedirs("plots", exist_ok=True)


def plot_section_2():
    # Busca o arquivo CSV do SR Adaptativo
    # (Ajuste o padrão de busca se a sua estrutura de pastas for ligeiramente diferente)
    search_pattern = "metrics/**/sr/**/adaptive/**/metrics_*.csv"
    files = glob.glob(search_pattern, recursive=True)

    if not files:
        # Fallback: procura qualquer CSV que contenha 'adaptive' ou 'sr'
        files = glob.glob("metrics/**/*adaptive*.csv", recursive=True)

    if not files:
        print(
            "[ERRO] Nenhum CSV de métricas do SR Adaptativo foi encontrado em 'metrics/'."
        )
        print("Certifique-se de que a pasta 'metrics/' contém os logs dos testes.")
        return

    # Pega o primeiro arquivo encontrado para a demonstração da Seção 2
    csv_file = files[0]
    print(f"[LENDO] Processando arquivo para a Seção 2: {csv_file}")

    df = pd.read_csv(csv_file)

    # -------------------------------------------------------------
    # Gráfico 1: RTT Estimado vs RTT Medido (Convergência)
    # -------------------------------------------------------------
    plt.figure(figsize=(10, 5))

    # Se houver coluna de seq_num ou usaremos o índice
    x_axis = df["seq_num"] if "seq_num" in df.columns else df.index

    # RTTs em milissegundos
    rtt_measured = df["rtt_ms"] if "rtt_ms" in df.columns else df["rtt"] * 1000.0
    rtt_estimated = (
        df["rtt_est"] * 1000.0 if "rtt_est" in df.columns else df["rtt_est_ms"]
    )

    plt.plot(
        x_axis,
        rtt_measured,
        label="RTT Medido (Amostra)",
        color="#3498db",
        alpha=0.5,
        linewidth=1,
    )
    plt.plot(
        x_axis, rtt_estimated, label="RTT Estimado (EWMA)", color="#e74c3c", linewidth=2
    )

    plt.title(
        "Seção 2: Convergência do Estimador EWMA (RTT Estimado vs. Medido)",
        fontsize=12,
        fontweight="bold",
    )
    plt.xlabel("Número de Sequência (Segmento)", fontsize=10)
    plt.ylabel("Tempo (ms)", fontsize=10)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend(loc="upper right")
    plt.tight_layout()

    plot1_path = os.path.join("plots", "sec2_rtt_est_vs_medido.png")
    plt.savefig(plot1_path, dpi=300)
    plt.close()
    print(f"[OK] Gráfico 1 salvo em: {plot1_path}")

    # -------------------------------------------------------------
    # Gráfico 2: Evolução do Timeout (RTO) ao Longo da Transferência
    # -------------------------------------------------------------
    plt.figure(figsize=(10, 5))

    # Timeout em milissegundos
    if "timeout_calc" in df.columns:
        timeout_val = df["timeout_calc"] * 1000.0
    elif "timeout" in df.columns:
        timeout_val = df["timeout"] * 1000.0
    else:
        timeout_val = (df["rtt_est"] + 4.0 * df["dev_rtt"]) * 1000.0

    plt.plot(
        x_axis,
        timeout_val,
        label="Timeout Calculado (RTO)",
        color="#2ecc71",
        linewidth=2,
    )
    plt.axhline(y=500, color="#95a5a6", linestyle="--", label="Baseline Fixo (500 ms)")

    plt.title(
        "Seção 2: Adaptação Dinâmica do Timeout (RTO) ao Longo do Tempo",
        fontsize=12,
        fontweight="bold",
    )
    plt.xlabel("Número de Sequência (Segmento)", fontsize=10)
    plt.ylabel("Timeout (ms)", fontsize=10)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend(loc="upper right")
    plt.tight_layout()

    plot2_path = os.path.join("plots", "sec2_timeout_evolution.png")
    plt.savefig(plot2_path, dpi=300)
    plt.close()
    print(f"[OK] Gráfico 2 salvo em: {plot2_path}")


if __name__ == "__main__":
    plot_section_2()
