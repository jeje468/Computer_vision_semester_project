import cv2 as cv
import numpy as np
import cvzone as cvz
from contrast import *

# Function to retrieve the dart contour from the difference between two images
def retrieveDartContour(board, dart, area):

    # Save the original dart image for debugging
    cv.imwrite('Images/Contour_detection/1_original_board.jpg', dart)

    # Increase the contrast of both board and dart images
    board = increaseContrast(board, 20, 110, 0.4)
    dart = increaseContrast(dart, 20, 110, 0.4)
    cv.imwrite('Images/Contour_detection/2_image_with_increased_contrast.jpg', dart)

    # Compute the absolute difference between the two images
    diff = board.copy()
    cv.absdiff(board, dart, diff)
    gray = cv.cvtColor(diff, cv.COLOR_BGR2GRAY) # Convert the difference to grayscale
    cv.imwrite('Images/Contour_detection/3_difference.jpg', gray)

    # Further increase the contrast of the difference image
    res = increaseContrast(gray, 20, 160, 1.5)
    cv.imwrite('Images/Contour_detection/4_diff_image_with_increased_contrast.jpg', res)

    # Apply median blur to reduce noise (with varying kernel sizes)
    for i in range(1, 6, 2):
        res = cv.medianBlur(res, i)    
    cv.imwrite('Images/Contour_detection/5_median_blur.jpg', res)

    # Increase contrast again after blurring
    res = increaseContrast(res, 20, 160, 0.4)
    cv.imwrite('Images/Contour_detection/6_contrast_increase_after_median_blur.jpg', res)

    # Apply thresholding to create a binary mask
    (thresh, mask) = cv.threshold(res, 240, 255, cv.THRESH_OTSU)
    cv.imwrite('Images/Contour_detection/7_thresholding.jpg', mask)

    # Find contours in the binary mask
    cnts = cv.findContours(mask, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)[-2]
    contours = np.zeros(mask.shape)

    # Filter contours based on area and draw them
    for cnt in cnts:
        if cv.contourArea(cnt) > area: # Only consider contours larger than the specified area
            cv.drawContours(contours, [cnt], -1, (255,255,255), thickness=cv.FILLED)
    
    cv.imwrite('Images/Contour_detection/8_contours.jpg', contours)

    # Convert the contours image to a suitable format for further processing
    contours = contours.astype(np.uint8)
    boardContours, contours = cvz.findContours(dart, contours, 0)

    # Return all contours, board contours, and refined contours
    return cnts, boardContours, contours