from pathlib import Path
import sys, json

if __name__ == "__main__":
    lookup = {}
    for local in sys.argv[1:-1]:
        fIn = Path(local)
        with fIn.open("r") as reader:
            lookup[fIn.stem] = reader.readline().strip()

    with Path(sys.argv[-1]).open("w") as writer:
        writer.write(json.dumps(lookup))
