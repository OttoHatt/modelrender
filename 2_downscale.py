from PIL import Image
import sys


def main():
    fIn = sys.argv[1]
    fOut = sys.argv[2]
    resolution = int(sys.argv[3] if len(sys.argv) >= 4 else 128)

    image = Image.open(fIn)
    new = image.resize((resolution, resolution), Image.Resampling.HAMMING)

    new.save(fOut, "PNG")


if __name__ == "__main__":
    main()
