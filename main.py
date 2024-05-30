from tkinter import Tk, Frame, Label, Button, BOTH
from capture_data import capture_data_init
from check_attendance import check_attendance_init


# Function to create the menu after running the app
def menu():
    menu_frame = Frame(parent_frame, width=1024, height=576, bg="#86c287")
    menu_frame.pack(anchor="center", expand=True, pady=10)
    menu_frame.pack_propagate(False)

    program_name = Label(menu_frame, text="Student Attendance System using Face Recognition", font=font_title,
                         bg="#86c287")
    program_name.pack(pady=100, padx=10)

    capture_button = Button(menu_frame, text="Capture Student Face", font=font_button, command=capture_face)
    capture_button.pack(pady=10, padx=10)

    attendance_button = Button(menu_frame, text="Check Student Attendance", font=font_button, command=check_attendance)
    attendance_button.pack(pady=10, padx=10)


# Function to direct app to menu page. Use in "Go Back" button
def go_to_menu():
    clear_frame(parent_frame)
    menu()


# For starting capture face feature to get face data from the user
def capture_face():
    clear_frame(parent_frame)
    capture_data_init(parent_frame, go_to_menu, camera_no)


# For starting the check attendance feature
def check_attendance():
    clear_frame(parent_frame)
    check_attendance_init(parent_frame, go_to_menu, camera_no)


# Clear the frame children in Tkinter
def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()


root = Tk()

root.geometry("1280x720")
root.title("Student Attendance System using Face Recognition")

bg_color = "#389438"
font_title = ("Georgia", 20)
font_button = ("Georgia", 14)

# Index for the camera, 0 is for default PC webcam, if you have other camera device connected to your PC,
# you can change the number index. Please make sure the resolution of your camera is 640x480
camera_no = 0

parent_frame = Frame(root, width=1280, height=720, bg=bg_color)
parent_frame.pack(fill=BOTH, expand=True)

# Call the menu function to display the menu when the program starts
menu()

root.mainloop()
