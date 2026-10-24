import hashlib
from cli import MAX_SEGMENT_SIZE, get_args
from protocols.go_back_n import GoBackN
from rdt_session import RDTSession
from protocols.stop_and_wait import StopAndWait
from metrics import save_metrics_csv


PORT = 8080

def save_downloaded_file(file_buffer: list[bytes], 
                         filename: str, expected_md5: str) -> bool:
    full_content = b"".join(file_buffer)
    
    with open(filename, "wb") as f:
        f.write(full_content)
    
    md5_hash = hashlib.md5(full_content).hexdigest()
    
    ok: bool = md5_hash.lower() == expected_md5.lower()
    
    if ok:
        print(f"[Checksum OK] {md5_hash}")
    else:
        print(f"[ERROR] Checksum difere: esperado '{expected_md5}',",  
              f"obtido '{md5_hash}'")

    return ok

def main():
    args = get_args()

    # parametros para a comunicação
    server = (args.server, PORT)
    file_type = args.file
    group = args.group

    # sessão RDT
    session = RDTSession(server)

    # protocolo de envio e retransmissão
    #protocol = StopAndWait(session)
    protocol = GoBackN(session, 4)

    # obter arquivo do servidor
    protocol.run(group, MAX_SEGMENT_SIZE, file_type)
    save_metrics_csv(protocol.metrics, group, protocol.name)
    save_downloaded_file(protocol.file_buffer,
                         f"downloaded_{file_type}_{protocol.name}_.bin",
                         protocol.expectedmd5)

    session.close()

if __name__ == "__main__":
    main()
