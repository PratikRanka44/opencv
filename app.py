from flask import Flask, redirect, url_for, send_from_directory
import cv2
import numpy as np
import pyautogui
import threading
import os

app = Flask(__name__)

# Global flag to control the detection loop
running = False

def run_detection():
    global running
    cap = cv2.VideoCapture(0)  # Change to 1 if you have multiple webcams
    if not cap.isOpened():
        print("Error: Could not open video capture")
        return

    yellow_lower = np.array([22, 93, 0])
    yellow_upper = np.array([45, 255, 255])
    prev_y = 0
    min_area = 300  # Adjust this value to change the object size

    while running:
        ret, frame = cap.read()
        if not ret or frame is None:
            print("Error: Could not read frame")
            break

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, yellow_lower, yellow_upper)
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for c in contours:
            area = cv2.contourArea(c)
            if area > min_area:
                x, y, w, h = cv2.boundingRect(c)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                if y < prev_y:
                    pyautogui.press('space')
                prev_y = y

        cv2.imshow('frame', frame)
        if cv2.waitKey(10) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

@app.route('/')
def index():
    return send_from_directory(os.getcwd(), 'index.html')

@app.route('/run')
def run():
    global running
    running = True
    thread = threading.Thread(target=run_detection)
    thread.start()
    return redirect(url_for('index'))

@app.route('/stop')
def stop():
    global running
    running = False
    return redirect(url_for('index'))

# if __name__ == '__main__':
  #  app.run(debug=True, host='0.0.0.0', port=5000)
