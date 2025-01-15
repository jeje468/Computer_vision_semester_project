import cv2

#Function is used to capture images for camera calibration
def captureImages():
    cap = cv2.VideoCapture(1) 
    img_counter = 0 

    while True:
        ret, frame = cap.read() 
        if not ret:
            break

        cv2.imshow("Camera", frame) 

        key = cv2.waitKey(1) & 0xFF 

        if key == 27:  
            break
        elif key == 32: 
            img_name = "Images/Calibration_images/{}.jpg".format(img_counter) 
            cv2.imwrite(img_name, frame)
            img_counter += 1
 
    cap.release() 
    cv2.destroyAllWindows()

captureImages()
