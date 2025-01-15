#This is not part of the final solution. The idea was to draw a line 
# through the middle of the contour and determine the tip using this line.

import re
from tkinter import Y
import cv2 as cv
import cvzone as cvz
import numpy as np
from contour import retrieveDartContour
from contrast import *

def extendLine(p1, p2, distance = 10000):
    diff = np.arctan2(p1[1] - p2[1], p1[0] - p2[0])
    p3_x = int(p1[0] + distance * np.cos(diff))
    p3_y = int(p1[1] + distance * np.sin(diff))
    p4_x = int(p1[0] - distance * np.cos(diff))
    p4_y = int(p1[1] - distance * np.sin(diff))
    return ((p3_x, p3_y), (p4_x, p4_y))

board = cv.imread('Images/previous.jpg')
dart = cv.imread('Images/hit.jpg')

cnts, board_contours, contourFound = retrieveDartContour(board, dart, 20)

AREA = 75
correct_cnts = []
for cnt in cnts:
    if cv.contourArea(cnt) > AREA:
        correct_cnts.append(cnt)
        M = cv.moments(cnt)
        lX = int(M["m10"] / M["m00"])
        lY = int(M["m01"] / M["m00"])
        cv.circle(board_contours, (lX, lY), 3, (0, 255, 0), -1)


x_coordinates = []
y_coordinates = []
for i in range(len(contourFound)):
    x_coordinates.append(min(list(map(lambda x: x[0][0], contourFound[i]['cnt']))))
    y_coordinates.append(max(list(map(lambda y: y[0][1], contourFound[i]['cnt']))))

x_coordinate = min(x_coordinates)
y_coordinate = max(y_coordinates)

if len(correct_cnts) > 1:
    first_cnt_center = cv.moments(correct_cnts[0])
    last_cnt_center = cv.moments(correct_cnts[len(correct_cnts) - 1])
    fX = int(first_cnt_center["m10"] / first_cnt_center["m00"])
    fY = int(first_cnt_center["m01"] / first_cnt_center["m00"])
    lX = int(last_cnt_center["m10"] / last_cnt_center["m00"])
    lY = int(last_cnt_center["m01"] / last_cnt_center["m00"])
    cv.line(board_contours, (fX, fY), (lX, lY), [0, 255, 0], 2)
else:
    # p3, p4 = extendLine(contourFound[0]['center'], (x_coordinate, y_coordinate))
    cnt_center = cv.moments(correct_cnts[0])
    fX = int(cnt_center["m10"] / cnt_center["m00"])
    fY = int(cnt_center["m01"] / cnt_center["m00"])
    cv.line(board_contours, (fX, fY), (x_coordinate, y_coordinate), [0, 255, 0], 2)
    
cv.circle(board_contours, (x_coordinate, y_coordinate), 3, (0, 255, 0), -1)
cv.imwrite('Images/tip.jpg', board_contours)

cv.imshow('Contours', board_contours)

cv.waitKey(0)