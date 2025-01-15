import cv2 as cv
import numpy as np

#Adjusts the contrast of an image by clamping intensities, normalizing, 
# and applying gamma correction.
# Parameters:
# img: Input image (grayscale or color).
# lower: Lower intensity threshold for clamping.
# upper: Upper intensity threshold for clamping.
# gamma: Gamma value for gamma correction.
def increaseContrast(img, lower, upper, gamma):

    # Clamp the pixel intensities to the specified range [lower, upper]
    img[img > upper] = upper
    img[img < lower] = lower

    # Normalize the image to stretch the intensity range to [0, 255]
    img = cv.normalize(img, None, 0, 255, norm_type=cv.NORM_MINMAX, dtype=cv.CV_8UC1)

    # Create a lookup table for gamma correction
    lookUpTable = np.empty((1,256), np.uint8)
    for i in range(256):
        # Apply gamma correction formula and clip to [0, 255]
        lookUpTable[0,i] = np.clip(pow(i / 255.0, gamma) * 255.0, 0, 255)

    # Apply the lookup table to the image for gamma correction
    img = cv.LUT(img, lookUpTable)

    return img

