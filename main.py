from cli import get_args
from rdt_core import run_rdt

def main():
    args = get_args()
    run_rdt(args)    

if __name__ == "__main__":
    main()
