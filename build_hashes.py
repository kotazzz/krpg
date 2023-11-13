import json
import updater
import glob
filename = "hashes.json"

def main():
    hashes = updater.local_hashes()
    print(*[f"{i}: {hashes[i]}" for i in hashes], sep="\n")
    with open(filename, "w") as f:
        json.dump(hashes, f, indent=4)

if __name__ == "__main__":
    main()