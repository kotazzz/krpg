"""
Updater for krpg
"""

import glob
import json
import os
import zlib
from typing import Dict

import urllib3
from urllib3.response import BaseHTTPResponse

LINK = "https://raw.githubusercontent.com/kotazzz/krpg/master/"
FILES = ["krpg/**/*.py", "krpg/**/*.krpg", "krpg/*.*", "updater.py"]


def local_hashes() -> Dict[str, int]:
    """Get local hashes of files

    Returns
    -------
    Dict[str, int]
        dict with hashes
    """
    # find all files
    hashes: Dict[str, int] = {}
    for pattern in FILES:
        # get all files by mask
        for file_path in glob.glob(pattern, recursive=True):
            # get hash
            with open(file_path, "rb") as f:
                file_path = file_path.replace("\\", "/")
                # CRLF -> LF
                fixed = f.read().replace(b"\r\n", b"\n")
                hashes[file_path] = zlib.crc32(fixed)
    return hashes


def get_hashes() -> Dict[str, int]:
    """Get hashes from github

    Returns
    -------
    Dict[str, int]
        dict with hashes

    Raises
    ------
    ValueError
        Can't get hashes
    """
    http: urllib3.PoolManager = urllib3.PoolManager()
    r: BaseHTTPResponse = http.request("GET", LINK + "hashes.json")
    if r.status == 200:
        return json.loads(r.data.decode("utf-8"))
    raise ValueError("Can't get hashes")


def update() -> None:
    """Update krpg

    Raises
    ------
    ValueError
        Can't download file
    """
    # get hashes from both sides
    local: Dict[str, int] = local_hashes()
    remote: Dict[str, int] = get_hashes()

    queue: list[str] = []
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
        url: str = LINK + i
        http: urllib3.PoolManager = urllib3.PoolManager()
        r: BaseHTTPResponse = http.request("GET", url)
        if r.status != 200:
            raise ValueError(f"Can't download {url}: {r.status}, {r.reason}")
        # create folders
        try:
            os.makedirs(os.path.dirname(i), exist_ok=True)
        except FileNotFoundError:
            print("Skipping folder creation")
        with open(i, "wb") as f:
            f.write(r.data.replace(b"\r\n", b"\n"))


def main() -> None:
    """Main function"""
    update()


if __name__ == "__main__":
    main()
