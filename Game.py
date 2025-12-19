import random
import cv2
from cvzone.HandTrackingModule import HandDetector
import math
import numpy as np
import cvzone
import time

# Webcam
cap = cv2.VideoCapture(0)
cap.set(3, 1280) #width
cap.set(4, 720)  #height

# Hand Detector
detector=HandDetector(detectionCon=0.8, maxHands=1)

# Find Function Representing How Distance from the Screen in Centimeters Depend on the Distance Variable Shown Below for Points 5 and 17
x = [300, 245, 200, 170, 145, 130, 112, 103, 93, 87, 80, 75, 70, 67, 62, 59, 57] #distance variable's raw value between points 5 and 17
y = [20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100] #distance measured in centimeters

coff=np.polyfit(x, y, 2) #y=A*x^2+B*x+C

# Game Variables
cx, cy=250, 250 #setting initial arbitrary values
color=(255, 0, 255)
counter=0
score=0
timeStart=time.time()
totalTime=20 #20 seconds as total duration of the game

# Loop
while True:
    success, img = cap.read()
    img=cv2.flip(img, 1) #flip in the x axis

    if time.time()-timeStart<totalTime:
        hands = detector.findHands(img, draw=False)
        if hands:
            x, y, w, h = hands[0]['bbox']
            lmList = hands[0]['lmList']
            x1, y1, _ = lmList[5]
            x2, y2, _ = lmList[17]

            distance = int(math.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2))
            A, B, C = coff
            distanceCM = A * distance ** 2 + B * distance + C
            # print(distanceCM, distance)

            if distanceCM < 40:
                if x < cx < x + w and y < cy < y + h:
                    counter = 1

            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 255), 3)
            cvzone.putTextRect(img, f'{int(distanceCM)} cm', (x + 5, y - 10))

        if counter:
            counter += 1
            color = (0, 255, 0)
            if counter == 3:
                h, w, _ = img.shape
                margin = 40  # circle radius + safety
                cx = random.randint(margin, w - margin)
                cy = random.randint(margin, h - margin)
                color = (255, 0, 255)
                score += 1
                counter = 0

        # Draw Button
        cv2.circle(img, (cx, cy), 30, color, cv2.FILLED)
        cv2.circle(img, (cx, cy), 10, (255, 255, 255), cv2.FILLED)
        cv2.circle(img, (cx, cy), 20, (255, 255, 255), 2)
        cv2.circle(img, (cx, cy), 30, (50, 50, 50), 2)

        # Game Head-Up Display
        cvzone.putTextRect(img, f'Time: {int(totalTime-(time.time()-timeStart))}', (450, 75), scale=2, offset=10)
        cvzone.putTextRect(img, f'Score: {str(score).zfill(2)}', (50, 75), scale=2, offset=10)
    else:
        cvzone.putTextRect(img, 'Game Over', (200, 250), scale=3, offset=30, thickness=5)
        cvzone.putTextRect(img, f'Your Score: {score}', (220, 330), scale=2, offset=20, thickness=5)
        cvzone.putTextRect(img, 'Press R to restart', (180, 390), scale=2, offset=10, thickness=5)

    cv2.imshow("Image", img)
    key = cv2.waitKey(1)

    if key==ord('r'):
        timeStart=time.time()
        score=0
