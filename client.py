import hashlib
from socket import timeout

from cli import MAX_SEGMENT_SIZE, get_args
from metrics import save_metrics_csv
from protocols.base_protocol import BaseProtocol
from protocols.go_back_n import GoBackN
from protocols.selective_repeat import SelectiveRepeat
from protocols.stop_and_wait import StopAndWait
from rdt_session import RDTSession

PORT = 8080


def get_selected_protocol(args, session: RDTSession) -> BaseProtocol:
    if args.protocol == "saw":
        return StopAndWait(session)
    elif args.protocol == "gbn":
        return GoBackN(session, args.window_size)

    return SelectiveRepeat(session, args.window_size)


def file_hash(file: bytes):
    pass


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
    content: bytes = protocol.get_content()
    md5: str = hashlib.md5(content).hexdigest().lower()

    # confirmação
    if protocol.finalize_transfer(md5):
        """
        save_metrics_csv(
            protocol.metrics,
            group,
            protocol.name,
            file_type,
            args.loss,
            protocol.window_size,
        )
        """
        print(f"Checksum OK ({md5})")
        if mc := protocol.metrics_collector:
            mc.print_summary()

        with open(f"{file_type}.bin", "wb") as f:
            f.write(content)
        return

    print(f"ERRO: Checksum não confere ({md5}). Arquivo descartado")


if __name__ == "__main__":
    main()
