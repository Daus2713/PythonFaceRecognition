import cv2
import numpy as np
import os
import pickle
from tkinter import Frame, Label, Button, BOTH, Entry, LEFT
from PIL import Image, ImageTk

global capture_face_frame, is_success, menu_function, camera_index


# Start capture data page
def capture_data_init(parent_frame, menu, camera_no):
    global capture_face_frame, menu_function, camera_index
    menu_function = menu
    camera_index = camera_no

    capture_face_frame = Frame(parent_frame, width=1152, height=710, bg="#86c287")
    capture_face_frame.pack(anchor="center", fill=BOTH, pady=50, padx=55)

    go_menu_button = Button(capture_face_frame, text="Go Back", bg="white", command=menu_function, font=("Georgia", 12))
    go_menu_button.pack(anchor="w", padx=5, pady=5)

    # Load the PNG image
    image_path = "capture_example.png"  # Update with the path to your PNG image
    image = Image.open(image_path)
    photo = ImageTk.PhotoImage(image)

    # Create a label to hold the image
    image_label = Label(capture_face_frame, image=photo)
    image_label.image = photo  # Keep a reference to avoid garbage collection
    image_label.pack(anchor="center", pady=10, padx=15)

    instruction_text = """
    * The red square border detects the face, and the number at the top left indicates the number of face data that have been captured.
    * The system needs to capture 50 frames of the face before adding the your face data into the system.
    * Try to adjust your face towards the camera and make sure the red rectangle appear to confirm your face
    * Press 'e' key while system capturing your face to stop and exit the process
    """

    # Create a label for the instruction text
    instruction_label = Label(capture_face_frame, text=instruction_text, justify=LEFT, font=("Georgia", 12))
    instruction_label.pack(anchor="center", pady=12, padx=20)

    form_instruction = Label(capture_face_frame, text="Please fill in name and matric no before start capturing!",
                             bg="#86c287")
    form_instruction.pack(anchor="center", pady=2)

    # Create a form for name and matric no
    form_frame = Frame(capture_face_frame, bg="#86c287")
    form_frame.pack(anchor="center", padx=40, pady=10)

    # Name entry
    name_label = Label(form_frame, text="Name:", anchor="w", bg="#86c287")
    name_label.grid(row=0, column=0, sticky="w", padx=20, pady=5)

    name_entry = Entry(form_frame, width=50)
    name_entry.grid(row=0, column=1, padx=20, pady=5)

    # Matric No entry
    matric_label = Label(form_frame, text="Matric No:", anchor="w", bg="#86c287")
    matric_label.grid(row=1, column=0, sticky="w", padx=20, pady=5)

    matric_entry = Entry(form_frame, width=50)
    matric_entry.grid(row=1, column=1, padx=20, pady=5)

    start_capture_button = Button(capture_face_frame, font=("Georgia", 12), text="Start Capture",
                                  command=lambda: check_capture(name_entry, matric_entry))
    start_capture_button.pack(anchor="center", pady=5, padx=5)


# Check name and matric no. is present before start running camera
def check_capture(name_entry, matric_entry):
    global is_success
    if not name_entry.get():
        name_entry.insert(0, "Missing required value!")
    elif not matric_entry.get():
        matric_entry.insert(0, "Missing required value!")
    else:
        is_success = True
        capture_data(name_entry.get() + "_" + matric_entry.get())


# Display response after user done capturing face
def after_capture_feedback(name_matric):
    for widget in capture_face_frame.winfo_children():
        widget.destroy()

    if is_success:
        success_text = Label(capture_face_frame, text="Face data saved successfully.", font=("Georgia", 18))
        success_text.pack(anchor="center", pady=20)

        person_info = Label(capture_face_frame, text=name_matric, font=("Georgia", 12))
        person_info.pack(anchor="center", pady=10)

    else:
        failure_text = Label(capture_face_frame, text="You pressed 'e' key. The system forced to exit",
                             font=("Georgia", 18))
        failure_text.pack(anchor="center", pady=20)

    main_menu_button = Button(capture_face_frame, text="Main menu", command=menu_function, font=("Georgia", 12))
    main_menu_button.pack(anchor="center", pady=10)


# Handle capturing face data from user and save in pickle file
def capture_data(person_info):
    # Initialize video capture and face detector
    video = cv2.VideoCapture(camera_index)
    facedetect = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

    face_data = []
    i = 0

    while True:
        global is_success
        ret, frame = video.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = facedetect.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            crop_img = frame[y:y + h, x:x + w, :]
            resized_img = cv2.resize(crop_img, (100, 100))
            if len(face_data) < 50 and i % 10 == 0:
                face_data.append(resized_img)
            i += 1
            cv2.putText(frame, str(len(face_data)), (100, 100), cv2.FONT_HERSHEY_COMPLEX, 1, (100, 100, 255), 1)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (100, 100, 255), 1)

        cv2.imshow("Capturing Face: " + person_info, frame)
        key = cv2.waitKey(1)

        # Break the loop if 'e' key is pressed
        if key == ord('e'):
            is_success = False
            break

        if len(face_data) == 50:
            break

    video.release()
    cv2.destroyAllWindows()

    if len(face_data) == 50 and is_success:
        # Save faces in pickle file
        face_data = np.array(face_data)
        face_data = face_data.reshape(50, -1)  # Reshape to (number of samples, flattened image size)

        # Ensure the data directory exists
        if not os.path.exists('data'):
            os.makedirs('data')

        # Save the student_info
        if 'student_info.pkl' not in os.listdir('data/'):
            student_info = [person_info] * 50
            with open('data/student_info.pkl', 'wb') as f:
                pickle.dump(student_info, f)
        else:
            with open('data/student_info.pkl', 'rb') as f:
                student_info = pickle.load(f)
            student_info.extend([person_info] * 50)
            with open('data/student_info.pkl', 'wb') as f:
                pickle.dump(student_info, f)

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

    after_capture_feedback(person_info)
