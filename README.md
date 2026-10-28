# RDT-UnB Client

Implementação de um cliente de um protocolo Reliable Data Transfer (RDT) para obter um arquivo de um servidor.
Desenvolvido para disciplina de Teleinformática e Redes 2 (2026/2).

## Fluxogramas dos Protocolos

### 1. Go Back N

```mermaid
stateDiagram-v2
    [*] --> DISCONNECTED

    DISCONNECTED --> CONNECTING : Send HELLO
    CONNECTING --> CONNECTED : Receive OK
    CONNECTING --> DISCONNECTED : Timeout (Max Retries)

    CONNECTED --> SEND_WINDOW

    SEND_WINDOW --> WAITING_DATA : Send REQ (base ... base + N - 1)

    WAITING_DATA --> PROCESS_DATA : Receive DATA [seq == base]
    WAITING_DATA --> RETRY : Timeout

    RETRY --> SEND_WINDOW : [Retries < Max] / Retries++
    RETRY --> FAILED : Retries == Max Retries

    PROCESS_DATA --> SEND_WINDOW : [seq < total] / base++
    PROCESS_DATA --> COMPLETED : seq == last_segment

    COMPLETED --> [*] : Save File & Validate MD5
    FAILED --> [*] : Abort Download
```

## 2. Selective Repeat

```mermaid
stateDiagram-v2
    [*] --> DISCONNECTED

    DISCONNECTED --> CONNECTING : Send HELLO
    CONNECTING --> CONNECTED : Receive OK
    CONNECTING --> DISCONNECTED : Timeout (Max Retries)

    CONNECTED --> SEND_WINDOW
    
    SEND_WINDOW --> CHECK_TIMEOUTS : Send REQ (seq in window if not sent)
    
    CHECK_TIMEOUTS --> WAITING_DATA : Check & Resend Timed-out Segments
    
    WAITING_DATA --> PROCESS_DATA : Receive DATA [valid seq in window]
    WAITING_DATA --> SEND_WINDOW : Socket Timeout / Next Iteration
    
    PROCESS_DATA --> SLIDE_WINDOW : Buffer Segment
    
    SLIDE_WINDOW --> SEND_WINDOW : Advance Base [base < total]
    SLIDE_WINDOW --> COMPLETED : [base == total]

    COMPLETED --> [*] : Save File & Validate MD5
```
