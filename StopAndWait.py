# StopAndWait.py
from RDTSession import RDTSession

class StopAndWait:
    def __init__(self, session: RDTSession) -> None:
        self.session = session

    def run(self, group: str, segment_size: int, file_type: str):
        ok_pkt = self.session.connect(group, segment_size, file_type)
        
        if ok_pkt:
            print(ok_pkt)   
