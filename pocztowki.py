import sys
import argparse
import logging
from PIL import Image

# Given:
#  1. Print paper size
#  2. Passepartout size
#  3. Picture to be printed
# This tool will create an image with added white border of the right size so that input image will fit into the passepartout
# Aspect ratio of the image will be maintaned. If aspect ratio of picture is different than passepartout aspect ratio then:
#  1. (default) aspect fill algorithm will be used. Aspect fill will make sure that whole are of passepartout will be used but some part of the image will be covered by passepartout.
#  2. aspect fit can be used using --mode option. Aspect fit will make sure that whole image is visible but you will get white strips at the edges.


class Size:
    # helper class
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def print(self, name, unit):
        logging.info("%s size %d%s x %d%s", name, self.width, unit, self.height, unit)


def main(argv):
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument("image")
    parser.add_argument("-m", "--mode", required=False, default="aspectFill")
    parser.add_argument("-pw", "--paper_width", help="Paper width in mm", required=True)
    parser.add_argument("-ph", "--paper_height", help="Paper height in mm", required=True)
    parser.add_argument("-ppw", "--passepartout_width", help="Passepartout width in mm", required=True)
    parser.add_argument("-pph", "--passepartout_height", help="Passepartout height in mm", required=True)
    args = parser.parse_args()

    try:
        paperSize = Size(int(args.paper_width), int(args.paper_height))
        passepartoutSize = Size(int(args.passepartout_width), int(args.passepartout_height))
        inputImage = Image.open(args.image)
        inputImageSizePx = Size(int(inputImage.width), int(inputImage.height))
        inputImageSizePx.print("INPUT IMAGE", "px")

        outputImageSize = calculateOutputImageSize(inputImageSizePx, paperSize, passepartoutSize, args.mode)
        createOutputImage(outputImageSize, inputImage, "out_" + args.image)

    except FileNotFoundError:
        logging.error("File not found")


def calculateOutputImageSize(inputImageSizePx, paperSize, passpartoutSize, mode):
    # if image is in portrait orientation rotate paper and passpartout to portrait as well
    if inputImageSizePx.height > inputImageSizePx.width:
        paperSize = Size(paperSize.height, paperSize.width)
        passpartoutSize = Size(passpartoutSize.height, passpartoutSize.width)

    paperSize.print("PAPER", "mm")
    passpartoutSize.print("PASSPARTOUT", "mm")

    widthDensity = float(inputImageSizePx.width) / passpartoutSize.width
    heightDensity = float(inputImageSizePx.height) / passpartoutSize.height

    if mode == "aspectFill":
        pixelDensity = min(widthDensity, heightDensity)
    elif mode == "aspectFit":
        pixelDensity = max(widthDensity, heightDensity)
    else:
        raise ValueError("Invalid mode (%s)" % (mode))

    idealSize = Size(float(inputImageSizePx.width) / pixelDensity, float(inputImageSizePx.height) / pixelDensity)
    logging.info("Aspect ratio difference will cost you %dmm x %dmm of space",
                 passpartoutSize.width - idealSize.width, passpartoutSize.height - idealSize.height)
    logging.debug("   ideal size: %dmm x %dmm   density: %f", idealSize.width, idealSize.height, pixelDensity)

    additionalPixels = Size((paperSize.width - idealSize.width) * pixelDensity,
                            (paperSize.height - idealSize.height) * pixelDensity)
    logging.debug("   additionalPixels: %d x %d", additionalPixels.width, additionalPixels.height)

    assert(additionalPixels.width > 0)
    assert(additionalPixels.height > 0)
    finalSize = Size(inputImageSizePx.width + additionalPixels.width,
                     inputImageSizePx.height + additionalPixels.height)
    logging.debug("   final size: %dpx x %dpx", finalSize.width, finalSize.height)
    return finalSize


def createOutputImage(targetSize, inputImage, targetFilename):
    targetImageSize = (int(targetSize.width), int(targetSize.height))
    outputImage = Image.new("RGB", targetImageSize, (255, 255, 255))

    outputImage.paste(inputImage, (int((targetSize.width - inputImage.width)/2),
                                   int((targetSize.height - inputImage.height)/2)))
    outputImage.save(targetFilename)
    logging.info("Output image saved to %s", targetFilename)


if __name__ == "__main__":
    main(sys.argv[1:])
