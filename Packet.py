# Packet.py
class Packet:
    def __init__(self, p_type: str) -> None:
        if p_type not in ["HELLO", "OK", 
                            "REQ", "DATA",
                            "ACK", "FIN", 
                            "DONE", "PING", 
                            "PONG"]:
            raise ValueError(f"Tipo de pacote inválido: {p_type}")
        
        self.type: str = p_type
        self._fields: dict = {}
        self.payload: bytes | None = None

    @staticmethod
    def hello(group: str, segment_size: int = 512, 
              file_type: str = "small") -> Packet:
        
        if segment_size > 1024:
            raise ValueError("Tamanho de segmento máximo é 1024 bytes")

        if file_type not in ["small", "medium", "large"]:
            raise ValueError("file_type deve ser <small|medium|large>")

        p = Packet("HELLO")
        p._fields = {
            "grupo": group, 
            "segment_size": segment_size,
            "file": file_type
        }
        
        return p

    def __repr__(self) -> str:
        str_list = [self.type]
        str_list.extend([f"{k}={self._fields[k]}" for k in self._fields])
        return "|".join(str_list) 

    def encode(self) -> bytes | None:
        return str(self).encode()
    
    def get(self, field: str):
        return self._fields.get(field)
