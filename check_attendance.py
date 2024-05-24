from tkinter import *
from PIL import Image, ImageTk
from sklearn.neighbors import KNeighborsClassifier
import cv2
import subprocess
import platform
import os
import csv
import time
import pickle
from datetime import datetime

# Global variables
global check_attendance_frame, menu_function, lbl_video, video, knn, facedetect, attend_button, toggle_auto_button, latest_attendance, auto_mode, action_text,action_log, date

def check_attendance_init(parent_frame, menu):
    global check_attendance_frame, menu_function
    menu_function = menu

    check_attendance_frame = Frame(parent_frame, width=1152, height=710, bg="#86c287")
    check_attendance_frame.pack(anchor="center", fill=BOTH, pady=25, padx=55)

    go_menu_button = Button(check_attendance_frame, text="Go Back", bg="white", command=menu_function, font=("Georgia", 12))
    go_menu_button.pack(anchor="w", padx=5, pady=5)

    # Initialize face detection
    init_face_detect()

def init_face_detect():
    global lbl_video, video, knn, facedetect, attend_button, toggle_auto_button, latest_attendance, auto_mode, action_text, action_log

    # Check if necessary data files exist
    if not (os.path.exists('data/student_info.pkl') and os.path.exists('data/face_data.pkl')):
        # Display message indicating missing data files
        warning = """
        There is no face data captured in the system.
        Please do capture face first before check attendance    
        """
        warning_text = Label(check_attendance_frame, text=warning,font=("Georgia", 18) )
        warning_text.pack(anchor="center", padx=12, pady=20)
        return

    # Load trained data
    with open('data/student_info.pkl', 'rb') as w:
        LABELS = pickle.load(w)

    with open('data/face_data.pkl', 'rb') as f:
        FACES = pickle.load(f)

    # Initialize KNN classifier
    knn = KNeighborsClassifier(n_neighbors=5)
    knn.fit(FACES, LABELS)

    # Load face detection model
    facedetect = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    # Initialize video capture
    video = cv2.VideoCapture(0)

    lbl_video = Label(check_attendance_frame)
    lbl_video.pack()

    group_button = Frame(check_attendance_frame)
    group_button.pack(anchor="center", padx=5)

    # Add a button below the video frame
    attend_button = Button(group_button, text="Capture Attendance", bg="white", command=capture_attendance, font=("Georgia", 12))
    attend_button.pack(side=LEFT, padx=2, pady=10)

    # Add a toggle button for auto mode
    auto_mode = False  # Initialize auto mode as off
    toggle_auto_button = Button(group_button, text="Enable Auto Mode", bg="white", command=toggle_auto_mode, font=("Georgia", 12))
    toggle_auto_button.pack(side=LEFT, padx=2, pady=10)

    show_csv = Button(group_button, text="Attendance List", bg="white", font=("Georgia", 12), command=lambda: open_csv_file(r"Attendance\Attendance_"+date+".csv"))
    show_csv.pack(side=LEFT, padx=2, pady=1)

    initial_action_text = """
    Capture Attendance - capture face and check the attendance
    Auto mode - Auto check attendance for the face detected by the system
    Attendance List - Open CSV file of student attendance
    """

    # Add a text box to display latest actions
    action_text = Text(check_attendance_frame, width=100, height=4, bg="white", font=("Georgia", 9))
    action_text.pack(anchor="center", padx=4, pady=12)

    action_log = []  # List to store the latest actions

    # Insert initial action text
    action_text.config(state="normal")
    action_text.insert(END, initial_action_text)
    action_text.config(state="disabled")

    latest_attendance = None  # Initialize latest attendance as None

    update_frame()



def toggle_auto_mode():
    global auto_mode, toggle_auto_button
    auto_mode = not auto_mode
    if auto_mode:
        toggle_auto_button.config(text="Disable Auto Mode")
    else:
        toggle_auto_button.config(text="Enable Auto Mode")

def stop_face_detect():
    global video
    video.release()
    cv2.destroyAllWindows()

def capture_attendance():
    global latest_attendance, action_text, action_log, date
    already_captured = False

    if latest_attendance is not None:
        date, timestamp, person_info = latest_attendance
        output = person_info.split('_', 1)
        COL_NAMES = ['Name', 'Matric NO', 'Time']
        exist = os.path.isfile(f"Attendance/Attendance_{date}.csv")

        attendance = [str(output[0]), str(output[1]), str(timestamp)]

        if exist:
            with open(f"Attendance/Attendance_{date}.csv", "r") as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if row and row[0] == str(output[0]) and row[1] == str(output[1]):  # Check if person already exists
                        print(f"Attendance for {output[0]} {output[1]} already captured for {date}")
                        already_captured = True
                        break

        if already_captured:
            latest_action = f"Attendance for {output[0]} {output[1]} already captured for {date}"
        else:
            latest_action = f"{output[0]} {output[1]} - {timestamp}"
            if exist:
                with open(f"Attendance/Attendance_{date}.csv", "a") as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(attendance)
            else:
                with open(f"Attendance/Attendance_{date}.csv", "a") as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(COL_NAMES)
                    writer.writerow(attendance)
            print("Attendance captured:", attendance)

        # Update the action log
        action_log.append(latest_action)
        if len(action_log) > 4:
            action_log.pop(0)

        # Update the action text box
        action_text.config(state="normal")
        action_text.delete(1.0, END)
        for action in action_log:
            action_text.insert(END, f"{action}\n")
        action_text.config(state="disabled")
    else:
        print("No face detected to capture attendance.")



def open_csv_file(file_path):
    if os.path.isfile(file_path):
        if platform.system() == 'Windows':
            os.startfile(file_path)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.call(('open', file_path))
        else:  # Linux
            subprocess.call(('xdg-open', file_path))
    else:
        print(f"File {file_path} does not exist")



def update_frame():
    global lbl_video, video, knn, facedetect, latest_attendance, auto_mode, date

    ret, frame = video.read()
    if not ret:
        return

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = facedetect.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        crop_img = frame[y:y + h, x:x + w, :]
        resized_img = cv2.resize(crop_img, (100, 100)).flatten().reshape(1, -1)
        output = knn.predict(resized_img)[0]
        ts = time.time()
        date = datetime.fromtimestamp(ts).strftime("%d-%m-%Y")
        timestamp = datetime.fromtimestamp(ts).strftime("%H:%M:%S")

        latest_attendance = (date, timestamp, output)  # Store the latest attendance data

        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 1)
        cv2.rectangle(frame, (x, y - 40), (x + w, y), (100, 100, 255), -1)
        cv2.putText(frame, str(output), (x, y - 15), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)

        if auto_mode:
            capture_attendance()  # Automatically capture attendance if auto mode is enabled

    # Convert frame to image for tkinter
    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    imgtk = ImageTk.PhotoImage(image=img)
    lbl_video.imgtk = imgtk
    lbl_video.configure(image=imgtk)
    lbl_video.after(10, update_frame)
