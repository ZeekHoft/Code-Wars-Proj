import cv2 
from time import sleep
import pyautogui
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))


face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')


# eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml') 

# capture frames from a camera
cap = cv2.VideoCapture(0)

jump_line_y = 170
duck_line_y = 320
# loop runs if capturing has been initialized.


def print_action(x, y, w, h):
    center_y = y + h // 2  # Calculate face center Y-coordinate
    if center_y < jump_line_y:
        # sleep(0.5)
        pyautogui.press('up')
    elif center_y > duck_line_y:
        # sleep(0.5)
        pyautogui.press('down')






while True: 

    # reads frames from a camera
    ret, img = cap.read() 
    #jump

    # convert to gray scale of each frames
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Detects faces of different sizes in the input image
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    # print(f"face: {faces}")

    cv2.line(img,(0,170),(700,170),(255,0,0),5)

    #duck
    cv2.line(img,(0,320),(700,320),(0,255,0),5)


    for (x,y,w,h) in faces:
        # To draw a rectangle in a face 
        cv2.rectangle(img,(x,y),(x+w,y+h),(255,255,0),2) 
        print_action(x, y, w, h)

        # roi_gray = gray[y:y+h, x:x+w]
        # roi_color = img[y:y+h, x:x+w]

        # # Detects eyes of different sizes in the input image
        # eyes = eye_cascade.detectMultiScale(roi_gray) 
        # print(f"eyes: {eyes}")

        # #To draw a rectangle in eyes
        # for (ex,ey,ew,eh) in eyes:
        #     cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,127,255),2)

    # Display an image in a window
    cv2.imshow('img',img)

    # Wait for Esc key to stop
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break

# Close the window
cap.release()

# De-allocate any associated memory usage
cv2.destroyAllWindows()