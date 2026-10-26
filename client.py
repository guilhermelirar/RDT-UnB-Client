import hashlib
from socket import timeout
from cli import MAX_SEGMENT_SIZE, get_args
from rdt_session import RDTSession
from metrics import save_metrics_csv

from protocols.base_protocol import BaseProtocol
from protocols.go_back_n import GoBackN
from protocols.stop_and_wait import StopAndWait
from protocols.selective_repeat import SelectiveRepeat

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

def get_selected_protocol(args, session: RDTSession) -> BaseProtocol:
    if args.protocol == "saw":
        return StopAndWait(session)
    elif args.protocol == "gbn":
        return GoBackN(session, args.window_size)
    
    return SelectiveRepeat(session, args.window_size)

def main():
    args = get_args()

    # parametros para a comunicação
    server = (args.server, PORT)
    file_type = args.file
    group = args.group

    # sessão RDT
    session = RDTSession(server, timeout=0.6, simulated_loss=args.loss)
    protocol: BaseProtocol = get_selected_protocol(args, session)

    # obter arquivo do servidor
    protocol.run(group, MAX_SEGMENT_SIZE, file_type)

    valid_metrics = [m for m in protocol.metrics if m is not None]

    if valid_metrics:
      save_metrics_csv(
          valid_metrics,
          group,
          protocol.name,
          file_type,
          args.loss,
          protocol.window_size,
      )

    save_downloaded_file(protocol.file_buffer,
                         f"bin/downloaded_{file_type}_{protocol.name}_.bin",
                         protocol.expectedmd5)

    session.close()

if __name__ == "__main__":
    main()
