"""
Client Presentation Layer .py

author : 
date : 14.12
"""


from Protocol import *  # Import protocol file
from tkinter import *  # Import tkinter library
from tkinter import messagebox  # Import messagebox from tkinter library
from Client_BL import connect, disconnect, send, receive

# Constants
DEFAULT_IP = "127.0.0.1"
BUTTON_IMAGE = "..\\GUI - button.png"
BACKGROUND_IMAGE = "..\\GUI - BG.png"
FONT = "Calibri"
FONT_TITLE = (FONT, 20)
FONT_BUTTON = (FONT, 14)
COLOR_BLACK = "#000000"
COLOR_DARK_GRAY = "#808080"
COLOR_LIGHT_GRAY = "#c0c0c0"

# declare a client_socket
client_socket: socket


class Client:
    def __init__(self, base):
        """ Init Client GUI """

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
        """ Connect client event, and initialize client socket """

        global client_socket
        client_socket = connect(self.ip_entry.get(), int(self.port_entry.get()))

        if client_socket:
            self.connect_button.config(state="disabled")
            self.ip_entry.config(state="disabled")
            self.port_entry.config(state="disabled")
            self.disconnect_button.config(state="normal")
            self.send_button.config(state="normal")

    def disconnect_event(self):
        """ Disconnect client event """

        global client_socket
        result = disconnect(client_socket)
        if result:
            self.connect_button.config(state="normal")
            self.ip_entry.config(state="normal")
            self.port_entry.config(state="normal")
            self.disconnect_button.config(state="disabled")
            self.send_button.config(state="disabled")

    def send_data_event(self):
        """ Send data from client to server event,
            and delay call for the receive data event """

        global client_socket
        message = self.sent_entry.get()
        if message:
            send(client_socket, message)
            self.window.after(100, self.receive_data_event)

    def receive_data_event(self):
        """ Receive data from server to the client,
            in addition update receive entry field """

        global client_socket
        message = receive(client_socket)
        self.received_entry.config(state="normal")
        self.received_entry.delete(0, END)
        self.received_entry.insert(0, message)
        self.received_entry.config(state="disabled")


# Main function
def main():
    # Create new window
    new_window = Tk()

    # Set title
    new_window.title("Assignment Client GUI")

    # Disable Resize
    new_window.resizable(False, False)

    # Set everything
    Client(new_window)


# Entry point
if __name__ == "__main__":
    main()
