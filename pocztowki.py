import sys
import argparse
import logging
from PIL import Image


class Size:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def print(self, name, unit):
        logging.info("%s size %d%s x %d%s", name, self.width, unit, self.height, unit)


def main(argv):
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument("image")
    parser.add_argument("-m", "--mode", required=False, default="aspectFill")
    parser.add_argument("-pw", "--paper_width", help="Paper width", required=True)
    parser.add_argument("-ph", "--paper_height", help="Paper height", required=True)
    parser.add_argument("-iw", "--image_width", help="Image width", required=True)
    parser.add_argument("-ih", "--image_height", help="Image height", required=True)
    args = parser.parse_args()

    try:
        paperSize = Size(int(args.paper_width), int(args.paper_height))
        imageSize = Size(int(args.image_width), int(args.image_height))
        inputImage = Image.open(args.image)
        inputImageSize = Size(int(inputImage.width), int(inputImage.height))
        inputImageSize.print("INPUT IMAGE", "px")

        outputImageSize = calculateOutputImageSize(inputImageSize, paperSize, imageSize, args.mode)
        createOutputImage(outputImageSize, inputImage, "out_" + args.image)

    except FileNotFoundError:
        logging.error("File not found")


def calculateOutputImageSize(inputImageSize, paperSize, passpartoutSize, mode):
    # if image is in portrait orientation rotate paper and passpartout to portrait as well
    if inputImageSize.height > inputImageSize.width:
        paperSize = Size(paperSize.height, paperSize.width)
        passpartoutSize = Size(passpartoutSize.height, passpartoutSize.width)

    paperSize.print("PAPER", "mm")
    passpartoutSize.print("PASSPARTOUT", "mm")

    widthDensity = float(inputImageSize.width) / passpartoutSize.width
    heightDensity = float(inputImageSize.height) / passpartoutSize.height

    # TODO extract to function that returns ideal size
    if mode == "aspectFill":
        if widthDensity < heightDensity:
            pixelDensity = widthDensity
            idealHeight = float(inputImageSize.height) / pixelDensity
            idealSize = Size(passpartoutSize.width, idealHeight)
        else:
            pixelDensity = heightDensity
            idealWidth = float(inputImageSize.width) / pixelDensity
            idealSize = Size(idealWidth, passpartoutSize.height)
    elif mode == "aspectFit":
        raise ValueError("aspectFit not supported yet")
    else:
        raise ValueError("Invalid mode (%s)" % (mode))

    logging.info("Lost image part %dmm x %dmm", passpartoutSize.width - idealSize.width, passpartoutSize.height - idealSize.height)
    logging.debug("   ideal size: %dmm x %dmm   density: %f", idealSize.width, idealSize.height, pixelDensity)

    additionalPixels = Size((paperSize.width - idealSize.width) * pixelDensity,
                            (paperSize.height - idealSize.height) * pixelDensity)
    logging.debug("   additionalPixels: %d x %d", additionalPixels.width, additionalPixels.height)

    assert(additionalPixels.width > 0)
    assert(additionalPixels.height > 0)
    finalSize = Size(inputImageSize.width + additionalPixels.width,
                     inputImageSize.height + additionalPixels.height)
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
