#pad to 300
def pad(byte):
    diff = 2000-len(byte)
    byte += b"\0"* diff
    assert len(byte) == 2000
    return byte
#unpad
def unpad(byte):
    assert len(byte) == 2000
    to_ret = b''
    for b in byte:
        if(bytes([b]) != b'\0'):
            to_ret+=bytes([b])
    return to_ret