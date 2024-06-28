import glob
import os

import cv2
import time
import os
from emailing import send_email

video = cv2.VideoCapture(0)  # Initialize the video camera with the 1st camera
time.sleep(1)
first_frame = None
status_list = []
count = 1


def clean_folder():
    images = glob.glob("images/*.png")
    for image in images:
        os.remove()


while True:
    status = 0
    check, frame = video.read()

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Transform the frame intro gray
    gray_frame_gau = cv2.GaussianBlur(gray_frame, (21, 21), 0)

    if first_frame is None:
        first_frame = gray_frame_gau  # Very first frame

    # Difference between first frame and second frame, to recognize movement
    delta_frame = cv2.absdiff(first_frame, gray_frame_gau)

    thresh_frame = cv2.threshold(delta_frame, 60, 255, cv2.THRESH_BINARY)[1]
    dil_frame = cv2.dilate(thresh_frame, None, iterations=2)
    cv2.imshow("My video", dil_frame)

    contours, check = cv2.findContours(dil_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        if cv2.contourArea(contour) < 5000:
            continue
        x, y, w, h = cv2.boundingRect(contour)
        rectangle = cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
        if rectangle.any():
            status = 1
            cv2.imwrite(f"images/{count}.png", frame) # Create images only when an object enters the video
            count += 1
            all_images = glob.glob("images/*.png")
            index = int(len(all_images) / 2)
            image_with_object = all_images[index]

    status_list.append(status)
    status_list = status_list[-2:] # Picks the last 2 items

    if status_list[0] == 1 and status_list[1] == 0:
        send_email(image_with_object)
        clean_folder()

    print(status_list)

    cv2.imshow("Video", frame)
    key = cv2.waitKey(1)  # This creates a keyboard key

    if key == ord("q"):  # If the user presses q, the loop will break
        break

video.release()