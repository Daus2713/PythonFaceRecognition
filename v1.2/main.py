from tkinter import *
from capture_data import capture_data_init
from check_attendance import check_attendance_init
# Function to create the menu
def menu():
    menu_frame = Frame(parent_frame, width=1024, height=576, bg=bg_color)
    menu_frame.pack(anchor="center", expand=True, pady=10)

    program_name = Label(menu_frame, text="Student Attendance System using Face Recognition", font=font_title, bg=bg_color)
    program_name.pack(pady=20, padx=10)

    capture_button = Button(menu_frame, text="Capture Student Face", font=font_button, command=capture_face)
    capture_button.pack(pady=10, padx=10)

    attendance_button = Button(menu_frame, text="Check Student Attendance", font=font_button, command=check_attendance)
    attendance_button.pack(pady=10, padx=10)


def go_to_menu():
    clear_frame(parent_frame)
    menu()

# Function to capture face
def capture_face():
    clear_frame(parent_frame)
    capture_data_init(parent_frame, go_to_menu)

def check_attendance():
    clear_frame(parent_frame)
    check_attendance_init(parent_frame, go_to_menu)

def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()

root = Tk()

root.geometry("1280x720")
root.title("Student Attendance System using Face Recognition")

bg_color = "#389438"
font_title = ("Georgia", 20)
font_button = ("Georgia", 14)

parent_frame = Frame(root, width=1280, height=720, bg=bg_color)
parent_frame.pack(fill=BOTH, expand=True)

# Call the menu function to display the menu when the program starts
menu()

root.mainloop()
