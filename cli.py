# cli.py
import argparse

# id do grupo
GROUP = 'grupo13'

# parametros do servidor RDT-Unb
ADDR = '137.131.178.229'
PORT = 8080
MAX_SEGMENT_SIZE = 512

# cliente envia REQ
# aguarda pacote de DATA
# envia ACK e solicita proximo segmento 
# (timeout() -> retransmitir o REQ)
def create_parser() -> argparse.ArgumentParser:
    """
    Retorna um argparse.ArgumentParser capaz de lidar 
    com os argumentos opocionais --server, --file, e o 
    argumento obrigatório --group
    """
    parser = argparse.ArgumentParser('Cliente RDT-UnB')

    # servidor
    parser.add_argument(
        "--server", "-s",
        type=str,
        default=ADDR,
        help=f"IP de servidor de destino (padrão {ADDR})"
    )

    # tipo de arquivo
    parser.add_argument(
            "--file", "-f",
            type=str,
            choices=["small","medium","large"],
            default="small",
            help="Tamanho do arquivo (small, medium, large)"
    )

    # protocolo
    parser.add_argument(
            "--protocolo", "-p",
            type=str,
            choices=["saw","gbn","sr"],
            help="Protocolo (saw, gbn, sr)",
            required=True
    )
    
    # grupo
    parser.add_argument(
            "--group", "-g",
            type=str,
            help="Identificador do grupo",
            required=True
    )
    
    # perda da rede simulada
    parser.add_argument(
            "--loss", "-l",
            type=int,
            default=0,
            help="Perda (padrão 0%)",
    )

    # Tamanho da janela para gbn e sr
    parser.add_argument(
            "--window-size", "-w",
            type=int,
            default=8,
            help="Perda (padrão 8 - exceto SAW)",
    )

    return parser

def get_args() -> argparse.Namespace:
    """
    Retorna argumentos passados pela linha de comando
    (argparse.Namespace)
    """
    parser = create_parser()
    return parser.parse_args()

