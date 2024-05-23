import cv2
import numpy as np
import os
import pickle

# Initialize video capture and face detector
video = cv2.VideoCapture(0)  # 0 for webcam
facedetect = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

face_data = []
i = 0

name = input("Enter your name: ")

while True:
    ret, frame = video.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = facedetect.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        crop_img = frame[y:y + h, x:x + w, :]
        resized_img = cv2.resize(crop_img, (100, 100))
        if len(face_data) < 70 and i % 10 == 0:
            face_data.append(resized_img)
        i += 1
        cv2.putText(frame, str(len(face_data)), (100, 100), cv2.FONT_HERSHEY_COMPLEX, 1, (100, 100, 255), 1)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (100, 100, 255), 1)

    cv2.imshow("Frame", frame)
    k = cv2.waitKey(1)
    if len(face_data) == 70:
        break

video.release()
cv2.destroyAllWindows()

# Save faces in pickle file
face_data = np.array(face_data)
face_data = face_data.reshape(70, -1)  # Reshape to (number of samples, flattened image size)

# Ensure the data directory exists
if not os.path.exists('data'):
    os.makedirs('data')

# Save the names
if 'names.pkl' not in os.listdir('data/'):
    names = [name] * 70
    with open('data/names.pkl', 'wb') as f:
        pickle.dump(names, f)
else:
    with open('data/names.pkl', 'rb') as f:
        names = pickle.load(f)
    names.extend([name] * 70)
    with open('data/names.pkl', 'wb') as f:
        pickle.dump(names, f)

# Save the face data
if 'face_data.pkl' not in os.listdir('data/'):
    with open('data/face_data.pkl', 'wb') as f:
        pickle.dump(face_data, f)
else:
    with open('data/face_data.pkl', 'rb') as f:
        faces = pickle.load(f)
    faces = np.append(faces, face_data, axis=0)
    with open('data/face_data.pkl', 'wb') as f:
        pickle.dump(faces, f)

print("Face data and labels saved successfully.")
