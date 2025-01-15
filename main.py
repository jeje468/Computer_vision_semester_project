from tkinter import *
import cv2 as cv
import numpy as np
import cvzone as cvz
from gameplay import *
import os
from camera_calibration import *

# Function that returns the center points of the sticky notes
def setValues():
    points = [] #List to store the sticky notes
    camera = cv.VideoCapture(1)
    result, board = camera.read()
    board = undistortImage(board, camera_matrix, dist_coefs, newcameramtx, roi) # Undistort the image

    #If the calibration has been done before, the coordinates of the sticky notes are stored in this file
    path = "post_it_coordinates.txt"
    if os.path.exists(path):
        # If the file already exists read coordinates from the file and append them to the list
        with open(path, 'r') as f:
            for line in f:
                x, y = map(int, line.strip().split(','))
                points.append((x, y))
    
    else:
        # If the camera successfully captured a frame, save the captured image
        if result:
            cv.imwrite('Images/calibration.jpg', board)

        # Create a mask using the color ranges defined by the sliders
        maskPostIt = cv.inRange(board, (dark_B.get(),dark_G.get(),dark_R.get()), (light_B.get(),light_G.get(),light_R.get()))

        # Save and display the mask
        cv.imwrite('Images/post_it_mask.jpg', maskPostIt)
        cv.imshow('Mask', maskPostIt)

        # Find the center points of the sticky notes from the mask
        points = findCenterPointsOfPostIt(board, maskPostIt)

        #Save the points to the file, so next time it can be simply read from the file
        with open(path, 'w') as f:
            for x, y in points:
                f.write(f"{x},{y}\n")

    # If exactly 4 points are detected, draw lines between them for validation, 
    # save the image and display it so the player can validate it
    if len(points) == 4:
            cv.line(board, points[0], points[1], [0, 255, 0], 2)
            cv.line(board, points[2], points[3], [0, 255, 0], 2)
            cv.imwrite('Images/center_of_board.jpg', board)
            cv.imshow('Center', board)

    return points

# Function to find the center points of the sticky notes
def findCenterPointsOfPostIt(board, mask):
    #Detect the contours on the board based on the mask. The two parameters are the 
    # upper and lower bound of the size of the contours
    board_contours, contours = cvz.findContours(board, mask, 500, 2000)

    # Ensure at least 4 contours are found
    if len(contours) >= 4:
        # Extract the centers of the contours
        centers = list(map(lambda x: x['center'], contours))

        # Extract x and y coordinates of the centers
        x_coordinates = list(map(lambda x: x['center'][0], contours))
        y_coordinates = list(map(lambda x: x['center'][1], contours))

        # Identify the extreme points (left, right, top, bottom)
        left_x = min(x_coordinates)
        right_x = max(x_coordinates)
        top_y = min(y_coordinates)
        bottom_y = max(y_coordinates)

        #Based on the extreme points identify the coordinates of the centers of the post its
        left = next(c for c in centers if c[0] == left_x) 
        right = next(c for c in centers if c[0] == right_x)
        top = next(c for c in centers if c[1] == top_y)
        bottom = next(c for c in centers if c[1] == bottom_y) 
            
        # Store the points in an array
        points = np.array([left, right, top, bottom])
        
        return points

# Function to start the game
def start():
    points = setValues() # Get the sticky note coordinates
    cv.destroyAllWindows() # Close all OpenCV windows
    startGame(points, camera_matrix, dist_coefs, newcameramtx, roi) # Start the game using the coordinates

#Run camera calibration
camera_matrix, dist_coefs, newcameramtx, roi = calibrateCamera()
# Create the GUI window for calibration sliders
master = Tk()
# Define sliders for dark color ranges
dark_B = Scale(master, from_=0, to=255, length=400, orient=HORIZONTAL)
dark_B.set(7)
dark_B.pack()
dark_G = Scale(master, from_=0, to=255, length=400, orient=HORIZONTAL)
dark_G.set(6)
dark_G.pack()
dark_R = Scale(master, from_=0, to=255, length=400, orient=HORIZONTAL)
dark_R.set(8)
dark_R.pack()

# Define sliders for light color ranges
light_B = Scale(master, from_=0, to=255, length=400, orient=HORIZONTAL)
light_B.set(105)
light_B.pack()
light_G = Scale(master, from_=0, to=255, length=400, orient=HORIZONTAL)
light_G.set(90)
light_G.pack()
light_R = Scale(master, from_=0, to=255, length=400, orient=HORIZONTAL)
light_R.set(69)
light_R.pack()

# Add buttons to the GUI for calibration and starting the game
Button(master, text='Show', command=setValues).pack()
Button(master, text='Start game', command=start).pack()

# Run the GUI main loop
mainloop()
