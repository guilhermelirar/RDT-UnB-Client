# Script de teste do Servidor RDT-UnB com medição de RTT
import socket
import time

srv = ('137.131.178.229', 8080)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.settimeout(5)

print("--- INICIANDO TESTE COM MEDIÇÃO DE RTT ---")
# Script de teste com RTT e comparação de fórmulas de Throughput
import socket
import time

srv = ('137.131.178.229', 8080)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.settimeout(5)

print("--- INICIANDO TESTE COM MEDIÇÃO DE RTT E THROUGHPUT ---\n")

# 1. HELLO / OK
t0 = time.perf_counter()
s.sendto(b'HELLO|grupo=teste|segment_size=512|file=small', srv)
ok = s.recvfrom(65507)[0].decode()
rtt_hello = (time.perf_counter() - t0) * 1000.0

print(f'HELLO: {ok[:60]}...')
print(f'-> RTT Handshake (HELLO/OK): {rtt_hello:.2f} ms\n')

# 2. REQ seg 0
t0 = time.perf_counter()
s.sendto(b'REQ|seq=0', srv)
data = s.recvfrom(65507)[0]
rtt_seg0 = (time.perf_counter() - t0) * 1000.0

# Tamanho do payload (assumindo 512 bytes se veio pacote DATA padronizado)
payload_size = 512  

# FÓRMULA ANTIGA (Errada - calcula KiB/s sem converter para bits)
tp_antigo = payload_size / ((rtt_seg0 / 1000.0) * 1024)

# FÓRMULA CORRETA (Exata - calcula kbps em kilobits por segundo)
tp_correto_kbps = (payload_size * 8.0) / rtt_seg0

print(f'DATA seq=0: {len(data)} bytes recebidos')
print(f'-> RTT REQ 0: {rtt_seg0:.2f} ms')
print(f'-> Throughput [Fórmula Antiga / KiB/s]: {tp_antigo:.2f}')
print(f'-> Throughput [Fórmula Correta / kbps]: {tp_correto_kbps:.2f} kbps\n')

# 3. ACK e REQ seg 1
t0 = time.perf_counter()
s.sendto(b'ACK|seq=0', srv)
s.sendto(b'REQ|seq=1', srv)
data2 = s.recvfrom(65507)[0]
rtt_seg1 = (time.perf_counter() - t0) * 1000.0

tp_antigo_1 = payload_size / ((rtt_seg1 / 1000.0) * 1024)
tp_correto_kbps_1 = (payload_size * 8.0) / rtt_seg1

print(f'DATA seq=1: {len(data2)} bytes recebidos')
print(f'-> RTT REQ 1 (+ ACK): {rtt_seg1:.2f} ms')
print(f'-> Throughput [Fórmula Antiga / KiB/s]: {tp_antigo_1:.2f}')
print(f'-> Throughput [Fórmula Correta / kbps]: {tp_correto_kbps_1:.2f} kbps\n')

print('Servidor OK')
s.close()
