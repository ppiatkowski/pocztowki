import sys
import argparse
from PIL import Image


class Size:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def ratio(self):
        return float(self.width) / self.height

    def print(self, name, unit):
        print("%s size %d%s x %d%s (ratio=%f)" %
              (name, self.width, unit, self.height, unit, self.ratio()))


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("image")
    parser.add_argument("-m", "--mode", required=False, default="aspectFill")
    parser.add_argument("-pw", "--paper_width",
                        help="Paper width", required=True)
    parser.add_argument("-ph", "--paper_height",
                        help="Paper height", required=True)
    parser.add_argument("-iw", "--image_width",
                        help="Image width", required=True)
    parser.add_argument("-ih", "--image_height",
                        help="Image height", required=True)
    args = parser.parse_args()

    try:
        paperSize = Size(int(args.paper_width), int(args.paper_height))
        imageSize = Size(int(args.image_width), int(args.image_height))
        calculateExpandedImage(args.image, paperSize, imageSize, args.mode)
    except FileNotFoundError:
        print("File not found")


def calculateExpandedImage(filename, paperSize, imageSize, mode):
    print("mode: %s" % (mode))
    paperSize.print("PAPER", "mm")
    imageSize.print("IMAGE", "mm")

    heightRatio = float(imageSize.height) / paperSize.height
    widthRatio = float(imageSize.width) / paperSize.width

    if mode == "aspectFill":
        targetRatio = max(heightRatio, widthRatio)
    elif mode == "aspectFit":
        targetRatio = min(heightRatio, widthRatio)
    else:
        raise ValueError("Invalid mode")

    print("I/P w=%f h=%f targetRatio=%f" %
          (widthRatio, heightRatio, targetRatio))

    image = Image.open(filename)
    inputImageSize = Size(image.width, image.height)
    inputImageSize.print("INPUT IMAGE", "px")

    outputImageSize = Size(inputImageSize.width / targetRatio,
                           inputImageSize.height / targetRatio)
    outputImageSize.print("OUTPUT_IMAGE", "px")


if __name__ == "__main__":
    main(sys.argv[1:])
