import hashlib

def save_downloaded_file(file_buffer: list[bytes], filename: str, 
                         expected_md5: str):
    full_content = b"".join(file_buffer)
    
    with open(filename, "wb") as f:
        f.write(full_content)
    
    md5_hash = hashlib.md5(full_content).hexdigest()
    
    if md5_hash == expected_md5:
        print("Checksum OK: ", md5_hash)
    else:
        print(f"[ERROR] Checksum difere: esperado '{expected_md5}',",
              "obtido '{md5_hash}'")

    return md5_hash

