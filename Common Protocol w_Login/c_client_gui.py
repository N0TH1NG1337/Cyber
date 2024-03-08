"""
    Client GUI .py

    date : 06/03/2024

    TODO :

"""

#  region Libraries

from c_client_bl import *
from c_login_gui import *
from tkinter import *

from tkinter import messagebox

#  endregion


#  region Constants

DEFAULT_IP: str = "127.0.0.1"

FONT_TITLE: tuple = ("Calibri", 20)
FONT_BUTTON: tuple = ("Calibri", 14)

COLOR_BLACK: str = "#000000"
COLOR_DARK_GRAY: str = "#808080"
COLOR_LIGHT_GRAY: str = "#c0c0c0"

BUTTON_IMAGE: str = "..\\Images\\gui_button.png"
BACKGROUND_IMAGE: str = "..\\Images\\gui_bg.png"


#  endregion


#  region Client CLass


class c_client_gui:

    def __init__(self):
        self._client = None

        # Client Window obj
        self._window = None

        # Login window Obj
        self._login_obj = None

        # Images Data
        self._images = {
            "background": {"size": [0, 0]},
            "button": {"size": [0, 0]}
        }

        # Back Canvas
        # Will work as base for ui
        self._back_canvas = None

        # UI
        self._ui = {}

        self.__setup_window()

    #  region GUI

    def __setup_window(self):
        """
        Setup client window
        """

        # Create and save window root
        self._window = Tk()

        # Set window title
        self._window.title("Client GUI")

        # Disable resize to fit with the background image
        self._window.resizable(False, False)

        # Setup images
        # NOTE: we dont need to pass anything since we already
        #       save everything within the client object
        self.__setup_images()

        # After we set up images we set the window size
        # since we need to know the background image size for this
        self._window.geometry("{}x{}".format(self._images["background"]["size"][0],
                                             self._images["background"]["size"][1]))

        # Now we need to set up the background of our window with
        # our background image
        self._back_canvas = Canvas(self._window,
                                   width=self._images["background"]["size"][0],
                                   height=self._images["background"]["size"][1])

        self._back_canvas.pack(fill='both', expand=True)
        self._back_canvas.create_image(0, 0, anchor="nw", image=self._images["background"]["image"])

        # In-Application title
        self._back_canvas.create_text(20, 30, text="Client", font=FONT_TITLE, fill=COLOR_DARK_GRAY, anchor="nw")

        self.__create_elements()

    def __create_elements(self):
        """
        Create the ui elements in the window
        """

        # All our buttons X axis the same
        # therefore we don't want to calculate everytime the same thing
        buttons_x = self._images["background"]["size"][0] - self._images["button"]["size"][0] - 30

        # Connect Button
        self.__create_button(
            "Connect", "connect_button",
            buttons_x, 40,
            self.__on_event_connect)

        # Disconnect Button
        self.__create_button(
            "Disconnect", "disconnect_button",
            buttons_x, 40 + 46 + 30,
            self.__on_event_disconnect,
            "disabled")

        # Send Data Button
        self.__create_button(
            "Send Data", "send_button",
            buttons_x, 40 + (46 + 30) * 2,
            self.__on_event_send_data,
            "disabled")

        # Login Button
        self.__create_button(
            "Login/Reg", "login_button",
            buttons_x, 40 + (46 + 30) * 3,
            self.__on_event_create_login_window,
            "disabled")

        # IP Entry
        self.__create_text_input("IP:", "ip_entry", 10, 150, None, DEFAULT_IP)

        # Port Entry
        self.__create_text_input("Port:", "port_entry", 10, 190, None, str(PORT))

        # Command Entry
        self.__create_text_input("Sent:", "cmd_entry", 10, 230, None)

        # Arguments Entry
        self.__create_text_input(None, "args_entry", 10 + 150, 230, None, None, 20)

        # Receive Field
        self._back_canvas.create_text(10, 150 + 40 * 3, text="Receive:", font=FONT_BUTTON, fill=COLOR_BLACK,
                                      anchor="nw")
        self._ui["receive_field"] = Text(self._back_canvas, width=44, height=6, state="disabled")
        self._ui["receive_field"].place(x=10 + 100, y=150 + 40 * 3)

    def __create_button(self, text, index, x_axis, y_axis, event_function, default_state=None):
        self._ui[index] = Button(self._back_canvas,
                                 text=text, font=FONT_BUTTON, bd=0,
                                 borderwidth=0, compound="center", fg="#c0c0c0",
                                 image=self._images["button"]["image"],
                                 width=self._images["button"]["size"][0],
                                 height=self._images["button"]["size"][1],
                                 highlightthickness=0,
                                 command=event_function)
        self._ui[index].place(x=x_axis, y=y_axis)

        if default_state:
            self._ui[index].config(state=default_state)

    def __create_text_input(self, text, index, x_axis, y_axis, default_state=None, default_value=None, width=13):
        if text:
            self._back_canvas.create_text(x_axis, y_axis, text=text, font=FONT_BUTTON, fill=COLOR_BLACK, anchor="nw")
        self._ui[index] = Entry(self._back_canvas, font=FONT_BUTTON, width=width)
        self._ui[index].place(x=x_axis + 100, y=y_axis)

        if default_value:
            self._ui[index].insert(0, default_value)

        if default_state:
            self._ui[index].config(state=default_state)

    def __setup_images(self):
        """
        Setup client gui images and save their data
        """

        # Load images
        self._images["background"]["image"] = PhotoImage(file=BACKGROUND_IMAGE)
        self._images["button"]["image"] = PhotoImage(file=BUTTON_IMAGE)

        # Save their vectors
        self._images["background"]["size"] = [self._images["background"]["image"].width(),
                                              self._images["background"]["image"].height()]

        self._images["button"]["size"] = [self._images["button"]["image"].width(),
                                          self._images["button"]["image"].height()]

    def draw(self):
        """
        Draw the client window
        """

        self._window.mainloop()

    #  endregion

    #  region Events

    def __on_event_connect(self):
        """
        Connect client event, and initialize client socket
        """

        try:

            # Start Client Business Layer
            self._client = c_client_bl(self._ui["ip_entry"].get(),
                                       int(self._ui["port_entry"].get()))

            if not self._client.get_success():
                # Show the error code of the failure
                raise Exception(self._client.get_last_error())
            else:

                # If everything is fine
                # Add functions to event callbacks
                self._client.register_callback("disconnect",
                                               self.__on_event_disconnect,
                                               "gui_disconnect_event")

                self._client.register_callback("receive",
                                               self.__on_event_receive_data,
                                               "gui_receive_event")

                self._client.register_callback("login",
                                               self.__on_event_login,
                                               "gui_login_event")

                # Handle GUI changes
                self._ui["ip_entry"].config(state="disabled")
                self._ui["port_entry"].config(state="disabled")

                self._ui["connect_button"].config(state="disabled")
                self._ui["disconnect_button"].config(state="normal")
                self._ui["login_button"].config(state="normal")

        except Exception as e:

            # Handle failure
            write_to_log(f"  Client    · an error has occurred : {e}")
            messagebox.showerror("Error on Connect", str(e))

    def __on_event_disconnect(self):
        """
        Disconnect client event
        """

        # Start the disconnection progress
        result = self._client.disconnect()

        if result:
            # Handle UI
            self._ui["ip_entry"].config(state="normal")
            self._ui["port_entry"].config(state="normal")

            self._ui["connect_button"].config(state="normal")
            self._ui["disconnect_button"].config(state="disabled")
            self._ui["send_button"].config(state="disabled")
            self._ui["login_button"].config(state="disabled")
        else:

            # Show error
            messagebox.showerror("Error on Disconnect", self._client.get_last_error())

    def __on_event_send_data(self):
        """
        Send data from client to server event,
        and delay call to receive data event
        """

        # Get from UI
        cmd = self._ui["cmd_entry"].get()
        args = self._ui["args_entry"].get()

        # Just small tweak
        if args == "":
            args = None

        # Send
        if cmd != "":
            if not self._client.send_data(cmd, args):

                # Show error on fail
                messagebox.showerror("Error on Send Data", self._client.get_last_error())

    def __on_event_receive_data(self, message):
        """
        Update the Receive Text Field
        """

        if message:
            self._ui["receive_field"].config(state="normal")
            self._ui["receive_field"].insert("end", " · " + message + "\n")
            self._ui["receive_field"].config(state="disabled")

    def __on_event_create_login_window(self):
        """
        Login event function,
        Set up a login window on button press
        """

        # Avoid creating more than one login
        if self._login_obj is None:

            # Create login window
            self._login_obj = c_login_gui(self._window)

            # Register all the events functions
            self._login_obj.register_callback("register", self._client.register_client, "gui_register_callback")
            self._login_obj.register_callback("login", self._client.login_client, "gui_login_callback")
            self._login_obj.register_callback("unload", self.__on_event_destroy_login_window, "gui_login_callback")

            # Draw the login window
            self._login_obj.draw()

    def __on_event_destroy_login_window(self):
        """
        Unload login window callback,
        use to access login another time, without duplicating windows
        """

        self._login_obj = None

    def __on_event_login(self, message):

        if message == "user_successfully_logged_in":
            # If we are logged in

            # Handle GUI
            self._ui["send_button"].config(state="normal")
            self._ui["login_button"].config(state="disabled")

            # Show Info
            messagebox.showinfo("Logged In",
                                "You can close the Login Window and use the client")
        else:
            # If we are not logged in
            # show error
            messagebox.showerror("Error in Log In",message)

    #  endregion


#  endregion


#  region Entry Point


def main():
    c_client_gui().draw()


if __name__ == "__main__":
    main()

#   endregion
