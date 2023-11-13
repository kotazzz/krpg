import requests
import os
import hashlib
import glob
link = "https://raw.githubusercontent.com/kotazzz/krpg/master/"
files = [
    "krpg/*.py",
    "scenario.krpg",
]

def local_hashes():
    # find all files
    hashes = {}
    for i in files:
        # get all files by mask
        for j in glob.glob(i):
            # get hash
            with open(j, "rb") as f:
                # hashes.append((j, hashlib.md5(f.read()).hexdigest()))
                hashes[j] = hashlib.md5(f.read()).hexdigest()
    return hashes

def get_hashes():
    r = requests.get(link + "hashes.json")
    if r.status_code == 200:
        return r.json()
    else:
        raise Exception("Can't get hashes")
    
def update():
    # get hashes from both sides
    local = local_hashes()
    remote = get_hashes()
    queue = []
    for i in local:
        if i not in remote:
            print(f"New file: {i}")
            queue.append(i)
        if local[i] != remote[i]:
            print(f"Updated: {i}")
            queue.append(i)
    for i in remote:
        if i not in local:
            print(f"Deleted: {i}")
            os.remove(i)
    for i in queue:
        print(f"Downloading: {i}")
        # download
        url = link + i
        r = requests.get(url)
        if r.status_code != 200:
            raise Exception(f"Can't download {url}: {r.status_code}, {r.reason}")
        # create folders
        os.makedirs(os.path.dirname(i), exist_ok=True)
        # save
        with open(i, "wb") as f:
            f.write(r.read())