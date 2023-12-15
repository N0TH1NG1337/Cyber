"""
Server Presentation Layer.py

author : 
date : 14.12
"""

from Protocol import *  # Import protocol file
from tkinter import *  # Import tkinter library
from tkinter import messagebox  # Import messagebox from tkinter library
from Server_BL import *

# Constants
DEFAULT_IP: str = "0.0.0.0"
BUTTON_IMAGE: str = "..\\GUI - button.png"
BACKGROUND_IMAGE: str = "..\\GUI - BG.png"
FONT: str = "Calibri"
FONT_TITLE: tuple = (FONT, 20)
FONT_BUTTON: tuple = (FONT, 14)
COLOR_BLACK: str = "#000000"
COLOR_DARK_GRAY: str = "#808080"
COLOR_LIGHT_GRAY: str = "#c0c0c0"


class Server:
    def __init__(self, base):
        """ Init Server GUI """

        # Save the window root
        self.window = base

        # Load both images that we will use
        self.background_image = PhotoImage(file=BACKGROUND_IMAGE)
        self.button_image = PhotoImage(file=BUTTON_IMAGE)

        # Save images sizes
        background_image_size = [self.background_image.width(), self.background_image.height()]
        button_image_size = [self.button_image.width(), self.button_image.height()]

        # Set window size
        self.window.geometry("{}x{}".format(background_image_size[0], background_image_size[1]))

        # Do Background
        self.bg_canvas = Canvas(self.window, width=background_image_size[0], height=background_image_size[1])
        self.bg_canvas.pack(fill='both', expand=True)
        self.bg_canvas.create_image(0, 0, anchor="nw", image=self.background_image)

        # In-Application title
        self.bg_canvas.create_text(20, 30, text="Server", font=FONT_TITLE, fill=COLOR_DARK_GRAY, anchor="nw")

        # Text Inputs
        # Ip
        self.bg_canvas.create_text(10, 180, text="IP:", font=FONT_BUTTON, fill=COLOR_BLACK, anchor="nw")
        self.ip_entry = Entry(self.bg_canvas, font=FONT_BUTTON)
        self.ip_entry.insert(0, DEFAULT_IP)
        self.ip_entry.place(x=10 + 120, y=180)

        # Port
        self.bg_canvas.create_text(10, 180 + 40, text="Port:", font=FONT_BUTTON, fill=COLOR_BLACK, anchor="nw")
        self.port_entry = Entry(self.bg_canvas, font=FONT_BUTTON)
        self.port_entry.insert(0, str(DEFAULT_PORT))
        self.port_entry.place(x=10 + 120, y=180 + 40)

        # Receive [no need]
        # self.bg_canvas.create_text(10, 180 + 40 * 2, text="Received:", font=FONT_BUTTON, fill=COLOR_BLACK, anchor="nw")
        # self.received_entry = Entry(self.bg_canvas, font=FONT_BUTTON, state="disabled")
        # self.received_entry.place(x=10 + 120, y=180 + 40 * 2)

        # Buttons
        # start
        self.start_button = Button(self.bg_canvas,
                                   text="Start", font=FONT_BUTTON, command=self.start_event, bd=0,
                                   image=self.button_image, borderwidth=0, compound="center", fg="#c0c0c0",
                                   width=button_image_size[0], height=button_image_size[1], highlightthickness=0)
        self.start_button.place(x=background_image_size[0] - button_image_size[0] - 30, y=40)

        # Disconnect
        self.stop_button = Button(self.bg_canvas,
                                  text="Stop", font=FONT_BUTTON, command=self.stop_event, bd=0,
                                  state="disabled",
                                  image=self.button_image, borderwidth=0, compound="center", fg="#c0c0c0",
                                  width=button_image_size[0], height=button_image_size[1], highlightthickness=0)
        self.stop_button.place(x=background_image_size[0] - button_image_size[0] - 30, y=40 + 46 + 30)

        # Draw
        self.window.mainloop()

    def start_event(self):
        """ Start server event """
        self.start_button.config(state="disabled")
        self.ip_entry.config(state="disabled")
        self.port_entry.config(state="disabled")
        self.stop_button.config(state="normal")

        server_handle_thread = threading.Thread(target=start_server)
        server_handle_thread.start()

    def stop_event(self):
        """ Stop server """
        self.start_button.config(state="normal")
        self.ip_entry.config(state="normal")
        self.port_entry.config(state="normal")
        self.stop_button.config(state="disabled")

        set_server_running_flag(False)


# Main function
def main():
    # Create new window
    new_window = Tk()

    # Set title
    new_window.title("Assignment Server GUI")

    # Disable Resize
    new_window.resizable(False, False)

    # Set everything
    Server(new_window)


# Entry point
if __name__ == "__main__":
    main()
