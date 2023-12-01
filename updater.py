import urllib3
import os
import zlib
import glob

link = "https://raw.githubusercontent.com/kotazzz/krpg/master/"
files = ["krpg/**/*.py", "krpg/**/*.krpg", "krpg/*.*", "updater.py"]


def local_hashes():
    # find all files
    hashes = {}
    for i in files:
        # get all files by mask
        for j in glob.glob(i, recursive=True):
            # get hash
            with open(j, "rb") as f:
                j = j.replace("\\", "/")
                # CRLF -> LF
                fixed = f.read().replace(b"\r\n", b"\n")
                hashes[j] = zlib.crc32(fixed)
    return hashes


def get_hashes():
    http = urllib3.PoolManager()
    r = http.request("GET", link + "hashes.json")
    if r.status == 200:
        return r.data
    else:
        raise Exception("Can't get hashes")


def update():
    # get hashes from both sides
    local = local_hashes()
    remote = get_hashes()

    queue = []
    for i in remote:
        if i not in local:
            print(f"New file: {i}")
            queue.append(i)
        elif local[i] != remote[i]:
            print(f"Updated: {i}")
            queue.append(i)
    for i in local:
        if i not in remote:
            print(f"Deleted: {i}")
            os.remove(i)
    if not queue:
        print("Nothing to update")
        return
    for i in queue:
        print(f"Downloading: {i}")
        # download
        url = link + i
        http = urllib3.PoolManager()
        r = http.request("GET", url)
        if r.status != 200:
            raise Exception(f"Can't download {url}: {r.status}, {r.reason}")
        # create folders
        try:
            os.makedirs(os.path.dirname(i), exist_ok=True)
        except FileNotFoundError:
            print("Skipping folder creation")
        with open(i, "wb") as f:
            f.write(r.data.replace(b"\r\n", b"\n"))


def main():
    update()


if __name__ == "__main__":
    main()