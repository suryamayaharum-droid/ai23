import hashlib
from pathlib import Path

def sha256(path,chunk=1024*1024):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(chunk),b""): h.update(b)
    return h.hexdigest()

def asset_uri(project,kind,name,version=1):
    safe=lambda s:str(s).strip().replace(" ","_").replace("/","_")
    return f"harum://{safe(project)}/{safe(kind)}/{safe(name)}?v={int(version)}"
