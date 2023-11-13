import socket  # Import socket library
from tkinter import *  # Import tkinter library
from tkinter import messagebox  # Import messagebox from tkinter library

# Default IP and port numbers
DEFAULT_IP = "127.0.0.1"
DEFAULT_PORT = 8822

# Images paths
BUTTON_IMAGE = "C:\\Users\\mishs\\PycharmProjects\\Cyber\\HomeWork_29_10\\Fixed Applications\\GUI - button.png"
BACKGROUND_IMAGE = "C:\\Users\\mishs\\PycharmProjects\\Cyber\\HomeWork_29_10\\Fixed Applications\\GUI - BG.png"

# Font and text colors
FONT = "Calibri"
FONT_TITLE = (FONT, 20)
FONT_BUTTON = (FONT, 14)
COLOR_BLACK = "#000000"
COLOR_DARK_GRAY = "#808080"
COLOR_LIGHT_GRAY = "#c0c0c0"


class Client:
    def __init__(self, base):
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
        self.bg_canvas.create_text(20, 30, text="Client", font=FONT_TITLE, fill=COLOR_DARK_GRAY, anchor="nw")

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

        # Send
        self.bg_canvas.create_text(10, 180 + 40 * 2, text="Sent:", font=FONT_BUTTON, fill=COLOR_BLACK, anchor="nw")
        self.sent_entry = Entry(self.bg_canvas, font=FONT_BUTTON)
        self.sent_entry.place(x=10 + 120, y=180 + 40 * 2)

        # Receive
        self.bg_canvas.create_text(10, 180 + 40 * 3, text="Received:", font=FONT_BUTTON, fill=COLOR_BLACK, anchor="nw")
        self.received_entry = Entry(self.bg_canvas, font=FONT_BUTTON, state="disabled")
        self.received_entry.place(x=10 + 120, y=180 + 40 * 3)

        # Buttons
        # Connect
        self.connect_button = Button(self.bg_canvas,
                                     text="Connect", font=FONT_BUTTON, command=self.connect_event, bd=0,
                                     image=self.button_image, borderwidth=0, compound="center", fg="#c0c0c0",
                                     width=button_image_size[0], height=button_image_size[1], highlightthickness=0)
        self.connect_button.place(x=background_image_size[0] - button_image_size[0] - 30, y=40)

        # Disconnect
        self.disconnect_button = Button(self.bg_canvas,
                                        text="Disconnect", font=FONT_BUTTON, command=self.disconnect_event, bd=0,
                                        state="disabled",
                                        image=self.button_image, borderwidth=0, compound="center", fg="#c0c0c0",
                                        width=button_image_size[0], height=button_image_size[1], highlightthickness=0)
        self.disconnect_button.place(x=background_image_size[0] - button_image_size[0] - 30, y=40 + 46 + 30)

        # Send
        self.send_button = Button(self.bg_canvas,
                                  text="Send Data", font=FONT_BUTTON, command=self.send_data_event, bd=0,
                                  state="disabled",
                                  image=self.button_image, borderwidth=0, compound="center", fg="#c0c0c0",
                                  width=button_image_size[0], height=button_image_size[1], highlightthickness=0)
        self.send_button.place(x=background_image_size[0] - button_image_size[0] - 30, y=40 + 46 * 2 + 30 * 2)

        # Draw
        self.window.mainloop()

    def connect_event(self):
        self.connect_button.config(state="disabled")
        self.ip_entry.config(state="disabled")
        self.port_entry.config(state="disabled")
        self.disconnect_button.config(state="normal")
        self.send_button.config(state="normal")

    def disconnect_event(self):
        self.connect_button.config(state="normal")
        self.ip_entry.config(state="normal")
        self.port_entry.config(state="normal")
        self.disconnect_button.config(state="disabled")
        self.send_button.config(state="disabled")

    def send_data_event(self):
        pass


# Main function
def main():
    # Create new window
    new_window = Tk()

    # Set title
    new_window.title("Assignment Client GUI - Michael Sokolov")

    # Disable Resize
    new_window.resizable(False, False)

    # Set everything else
    Client(new_window)


# Entry Point
if __name__ == "__main__":
    main()
