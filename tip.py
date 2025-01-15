import cv2 as cv
import numpy as np
import cvzone as cvz
from contour import *
import math
from angles import angles

# Function to calculate the angle between two vectors
def angleOfVectors(a,b,c,d):
     dotProduct = a*c + b*d # Dot product of the two vectors
     modOfVector = math.sqrt( a*a + b*b)*math.sqrt(c*c + d*d) # Magnitudes of the vectors
     angle = dotProduct/modOfVector # Cosine of the angle
     angleInDegree = math.degrees(math.acos(angle)) # Convert angle to degrees

     return angleInDegree

# Function to perform a perspective warp on the image
def warpImage(img, points):
    width, height = int(451 * 1.5), int(451 * 1.5) # 45.1 cm is the width of the board
    points = np.float32(points) # Coordinates of the sticky notes
    points2 = np.float32(
        [[0, height / 2, ], [width, height / 2], [width / 2, 0], [width / 2, height]]) #Correspondance points
    matrix = cv.getPerspectiveTransform(points, points2) # Compute the perspective transformation matrix
    imgOutput = cv.warpPerspective(img, matrix, (width, height)) # Warp the image using the transformation matrix

    return imgOutput

# Function to determine the score based on the dart hit position
def determinePoint(img):
    # Create a mask to detect the green dot representing the dart hit
    dots = cv.inRange(img, (0, 255, 0), (0, 255, 0))

    # Find contours in the mask
    dots, contourFound = cvz.findContours(dots, dots, 1)

    # Define key reference points on the dartboard
    boardCenter = (int(img.shape[0] / 2), int(img.shape[1] / 2)) # Center of the dartboard
    rightCenter = (int(img.shape[0]), int(img.shape[1] / 2)) # Center of the right edge of the board
    hit = (contourFound[0]['center']) # Coordinate of the tip of the dart

    # Normalize the hit position relative to the board center
    hitForDistance = [hit[0], hit[1]]
    hit[0] = hit[0] - boardCenter[0]
    hit[1] = hit[1] - boardCenter[1]
    hit[1] = -1 * hit[1]

    # Calculate the angle between the dart hit and the right center of the board
    angle = angleOfVectors(hit[0], hit[1], rightCenter[0], 0)

    if hit[1] < 0:
        angle = 360 - angle # Adjust angle for hits below the x-axis

    # Calculate the distance of the dart hit from the board center
    ratio = 53.6 / rightCenter[0] # Ratio between the real distance and the image distance
    norm = (hitForDistance[0] - boardCenter[0], hitForDistance[1] - boardCenter[1])
    dist = cv.norm(norm)
    dist = dist * ratio # Distance in cm

    # Determine the score based on the angle and distance
    point = 0
    for ang in angles: # Iterate through the predefined angle ranges for scoring
        if ang[0][0] < angle and angle <= ang[0][1]:
            point = ang[1]
            break

    # Adjust the score based on the distance
    if 17 < dist:
        point = 0 * point # Missed board
    elif dist <= 0.635:
        point = 50 # Bullseye
    elif 0.635 < dist and dist <= 1.6:
        point = 25 # Outer bullseye
    elif 9.9 <= dist and dist <=10.7:
        point = 3 * point # Triple ring
    elif 16.2 <= dist and dist <= 17:
        point = 2 * point # Double ring

    return point

# Function to find the tip of the dart, the parameters are the coordinates of the sticky notes and the contours
def findTipOfArrow(points, cnts, boardContours, contourFound):
    AREA = 75 # Minimum contour area to consider
    correctCnts = []
    for cnt in cnts: # Filter contours by area
        if cv.contourArea(cnt) > AREA:
            correctCnts.append(cnt)

    # Extract x and y coordinates of the contours
    x_coordinates = []
    y_coordinates = []
    for i in range(len(contourFound)):
        x_coordinates.append(min(list(map(lambda x: x[0][0], contourFound[i]['cnt']))))
        y_coordinates.append(max(list(map(lambda y: y[0][1], contourFound[i]['cnt']))))

    # Find the coordinates of the dart tip
    x_coordinate = min(x_coordinates)
    y_coordinate = max(y_coordinates)

    # Mark the dart tip on the board image
    cv.circle(boardContours, (x_coordinate, y_coordinate), 3, (0, 255, 0), -1)
    cv.imwrite('Images/tip.jpg', boardContours)

    # Warp the image to make it look like the camera is in front of the board
    warped = warpImage(boardContours, points)
    cv.imwrite('Images/warped.jpg', warped)

    # Determine the score based on the warped image
    point = determinePoint(warped)
    return point
