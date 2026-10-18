from cli import MAX_SEGMENT_SIZE, get_args
from rdt_session import RDTSession
from stop_and_wait import StopAndWait
from metrics import save_metrics_csv
from file_manager import save_downloaded_file


PORT = 8080
MAX_SEGMENT_SIZE = 512

def main():
    args = get_args()
        
    # parametros para a comunicação
    server = (args.server, PORT)
    file_type = args.file 
    group = args.group

    # sessão RDT
    session = RDTSession(server)

    # protocolo de envio e retransmissão
    protocol = StopAndWait(session)
    
    # obter arquivo do servidor
    protocol.run(group, MAX_SEGMENT_SIZE, file_type)
    save_metrics_csv(protocol.metrics, group, "saw")
    save_downloaded_file(protocol.file_buffer, 
                         f"downloaded_{file_type}.bin", 
                         protocol.expectedmd5)

    session.close()

if __name__ == "__main__":
    main()
