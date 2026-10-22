from __future__ import annotations

class Packet:

    def __init__(self, p_type: str) -> None:
        VALID_TYPES = {
            "HELLO",
            "OK",
            "REQ",
            "DATA",
            "ACK",
            "FIN",
            "DONE",
            "PING",
            "PONG",
            "ERROR",
        }
        if p_type not in VALID_TYPES:
            raise ValueError(f"Tipo de pacote inválido: {p_type}")

        self.type: str = p_type
        self._fields: dict[str, str | int] = {}
        self.payload: bytes = b""

    @property
    def seq(self) -> int:
        """Retorna o número de sequência como int."""
        val = self._fields.get("seq", 0)
        return int(val) if val is not None else 0

    @property
    def total_segments(self) -> int:
        """Retorna o total de segmentos (presente no OK)."""
        val = self._fields.get("total_segments", 0)
        return int(val) if val is not None else 0

    @property
    def checksum(self) -> str:
        """Retorna o md5/checksum."""
        return str(self._fields.get("checksum", ""))

    @property
    def payload_size(self) -> int:
        return len(self.payload)

    # --- MÉTODOS ESTÁTICOS DE CRIAÇÃO ---

    @staticmethod
    def hello(
        group: str, segment_size: int = 512, file_type: str = "small"
    ) -> Packet:
        if segment_size > 1024:
            raise ValueError("Tamanho de segmento máximo é 1024 bytes")
        if file_type not in ["small", "medium", "large"]:
            raise ValueError("file_type deve ser <small|medium|large>")

        p = Packet("HELLO")
        p._fields = {
            "grupo": group,
            "segment_size": segment_size,
            "file": file_type,
        }
        return p

    @staticmethod
    def req(seq: int) -> Packet:
        p = Packet("REQ")
        p._fields = {"seq": seq}
        return p

    @staticmethod
    def ack(seq: int) -> Packet:
        p = Packet("ACK")
        p._fields = {"seq": seq}
        return p

    @staticmethod
    def parse(raw_bytes: bytes) -> Packet:
        parts = raw_bytes.split(b"|")
        if not parts:
            raise ValueError("Pacote vazio")

        p_type = parts[0].decode("ascii")
        p = Packet(p_type)

        if p_type == "DATA":
            # DATA|seq=<n>|total=<bytes>|<payload_binário>[cite: 2]
            data_parts = raw_bytes.split(b"|", 3)

            for field in data_parts[1:3]:
                token = field.decode("ascii")
                if "=" in token:
                    k, v = token.split("=", 1)
                    p._fields[k] = int(v) if v.isdigit() else v

            p.payload = data_parts[3] if len(data_parts) > 3 else b""

        else:
            text = raw_bytes.decode("ascii", errors="ignore")
            tokens = text.split("|")[1:]
            for token in tokens:
                if "=" in token:
                    k, v = token.split("=", 1)
                    p._fields[k] = int(v) if v.isdigit() else v

        return p

    def __repr__(self) -> str:
        str_list = [self.type]
        str_list.extend([f"{k}={v}" for k, v in self._fields.items()])
        if self.payload:
            str_list.append(f"<{len(self.payload)} bytes>")
        return "|".join(str_list)

    def encode(self) -> bytes:
        header_str = str(self)
        header_bytes = header_str.encode("ascii")
        if self.payload:
            return header_bytes + b"|" + self.payload
        return header_bytes

    def get(self, field: str, fallback=None):
        return self._fields.get(field, fallback)
