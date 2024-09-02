import threading
import cv2
import numpy as np
import time
import os
from camera import setup_camera, get_frame
from gui import run_gui
import requests
from datetime import datetime

def load_known_faces(image_paths):
    known_faces = []
    for path in image_paths:
        image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        known_faces.append(image)
    return known_faces

def send_telegram_message(bot_token, chat_id, message, image_path=None):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message
    }
    response = requests.post(url, data=data)
    
    if image_path:
        url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
        with open(image_path, 'rb') as photo:
            files = {'photo': photo}
            data = {'chat_id': chat_id}
            response = requests.post(url, data=data, files=files)
    
    return response.json()

def detect_person(known_faces, pipeline, window, bot_token, chat_id):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    detection_start_time = None
    warning_sent = False
    
    # Ensure debug folder exists
    os.makedirs("./debug", exist_ok=True)

    while True:
        frame = get_frame(pipeline)
        if frame is None:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        mao_detected = False
        for (x, y, w, h) in faces:
            face_roi = gray[y:y+h, x:x+w]
            face_roi = cv2.resize(face_roi, (100, 100))

            for known_face in known_faces:
                result = cv2.matchTemplate(face_roi, known_face, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, _ = cv2.minMaxLoc(result)
                if max_val > 0.6:
                    mao_detected = True
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                    break

            if mao_detected:
                break

        if mao_detected:
            window.comm.update_status.emit("<font color='red' size='20'>Mao laoshi Laile</font>")
            if not warning_sent:
                # Save image with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                image_path = f"./debug/mao_detected_{timestamp}.jpg"
                cv2.imwrite(image_path, frame)
                
                # Send message and image to Telegram
                send_telegram_message(bot_token, chat_id, "Mao laoshi Laile!", image_path)
                warning_sent = True
        else:
            window.comm.update_status.emit("Safe")
            warning_sent = False

        window.update_frame(frame)

if __name__ == "__main__":
    mao_image_paths = [
        './mao/3.jpg',
        './mao/7.png'
        # ... add paths for all 7 Mao images
    ]
    known_faces = load_known_faces(mao_image_paths)

    pipeline = setup_camera()
    app, window = run_gui()

    # Replace with your actual bot token and chat ID
    bot_token = "7531965499:AAHD_gtwHw3AYX18GO2iroH3uIgs0FVEg6E"
    chat_id = "5500508469"

    thread = threading.Thread(target=detect_person, args=(known_faces, pipeline, window, bot_token, chat_id), daemon=True)
    thread.start()

    app.exec_()

    pipeline.stop()


import threading
import cv2
import numpy as np
import time
import os
from camera import setup_camera, get_frame
from gui import run_gui
import requests
from datetime import datetime
import face_recognition

def load_known_faces(image_paths):
    known_faces = []
    for path in image_paths:
        image = face_recognition.load_image_file(path)
        encoding = face_recognition.face_encodings(image)
        if encoding:
            known_faces.append(encoding[0])
    return known_faces

def send_telegram_message(bot_token, chat_id, message, image_path=None):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message
    }
    response = requests.post(url, data=data)
    
    if image_path:
        url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
        with open(image_path, 'rb') as photo:
            files = {'photo': photo}
            data = {'chat_id': chat_id}
            response = requests.post(url, data=data, files=files)
    
    return response.json()

def detect_person(known_faces, pipeline, window, bot_token, chat_id):
    detection_start_time = None
    warning_sent = False
    
    # Ensure debug folder exists
    os.makedirs("./debug", exist_ok=True)

    while True:
        frame = get_frame(pipeline)
        if frame is None:
            continue

        # Reduce frame size for faster processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = small_frame[:, :, ::-1]  # Convert BGR to RGB

        # Find all faces in the current frame
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        mao_detected = False
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # Compare face with known faces
            matches = face_recognition.compare_faces(known_faces, face_encoding, tolerance=0.6)
            
            if True in matches:
                mao_detected = True
                # Scale back up face locations since we detected on scaled down image
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                break

        if mao_detected:
            window.comm.update_status.emit("<font color='red' size='20'>Mao laoshi Laile</font>")
            if not warning_sent:
                # Save image with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                image_path = f"./debug/mao_detected_{timestamp}.jpg"
                cv2.imwrite(image_path, frame)
                
                # Send message and image to Telegram
                send_telegram_message(bot_token, chat_id, "Mao laoshi Laile!", image_path)
                warning_sent = True
        else:
            window.comm.update_status.emit("Safe")
            warning_sent = False

        window.update_frame(frame)

if __name__ == "__main__":
    mao_image_paths = [
        './mao/***.jpg',
        './mao/***.png'
        # ... add paths for all images
    ]
    known_faces = load_known_faces(mao_image_paths)

    pipeline = setup_camera()
    app, window = run_gui()

    # Replace with your actual bot token and chat ID
    bot_token = "YOUR_TELEGRAM_BOT_API_TOKEN"
    chat_id = "CHAT_ID"

    thread = threading.Thread(target=detect_person, args=(known_faces, pipeline, window, bot_token, chat_id), daemon=True)
    thread.start()

    app.exec_()

    pipeline.stop()

