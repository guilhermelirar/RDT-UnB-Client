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

    @staticmethod
    def parse(raw_bytes: bytes) -> Packet:
        # Separar tipo do resto do pacote
        parts = raw_bytes.split(b'|')
        if not parts:
            raise ValueError("Pacote vazio")
            
        p_type = parts[0].decode('ascii')
        p = Packet(p_type)

        if p_type == "DATA":
            # DATA|seq=<n>|total=<bytes>|<payload_binário>
            # pegar 3 splits para evitar dar split no binário
            data_parts = raw_bytes.split(b'|', 3)
            
            for field in data_parts[1:3]:
                k, v = field.decode('ascii').split('=')
                p._fields[k] = int(v) if v.isdigit() else v
                
            p.payload = data_parts[3] if len(data_parts) > 3 else b""
            
        else:
            # pacotes de ascii puro
            text = raw_bytes.decode('ascii', errors='ignore')
            tokens = text.split('|')[1:]
            for token in tokens:
                if '=' in token:
                    k, v = token.split('=', 1)
                    p._fields[k] = int(v) if v.isdigit() else v

        return p

    def __repr__(self) -> str:
        str_list = [self.type]
        str_list.extend([f"{k}={self._fields[k]}" for k in self._fields])
        return "|".join(str_list) 

    def encode(self) -> bytes:
        header_str = str(self)
        header_bytes = header_str.encode('ascii')
        
        if self.payload:
            return header_bytes + b"|" + self.payload
        return header_bytes
    
    def get(self, field: str):
        return self._fields.get(field)
