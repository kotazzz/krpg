"""
Updater for krpg
"""
import glob
import os
import zlib

import urllib3

LINK = "https://raw.githubusercontent.com/kotazzz/krpg/master/"
FILES = ["krpg/**/*.py", "krpg/**/*.krpg", "krpg/*.*", "updater.py"]


def local_hashes() -> dict[str, int]:
    """Get local hashes of files

    Returns
    -------
    dict[str, int]
        dict with hashes
    """
    # find all files
    hashes = {}
    for i in FILES:
        # get all files by mask
        for j in glob.glob(i, recursive=True):
            # get hash
            with open(j, "rb") as f:
                j = j.replace("\\", "/")
                # CRLF -> LF
                fixed = f.read().replace(b"\r\n", b"\n")
                hashes[j] = zlib.crc32(fixed)
    return hashes


def get_hashes() -> dict[str, int]:
    """Get hashes from github

    Returns
    -------
    dict[str, int]
        dict with hashes

    Raises
    ------
    ValueError
        Can't get hashes
    """
    http = urllib3.PoolManager()
    r = http.request("GET", LINK + "hashes.json")
    if r.status == 200:
        return r.data
    raise ValueError("Can't get hashes")


def update():
    """Update krpg

    Raises
    ------
    ValueError
        Can't download file
    """
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
        url = LINK + i
        http = urllib3.PoolManager()
        r = http.request("GET", url)
        if r.status != 200:
            raise ValueError(f"Can't download {url}: {r.status}, {r.reason}")
        # create folders
        try:
            os.makedirs(os.path.dirname(i), exist_ok=True)
        except FileNotFoundError:
            print("Skipping folder creation")
        with open(i, "wb") as f:
            f.write(r.data.replace(b"\r\n", b"\n"))


def main():
    """Main function"""
    update()


if __name__ == "__main__":
    main()
