import cv2
import numpy as np
import time
from imutils.perspective import four_point_transform

cap = cv2.VideoCapture(0 + cv2.CAP_DSHOW)

width, height = 800, 600

cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)


def scanDetection(image):
    global document_contour
    global max_area

    document_contour = np.array([[0, 0], [width, 0], [width, height], [0, height]])
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, threshold = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    contours, _ = cv2.findContours(threshold, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    max_area = 0
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 1000:
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.015 * peri, True)
            if area > max_area and len(approx) == 4:
                document_contour = approx
                max_area = area

    cv2.drawContours(frame, [document_contour], -1, (0, 255, 0), 3)


current_time = 0
Once = True
while True:
    ret, frame = cap.read()

    frame = cv2.resize(frame, (width, height))
    frame = cv2.flip(frame, 1)
    new_frame = frame.copy()

    scanDetection(new_frame)

    cv2.imshow("Webcam", frame)

    if max_area != 0:
        warped = four_point_transform(new_frame, document_contour.reshape(4, 2))
        cv2.imshow("Warped", warped)
        # if time.perf_counter() - preT >= 5 and Once:
        #     preT = time.perf_counter()
        #     Once = False
        #     cv2.imwrite("test.png", frame)
        #     break
    else:
        preT = time.perf_counter()

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
