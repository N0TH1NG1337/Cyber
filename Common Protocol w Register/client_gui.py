"""
    c_client_gui.py - Client Application Layer File

    last update : 15/05/2024
"""

#  region @ Libraries

from client_bl import *
from login_gui import *
from tkinter import *

from tkinter import messagebox

#  endregion


#  region @ Constants

DEFAULT_IP: str = "127.0.0.1"

FONT_TITLE: tuple = ("Calibri", 20)
FONT_BUTTON: tuple = ("Calibri", 14)

COLOR_BLACK: str = "#000000"
COLOR_DARK_GRAY: str = "#808080"
COLOR_LIGHT_GRAY: str = "#c0c0c0"

BUTTON_IMAGE: str = "...\\Images\\gui_button.png"
BACKGROUND_IMAGE: str = "...\\Images\\gui_bg.png"

#  endregion


#  region @ GUI Utils

class c_image:
    # I just hate to use .width/height() when i can do .x/y to access size

    def __init__(self):
        self.x = 0
        self.y = 0

        self._object = None

    def load(self, file_path):
        self._object = PhotoImage(file=file_path)

        self.x = self._object.width()
        self.y = self._object.height()

    def __call__(self):
        return self._object

#  endregion


#  region @ Client GUI Class

class c_client_gui:

    def __init__(self):

        # Client BL object
        self._client = None

        # Client window obj
        self._window = None

        # Login window Obj
        self._login_obj = None

        # Images data
        self._button_img = c_image()
        self._background_img = c_image()

        # Back canvas
        self._back_canvas = None

        # UI Elements handler
        self._ui = {}

        self.__setup_window()

    # region GUI Setup

    def __setup_window(self):
        """
            Setup window
        """

        # Create and save window root
        self._window = Tk()

        # Set window title
        self._window.title("Client GUI")

        # Disable resize to fit with the background image
        self._window.resizable(False, False)

        # Setup images
        self.__setup_images()

        # Set window Size
        self._window.geometry(f"{self._background_img.x}x{self._background_img.y}")

        # Setup background
        self._back_canvas = Canvas(self._window, width=self._background_img.x, height=self._background_img.y)
        self._back_canvas.pack(fill='both', expand=True)
        self._back_canvas.create_image(0, 0, anchor="nw", image=self._background_img())

        # In-Application title
        self._back_canvas.create_text(20, 30, text="Client", font=FONT_TITLE, fill=COLOR_DARK_GRAY, anchor="nw")

        # Create the elements
        self.__create_elements()

    def __create_elements(self):
        """
            Create interface elements
        """

        button_x_axis = self._background_img.x - self._button_img.x - 30

        # Connect Button
        self.create_button("Connect", "connect_button",
                           button_x_axis, 40,
                           self.__on_event_connect)

        # Disconnect Button
        self.create_button("Disconnect", "disconnect_button",
                           button_x_axis, 40 + 46 + 30,
                           self.__on_event_disconnect,
                           "disabled")

        # Send Message Button
        self.create_button("Send", "send_button",
                           button_x_axis, 40 + (46 + 30) * 2,
                           self.__on_event_send_message,
                           "disabled")

        # Login Button
        self.create_button("Login", "login_button",
                           button_x_axis, 40 + (46 + 30) * 3,
                           None,
                           "disabled")

        # Ip Entry
        self.create_text_input("IP:", "ip_entry", 10, 150, None, DEFAULT_IP)

        # Port Entry
        self.create_text_input("Port:", "port_entry", 10, 190, None, str(DEFAULT_PORT))

        # Command Entry
        self.create_text_input("Sent:", "cmd_entry", 10, 230)

        # Arguments Entry
        self.create_text_input(None, "args_entry", 10 + 150, 230, None, None, 21)

        # Receive Field
        self.create_big_text_input("Receive:", "receive_field", 10, 150 + 40 * 3, "disabled", 45)

    def __setup_images(self):
        """
            Load images data
        """

        self._button_img.load(BUTTON_IMAGE)
        self._background_img.load(BACKGROUND_IMAGE)

    #  endregion

    #  region GUI Utils

    def create_button(self, text, index, x_axis, y_axis, event_function, default_state=None):
        """
            Create a new button in the menu
        """

        self._ui[index] = Button(self._back_canvas,
                                 text=text, font=FONT_BUTTON,
                                 bd=0, borderwidth=0,
                                 compound="center", fg=COLOR_LIGHT_GRAY,
                                 image=self._button_img(),
                                 width=self._button_img.x,
                                 height=self._button_img.y,
                                 highlightthickness=0,
                                 command=event_function)

        self._ui[index].place(x=x_axis, y=y_axis)

        if default_state:
            self._ui[index].config(state=default_state)

    def create_text_input(self, text, index, x_axis, y_axis, default_state=None, default_value=None, width=13):
        """
            Create a new single line Text input in the menu
        """

        if text:
            self._back_canvas.create_text(x_axis, y_axis, text=text, font=FONT_BUTTON, fill=COLOR_BLACK, anchor="nw")

        self._ui[index] = Entry(self._back_canvas, font=FONT_BUTTON, width=width)
        self._ui[index].place(x=x_axis + 100, y=y_axis)

        if default_value:
            self._ui[index].insert(0, default_value)

        if default_state:
            self._ui[index].config(state=default_state)

    def create_big_text_input(self, text, index, x_axis, y_axis, default_state=None, width=44, height=6):
        """
            Create a new multi line text input in the menu
        """

        if text:
            self._back_canvas.create_text(x_axis, y_axis, text=text, font=FONT_BUTTON, fill=COLOR_BLACK, anchor="nw")

        self._ui[index] = Text(self._back_canvas, width=width, height=height)
        self._ui[index].place(x=x_axis + 100, y=y_axis)

        if default_state:
            self._ui[index].config(state=default_state)

    def update_state(self, index, state):
        """
            Update any element config state
        """

        if index not in self._ui:
            raise Exception("Invalid UI Index")

        self._ui[index].config(state=state)

    def get(self, index, return_type=None) -> any:
        """
            Receive the specific item Value.

            Can cast if needed (Doesn't check for errors)
        """

        if index not in self._ui:
            return None

        value = self._ui[index].get()

        if return_type is not None:
            return return_type(value)

        return value

    def set(self, index, place, value):
        """
            Set to specific item a new value
        """

        if index not in self._ui:
            raise Exception("Invalid UI Index")

        self._ui[index].insert(place, value)

    #  endregion

    #  region GUI Events

    @utils.safe_call(True, write_to_log)
    def __on_event_connect(self):
        """
            Client connects to server event
        """

        # Init Client BL
        self._client = c_client_bl(self.get("ip_entry"), self.get("port_entry", int))

        # Check for any error
        if not self._client("success"):
            raise Exception(self._client("last_error"))

        # Register callbacks
        self._client("disconnect") + (self.__on_event_disconnect, "gui_disconnect", False)
        self._client("receive") + (self.__on_event_receive_message, "gui_receive_message", True)
        self._client("login") + (self.__on_event_login, "gui_login_event", True)

        # Handle GUI
        self.update_state("ip_entry", "disabled")
        self.update_state("port_entry", "disabled")

        self.update_state("connect_button", "disabled")
        self.update_state("disconnect_button", "normal")
        self.update_state("login_button", "normal")

        # Create login window
        self.__on_event_create_login_window()

    @utils.safe_call(True, write_to_log)
    def __on_event_disconnect(self):
        """
            Client disconnect from the server event
        """

        # Call to stop the connection
        if not self._client.stop_connection():
            raise Exception(self._client("last_error"))

        # Handle GUI
        self.update_state("ip_entry", "normal")
        self.update_state("port_entry", "normal")

        self.update_state("connect_button", "normal")
        self.update_state("disconnect_button", "disabled")
        self.update_state("send_button", "disabled")
        self.update_state("login_button", "disabled")

    @utils.safe_call(True, write_to_log)
    def __on_event_send_message(self):
        """
            Client send message to the server event
        """

        # Get command and arguments string values
        command = self.get("cmd_entry")
        arguments = self.get("args_entry")

        # Just small change
        if arguments == "":
            arguments = None

        # Need valid Command
        if command == "":
            raise Exception("Invalid Command")

        # Check if sending the message was successful.
        if not self._client.send_message(command, arguments):
            raise Exception(self._client("last_error"))

    @utils.safe_call(True, write_to_log)
    def __on_event_receive_message(self, event):
        """
            Client received message from the server event
        """

        # Get message value
        message = event("message")

        # Check if not None
        if message:

            # Update the receive field
            self.update_state("receive_field", "normal")
            self.set("receive_field", "end", " · " + message + "\n")
            self.update_state("receive_field", "disabled")

    @utils.safe_call(True, write_to_log)
    def __on_event_login(self, event):
        """
            Client maybe logged on the server event
        """

        # Get status
        status = event("success")

        # Check if we successfully logged in
        if status != SUCCESS_CMD:
            raise Exception(status)

        # Handle GUI
        self.update_state("send_button", "normal")
        self.update_state("login_button", "disabled")

        # Get username and key for the event
        username, key = event("username"), event("key")

        self._login_obj.close()  # Close login window

        # Inform the user
        messagebox.showinfo(f"Welcome back {username}",
                            "You can use now the client")

        # We don't want to save anything on login
        if event("type") == "LOGIN":
            return

        user_data = { "key": key }  # Add another thing ?

        # Update the client file
        self._client.change_user_field(username, user_data)

    @utils.safe_call(True, write_to_log)
    def __on_event_request_login(self, event):
        """
            Client wants to request login from the server event
        """

        # Get information
        username = event("username")
        password = event("password")

        # Try to get the key
        key = utils.find_key(self._client.access_user_field(username))

        if key is None:
            return

        # Create encryption object
        cipher = c_encryption(key)

        # Prepare message
        contact_information = f"{username},{cipher.encrypt(password).decode()}"

        # Send message
        self._client.send_message("LOGIN", contact_information)

    @utils.safe_call(True, write_to_log)
    def __on_event_request_register(self, event):
        """
            Client wants to request register from the server event
        """

        # Get information
        username = event("username")
        password = event("password")

        # Prepare and send message
        contact_information = f"{username},{password}"
        self._client.send_message("REGISTER", contact_information)

    @utils.safe_call(True, write_to_log)
    def __on_event_create_login_window(self):
        """
            User opens a login window event
        """

        # Avoid duplicating windows
        if self._login_obj is not None:
            return

        # Create window
        self._login_obj = c_login_gui()

        # Setup it
        self._login_obj.setup_window(self._window)

        # Register callbacks
        self._login_obj("register") + (self.__on_event_request_register, "client_gui_register", True)
        self._login_obj("login") + (self.__on_event_request_login, "client_gui_login", True)
        self._login_obj("unload") + (self.__on_event_destroy_login_window, "client_gui_unload", False)

        # Draw it
        self._login_obj.draw()

    def __on_event_destroy_login_window(self):
        """
            login window was closed event
        """

        self._login_obj = None

    #  endregion

    def run(self):
        """
            Draw the menu
        """

        self._window.mainloop()

#  endregion


# Entry Point

def main():
    c_client_gui().run()


if __name__ == "__main__":
    main()
