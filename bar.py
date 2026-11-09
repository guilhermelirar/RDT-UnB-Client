import matplotlib.pyplot as plt
import numpy as np

# Dados extraídos da Tabela Consolidada
cenarios = [
    'SAW (0%)', 'SAW (5%)',
    'GBN W=4 (0%)', 'GBN W=8 (0%)', 'GBN W=16 (0%)', 'GBN W=16 (5%)', 'GBN W=16 (10%)',
    'SR W=4 (0%)', 'SR W=8 (0%)', 'SR W=16 (0%)', 'SR W=16 (5%)', 'SR W=16 (10%)',
    'SR Adapt. (0%)', 'SR Adapt. (5%)', 'SR Adapt. (10%)'
]

throughput = [
    23.02, 19.43,
    91.64, 177.32, 303.41, 63.31, 36.36,
    95.93, 182.04, 372.37, 143.22, 114.58,
    379.14, 208.93, 147.82
]

# Definir cores para diferenciar os protocolos
cores = [
    '#e74c3c', '#e74c3c',  # SAW (Vermelho)
    '#f39c12', '#f39c12', '#f39c12', '#d35400', '#d35400',  # GBN (Laranja/Castanho)
    '#3498db', '#3498db', '#3498db', '#2980b9', '#2980b9',  # SR Fixo (Azul)
    '#2ecc71', '#27ae60', '#1e8449'   # SR Adaptativo (Verde)
]

plt.figure(figsize=(14, 7))
bars = plt.bar(cenarios, throughput, color=cores, edgecolor='black', linewidth=0.8)

plt.title('Comparação Consolidada do Throughput Médio entre os Protocolos (kbps)', fontsize=14, fontweight='bold', pad=15)
plt.ylabel('Throughput Médio (kbps)', fontsize=12)
plt.xticks(rotation=45, ha='right', fontsize=10)
plt.yticks(fontsize=10)
plt.grid(axis='y', linestyle='--', alpha=0.5)

# Adicionar o valor numérico em cima de cada barra
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + 5,
             f'{height:.1f}',
             ha='center', va='bottom', fontsize=8, rotation=0)

plt.tight_layout()
plt.savefig('grafico_throughput_consolidado.png', dpi=300)
print("Gráfico 'grafico_throughput_consolidado.png' gerado com sucesso!")
