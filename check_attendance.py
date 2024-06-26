import csv
import os
import pickle
import platform
import time
from datetime import datetime
from tkinter import Frame, Label, Button, BOTH, Text, LEFT, END

import cv2
from PIL import Image, ImageTk
from sklearn.neighbors import KNeighborsClassifier

# Global variables declaration
global check_attendance_frame, menu_function, lbl_video, video, knn, facedetect, attend_button, toggle_auto_button, latest_attendance, auto_mode, action_text, action_log, date, camera_index


# Function to start the check attendance interface
def check_attendance_init(parent_frame, menu, camera_no):
    global check_attendance_frame, menu_function, camera_index
    menu_function = menu
    camera_index = camera_no

    # Create a frame for check attendance interface
    check_attendance_frame = Frame(parent_frame, width=1152, height=710, bg="#86c287")
    check_attendance_frame.pack(anchor="center", fill=BOTH, pady=25, padx=55)

    # Create a button to go back to the menu
    go_menu_button = Button(check_attendance_frame, text="Go Back", bg="white", command=menu_function,
                            font=("Georgia", 12))
    go_menu_button.pack(anchor="w", padx=5, pady=5)

    # Initialize face detection
    init_face_detect()


# Function to initialize face detection
def init_face_detect():
    global lbl_video, video, knn, facedetect, attend_button, toggle_auto_button, latest_attendance, auto_mode, action_text, action_log

    # Check if necessary data files exist
    if not (os.path.exists('data/student_info.pkl') and os.path.exists('data/face_data.pkl')):
        # Display a warning message if data files are missing
        warning = """
        There is no face data captured in the system.
        Please do capture face first before check attendance    
        """
        warning_text = Label(check_attendance_frame, text=warning, font=("Georgia", 18))
        warning_text.pack(anchor="center", padx=12, pady=20)
        return

    # Load trained data for KNN classifier
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
    video = cv2.VideoCapture(camera_index)

    # Create a label to display the video feed
    lbl_video = Label(check_attendance_frame)
    lbl_video.pack()

    # Create a frame to hold the buttons
    group_button = Frame(check_attendance_frame)
    group_button.pack(anchor="center", padx=5)

    # Add a button to capture attendance manually
    attend_button = Button(group_button, text="Capture Attendance", bg="white", command=capture_attendance,
                           font=("Georgia", 12))
    attend_button.pack(side=LEFT, padx=2, pady=10)

    # Add a button to toggle auto mode for attendance capture
    auto_mode = False  # Initialize auto mode as off
    toggle_auto_button = Button(group_button, text="Enable Auto Mode", bg="white", command=toggle_auto_mode,
                                font=("Georgia", 12))
    toggle_auto_button.pack(side=LEFT, padx=2, pady=10)

    # Add a button to show the attendance list
    show_csv = Button(group_button, text="Attendance List", bg="white", font=("Georgia", 12),
                      command=lambda: open_csv_file(r"Attendance\Attendance_" + date + ".csv"))
    show_csv.pack(side=LEFT, padx=2, pady=1)

    # Initial instructions for actions
    initial_action_text = """
    Capture Attendance - capture face and check the attendance
    Auto mode - Auto check attendance for the face detected by the system
    Attendance List - Open CSV file of student attendance. Generated CSV file located in Attendance folder
    """

    # Add a text box to display the latest actions
    action_text = Text(check_attendance_frame, width=100, height=4, bg="white", font=("Georgia", 9))
    action_text.pack(anchor="center", padx=4, pady=12)

    # List to store the latest actions
    action_log = []

    # Insert initial action text into the text box
    action_text.config(state="normal")
    action_text.insert(END, initial_action_text)
    action_text.config(state="disabled")

    # Initialize latest attendance as None
    latest_attendance = None

    # Start updating the video frame
    update_frame()


# Function to toggle auto detect and record attendance mode
def toggle_auto_mode():
    global auto_mode, toggle_auto_button
    auto_mode = not auto_mode
    if auto_mode:
        toggle_auto_button.config(text="Disable Auto Mode")
    else:
        toggle_auto_button.config(text="Enable Auto Mode")


# Function to handle recording the recognized face into a CSV file
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
            # Check if the person already exists in the CSV file
            with open(f"Attendance/Attendance_{date}.csv", "r") as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if row and row[0] == str(output[0]) and row[1] == str(output[1]):
                        print(f"Attendance for {output[0]} {output[1]} already captured for {date}")
                        already_captured = True
                        break

        if already_captured:
            latest_action = f"Attendance for {output[0]} {output[1]} already captured for {date}"
        else:
            latest_action = f"{output[0]} {output[1]} - {timestamp}"
            # Write attendance data into the CSV file
            if exist:
                with open(f"Attendance/Attendance_{date}.csv", "a", newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(attendance)
            else:
                with open(f"Attendance/Attendance_{date}.csv", "a", newline='') as csvfile:
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
        print("No face detected to capture attendance or camera not working")


# Function to open CSV file using the default application of the device
def open_csv_file(file_path):
    if os.path.isfile(file_path):
        if platform.system() == 'Windows':
            os.startfile(file_path)
        else:
            print("Only windows supported for this application")
    else:
        print(f"File {file_path} does not exist")


# Function to update the video frame and perform face detection
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
    lbl_video.after(10, update_frame)  # Call update_frame again after 10 milliseconds to create a loop
