from cli import MAX_SEGMENT_SIZE, get_args
from RDTSession import RDTSession
from StopAndWait import StopAndWait


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


if __name__ == "__main__":
    main()
