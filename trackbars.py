#This code is not part of the final solution. 
# The idea was to split the board into regions (multiplier regions) based on the colors.

from turtle import color
import cv2 as cv
import numpy as np
from tkinter import *
import cvzone as cvz

class Colors:
    black_lower = []
    black_upper = []

    red_lower = []
    red_upper = []

    green_lower = []
    green_upper = []

    blue_lower = []
    blue_upper = []

colors = Colors()

def warpImage(img, points):
    width, height = int(451 * 1.5), int(451 * 1.5)
    points = np.float32(points)
    points2 = np.float32(
        [[0, height / 2, ], [width, height / 2], [width / 2, 0], [width / 2, height]])
    matrix = cv.getPerspectiveTransform(points, points2)
    imgOutput = cv.warpPerspective(img, matrix, (width, height))

    return imgOutput

def findCenterPointsOfPostIt(mask):
    board = cv.imread('Images/calibration.jpg')
    board_contours, contourFound = cvz.findContours(board, mask, 50)

    if len(contourFound) >= 4:
        centers = list(map(lambda x: x['center'], contourFound))
        x_coordinates = list(map(lambda x: x['center'][0], contourFound))
        y_coordinates = list(map(lambda x: x['center'][1], contourFound))
        left_x = min(x_coordinates)
        right_x = max(x_coordinates)
        top_y = min(y_coordinates)
        bottom_y = max(y_coordinates)
        left = next(c for c in centers if c[0] == left_x) 
        right = next(c for c in centers if c[0] == right_x)
        top = next(c for c in centers if c[1] == top_y)
        bottom = next(c for c in centers if c[1] == bottom_y) 
            
        points = np.array([left, right, top, bottom])
        
        return points

def showBlack():
    board = cv.imread('Images/calibration.jpg')
    board_mask = cv.inRange(board, (black_lower_B.get(), black_lower_G.get(), black_lower_R.get()), (black_upper_B.get(), black_upper_G.get(), black_upper_R.get()))
    cv.imshow('Black', board_mask)

    cv.waitKey(0)

def showRed():
    board = cv.imread('Images/calibration.jpg')
    #board = cv.cvtColor(board, cv.COLOR_BGR2HSV)
    board_mask = cv.inRange(board, (red_lower_B.get(), red_lower_G.get(), red_lower_R.get()), (red_upper_B.get(), red_upper_G.get(), red_upper_R.get()))
    cv.imshow('Red', board_mask)

    cv.waitKey(0)

def showGreen():
    board = cv.imread('Images/calibration.jpg')
    board = cv.cvtColor(board, cv.COLOR_BGR2HSV)
    board_mask = cv.inRange(board, (green_lower_B.get(), green_lower_G.get(), green_lower_R.get()), (green_upper_B.get(), green_upper_G.get(), green_upper_R.get()))
    cv.imshow('Green', board_mask)

    cv.waitKey(0)

def showBlue():
    board = cv.imread('Images/calibration.jpg')
    post_it_mask = cv.inRange(board, (blue_lower_B.get(), blue_lower_G.get(), blue_lower_R.get()), (blue_upper_B.get(), blue_upper_G.get(), blue_upper_R.get()))
    cv.imshow('Blue', post_it_mask)

    cv.waitKey(0)

def getMaskOfSpecificColor(board, board_mask, post_it_mask, lower, upper):
    mask = cv.inRange(board, lower, upper)
    cv.imwrite('Images/Zones/original_mask.jpg', mask)

    mask = cv.bitwise_and(board_mask, mask)
    mask = cv.subtract(mask, post_it_mask)
    cv.imwrite('Images/Zones/botwise_and.jpg', mask)

    cnts = cv.findContours(mask, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)[-2]
    canvas = np.zeros(mask.shape)
    
    AREA = 75
    for cnt in cnts:
        if cv.contourArea(cnt) > AREA:
            cv.drawContours(canvas, [cnt], -1, (255,255,255), thickness=cv.FILLED)

    return canvas

def findZones():
    board = cv.imread('Images/calibration.jpg')
    board_hsv = cv.cvtColor(board, cv.COLOR_BGR2HSV)
    board_mask = cv.inRange(board, colors.black_lower, colors.black_upper)
    post_it_mask = cv.inRange(board, colors.blue_lower, colors.blue_upper)
    cv.imshow('Original board', board_mask)
    cv.imshow('Post it mask', post_it_mask)

    kernel = np.ones((8, 8), np.uint8)
    board_mask = cv.dilate(board_mask, kernel, iterations=10)
    board_mask = cv.erode(board_mask, kernel, iterations=10)
    cv.imshow('Board mask', board_mask)

    red_mask = getMaskOfSpecificColor(board, board_mask, post_it_mask, colors.red_lower, colors.red_upper)
    cv.imshow('Red mask', red_mask)

    green_mask = getMaskOfSpecificColor(board_hsv, board_mask, post_it_mask, colors.green_lower, colors.green_upper)
    cv.imshow('Green mask', green_mask)

    green_mask = cv.subtract(green_mask, red_mask)
    
    cv.waitKey(0)

def saveColorValues():
    black.quit()
    red.quit()
    green.quit()
    blue.quit()

    colors.black_lower = (black_lower_B.get(), black_lower_G.get(), black_lower_R.get())
    colors.black_upper = (black_upper_B.get(), black_upper_G.get(), black_upper_R.get())

    colors.red_lower = (red_lower_B.get(), red_lower_G.get(), red_lower_R.get())
    colors.red_upper = (red_upper_B.get(), red_upper_G.get(), red_upper_R.get())

    colors.green_lower = (green_lower_B.get(), green_lower_G.get(), green_lower_R.get())
    colors.green_upper = (green_upper_B.get(), green_upper_G.get(), green_upper_R.get())

    colors.blue_lower = (blue_lower_B.get(), blue_lower_G.get(), blue_lower_R.get())
    colors.blue_upper = (blue_upper_B.get(), blue_upper_G.get(), blue_upper_R.get())

    findZones()

def findCenter():
    cam = cv.VideoCapture(0)

    colors.blue_lower = (blue_lower_B.get(), blue_lower_G.get(), blue_lower_R.get())
    colors.blue_upper = (blue_upper_B.get(), blue_upper_G.get(), blue_upper_R.get())

    while True:
        check, board = cam.read()

        post_it_mask = cv.inRange(board, colors.blue_lower, colors.blue_upper)
        points = findCenterPointsOfPostIt(post_it_mask)
        cv.line(board, points[0], points[1], [0, 255, 0], 2)
        cv.line(board, points[2], points[3], [0, 255, 0], 2)
        
        #board = warpImage(board, points)
        cv.imshow('Board', board)

        key = cv.waitKey(1)
        if key == 27:
            break

    cam.release()



camera = cv.VideoCapture(0)
result, image = camera.read()
if result:
    cv.imwrite('Images/calibration.jpg', image)

black = Tk()
black_lower_B = Scale(black, from_=0, to=255, length=400, orient=HORIZONTAL)
black_lower_B.set(0)
black_lower_B.pack()
black_lower_G = Scale(black, from_=0, to=255, length=400, orient=HORIZONTAL)
black_lower_G.set(0)
black_lower_G.pack()
black_lower_R = Scale(black, from_=0, to=255, length=400, orient=HORIZONTAL)
black_lower_R.set(0)
black_lower_R.pack()

black_upper_B = Scale(black, from_=0, to=255, length=400, orient=HORIZONTAL)
black_upper_B.set(25)
black_upper_B.pack()
black_upper_G = Scale(black, from_=0, to=255, length=400, orient=HORIZONTAL)
black_upper_G.set(25)
black_upper_G.pack()
black_upper_R = Scale(black, from_=0, to=255, length=400, orient=HORIZONTAL)
black_upper_R.set(25)
black_upper_R.pack()
Button(black, bg="black", text='Show black', command=showBlack).pack()
Button(black, text='Find center', command=findCenter).pack()
Button(black, text='Start', command=saveColorValues).pack()

red = Tk()
red_lower_B = Scale(red, from_=0, to=255, length=400, orient=HORIZONTAL)
red_lower_B.set(30)
red_lower_B.pack()
red_lower_G = Scale(red, from_=0, to=255, length=400, orient=HORIZONTAL)
red_lower_G.set(10)
red_lower_G.pack()
red_lower_R = Scale(red, from_=0, to=255, length=400, orient=HORIZONTAL)
red_lower_R.set(100)
red_lower_R.pack()

red_upper_B = Scale(red, from_=0, to=255, length=400, orient=HORIZONTAL)
red_upper_B.set(100)
red_upper_B.pack()
red_upper_G = Scale(red, from_=0, to=255, length=400, orient=HORIZONTAL)
red_upper_G.set(100)
red_upper_G.pack()
red_upper_R = Scale(red, from_=0, to=255, length=400, orient=HORIZONTAL)
red_upper_R.set(255)
red_upper_R.pack()
Button(red, bg="red", text='Show red', command=showRed).pack()
Button(red, text='Start', command=saveColorValues).pack()


green = Tk()
green_lower_B = Scale(green, from_=0, to=255, length=400, orient=HORIZONTAL)
green_lower_B.set(52)
green_lower_B.pack()
green_lower_G = Scale(green, from_=0, to=255, length=400, orient=HORIZONTAL)
green_lower_G.set(52)
green_lower_G.pack()
green_lower_R = Scale(green, from_=0, to=255, length=400, orient=HORIZONTAL)
green_lower_R.set(52)
green_lower_R.pack()

green_upper_B = Scale(green, from_=0, to=255, length=400, orient=HORIZONTAL)
green_upper_B.set(161)
green_upper_B.pack()
green_upper_G = Scale(green, from_=0, to=255, length=400, orient=HORIZONTAL)
green_upper_G.set(200)
green_upper_G.pack()
green_upper_R = Scale(green, from_=0, to=255, length=400, orient=HORIZONTAL)
green_upper_R.set(140)
green_upper_R.pack()
Button(green, bg="green", text='Show green', command=showGreen).pack()
Button(green, text='Start', command=saveColorValues).pack()


blue = Tk()
blue_lower_B = Scale(blue, from_=0, to=255, length=400, orient=HORIZONTAL)
blue_lower_B.set(96)
blue_lower_B.pack()
blue_lower_G = Scale(blue, from_=0, to=255, length=400, orient=HORIZONTAL)
blue_lower_G.set(74)
blue_lower_G.pack()
blue_lower_R = Scale(blue, from_=0, to=255, length=400, orient=HORIZONTAL)
blue_lower_R.set(13)
blue_lower_R.pack()

blue_upper_B = Scale(blue, from_=0, to=255, length=400, orient=HORIZONTAL)
blue_upper_B.set(215)
blue_upper_B.pack()
blue_upper_G = Scale(blue, from_=0, to=255, length=400, orient=HORIZONTAL)
blue_upper_G.set(157)
blue_upper_G.pack()
blue_upper_R = Scale(blue, from_=0, to=255, length=400, orient=HORIZONTAL)
blue_upper_R.set(105)
blue_upper_R.pack()
Button(blue, bg="blue", text='Show blue', command=showBlue).pack()
Button(blue, text='Start', command=saveColorValues).pack()


mainloop()


