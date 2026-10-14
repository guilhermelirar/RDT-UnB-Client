import hashlib

def save_downloaded_file(file_buffer: list[bytes], filename: str) -> str:
    full_content = b"".join(file_buffer)
    
    with open(filename, "wb") as f:
        f.write(full_content)
        
    md5_hash = hashlib.md5(full_content).hexdigest()
    return md5_hash
