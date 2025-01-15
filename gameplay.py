import cv2 as cv
from contour import *
from tip import *
from camera_calibration import *

# Function to start the dart game, using the provided points for calibration
def startGame(points, camera_matrix, dist_coefs, newcameramtx, roi):
    cam = cv.VideoCapture(1)
    countHit = 0 # Counter to track the number of dart hits detected. Hit is only detected if the dart is visible on at least 5 frames (it didn't fall off)
    frame = 1 # Counter used to copy the current image into the previous image variable for the first frame

    while True:
        check, board = cam.read()
        board = undistortImage(board, camera_matrix, dist_coefs, newcameramtx, roi) #Undistort the image
        # If it is the first frame there was no previous frame so the current frame is copied
        if frame == 1:
            previous = board.copy()
            frame += 1
        
        # Save the current frame and previous frame to files
        cv.imwrite('Images/board.jpg', board)
        cv.imwrite('Images/previous.jpg', previous)
        # Display the current frame
        cv.imshow('Video', board)
        
        # Retrieve the dart contour using the current and previous frames. 
        # The last parameter is the upper bound of the size of the contour to detect.
        cnts, boardContours, contourFound = retrieveDartContour(previous, board, 200)
        

        if contourFound: # If a dart contour is detected
            countHit += 1  # Increment the hit counter
            if countHit == 5: # If the dart is visible on 5 consecutive frames it is a hit
                cv.imwrite('Images/hit.jpg', board) # Save the frame where the dart hit was detected

                # Find the tip of the dart relative to the calibration points
                point = findTipOfArrow(points, cnts, boardContours, contourFound)
                print(point)
                countHit = 0 # Reset the hit counter

                # Update the previous frame with the current frame 
                cv.imwrite('Images/previous.jpg', board)
                previous = board

        # Check for the 'ESC' key press to exit the game
        key = cv.waitKey(1)
        if key == 27:
            break
    
    #Release the camera resource
    cam.release()
