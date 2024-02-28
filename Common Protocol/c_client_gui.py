"""

Client GUI       .py

last update:    28/02/2024

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

BUTTON_IMAGE: str = "Images\\gui_button.png"
BACKGROUND_IMAGE: str = "Images\\gui_bg.png"

#  endregion


#  region Client GUI Class
class c_client_gui:

    def __init__(self):
        self._client = None

        self._window = None
        self._login_obj = None

        self._back_img = None
        self._btn_img = None

        self._back_img_size = [0, 0]
        self._btn_img_size = [0, 0]

        self._back_canvas = None

        # UI
        self._connect_button = None
        self._disconnect_button = None
        self._send_button = None
        self._login_button = None

        self._ip_entry = None
        self._port_entry = None
        self._cmd_entry = None
        self._args_entry = None

        self._receive_field = None

        self.__setup_window()

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
        self._window.geometry("{}x{}".format(self._back_img_size[0], self._back_img_size[1]))

        # Now we need to set up the background of our window with
        # our background image
        self._back_canvas = Canvas(self._window, width=self._back_img_size[0], height=self._back_img_size[1])
        self._back_canvas.pack(fill='both', expand=True)
        self._back_canvas.create_image(0, 0, anchor="nw", image=self._back_img)

        # In-Application title
        self._back_canvas.create_text(20, 30, text="Client", font=FONT_TITLE, fill=COLOR_DARK_GRAY, anchor="nw")

        # Create the ui elements
        self.__create_elements()

    def __create_elements(self):
        """
        Create the ui elements in the window
        """

        # Buttons

        # Connect
        self._connect_button = Button(self._back_canvas,
                                      text="Connect", font=FONT_BUTTON, command=self.__connect_event, bd=0,
                                      image=self._btn_img, borderwidth=0, compound="center", fg="#c0c0c0",
                                      width=self._btn_img_size[0], height=self._btn_img_size[1],
                                      highlightthickness=0)
        self._connect_button.place(x=self._back_img_size[0] - self._btn_img_size[0] - 30, y=40)

        # Disconnect
        self._disconnect_button = Button(self._back_canvas,
                                         text="Disconnect", font=FONT_BUTTON, command=self.__disconnect_event, bd=0,
                                         state="disabled",
                                         image=self._btn_img, borderwidth=0, compound="center", fg="#c0c0c0",
                                         width=self._btn_img_size[0], height=self._btn_img_size[1],
                                         highlightthickness=0)
        self._disconnect_button.place(x=self._back_img_size[0] - self._btn_img_size[0] - 30, y=40 + 46 + 30)

        # Send data
        self._send_button = Button(self._back_canvas,
                                   text="Send Data", font=FONT_BUTTON, command=self.__send_data_event, bd=0,
                                   state="disabled",
                                   image=self._btn_img, borderwidth=0, compound="center", fg="#c0c0c0",
                                   width=self._btn_img_size[0], height=self._btn_img_size[1],
                                   highlightthickness=0)
        self._send_button.place(x=self._back_img_size[0] - self._btn_img_size[0] - 30, y=40 + (46 + 30) * 2)

        self._login_button = Button(self._back_canvas,
                                    text="Login/Reg", font=FONT_BUTTON, command=self.__login_event, bd=0,
                                    image=self._btn_img, borderwidth=0, compound="center", fg="#c0c0c0",
                                    width=self._btn_img_size[0], height=self._btn_img_size[1],
                                    highlightthickness=0)
        self._login_button.place(x=self._back_img_size[0] - self._btn_img_size[0] - 30, y=40 + (46 + 30) * 3)

        # Text Inputs

        # IP
        self._back_canvas.create_text(10, 150, text="IP:", font=FONT_BUTTON, fill=COLOR_BLACK, anchor="nw")
        self._ip_entry = Entry(self._back_canvas, font=FONT_BUTTON, width=13)
        self._ip_entry.insert(0, DEFAULT_IP)
        self._ip_entry.place(x=10 + 100, y=150)

        # Port
        self._back_canvas.create_text(10, 150 + 40, text="Port:", font=FONT_BUTTON, fill=COLOR_BLACK, anchor="nw")
        self._port_entry = Entry(self._back_canvas, font=FONT_BUTTON, width=13)
        self._port_entry.insert(0, str(PORT))
        self._port_entry.place(x=10 + 100, y=150 + 40)

        # Send
        self._back_canvas.create_text(10, 150 + 40 * 2, text="Sent:", font=FONT_BUTTON, fill=COLOR_BLACK, anchor="nw")
        self._cmd_entry = Entry(self._back_canvas, font=FONT_BUTTON, width=13)
        self._args_entry = Entry(self._back_canvas, font=FONT_BUTTON)

        self._cmd_entry.place(x=10 + 100, y=150 + 40 * 2)
        self._args_entry.place(x=10 + 252, y=150 + 40 * 2)

        # Little magic
        self.__event_args_focus_out(None)
        self._args_entry.bind('<FocusIn>', self.__event_args_focus_in)
        self._args_entry.bind('<FocusOut>', self.__event_args_focus_out)

        # Receive
        self._back_canvas.create_text(10, 150 + 40 * 3, text="Receive:", font=FONT_BUTTON, fill=COLOR_BLACK, anchor="nw")
        self._receive_field = Text(self._back_canvas, width=44, height=6, state="disabled")
        self._receive_field.place(x=10 + 100, y=150 + 40 * 3)

    def __setup_images(self):
        """
        Setup client gui images and save their data
        """
        # Load images
        self._back_img = PhotoImage(file=BACKGROUND_IMAGE)
        self._btn_img = PhotoImage(file=BUTTON_IMAGE)

        # Save their vectors
        self._back_img_size = [self._back_img.width(), self._back_img.height()]
        self._btn_img_size = [self._btn_img.width(), self._btn_img.height()]

    def __event_args_focus_in(self, event):
        if self._args_entry.get() == "separate with ','":
            self._args_entry.delete(0, 'end')

    def __event_args_focus_out(self, event):
        if self._args_entry.get() == "":
            self._args_entry.insert(0, "separate with ','")

    def __connect_event(self):
        """
        Connect client event, and initialize client socket

        TODO : show error in gui
        """

        try:
            # Handle failure on casting from string to int

            self._client = c_client_bl(self._ip_entry.get(),
                                       int(self._port_entry.get()),
                                       self.__receive_data_event,
                                       self.__disconnect_event)

            # check if we successfully created socket
            # and ready to go
            if not self._client.get_success():
                raise Exception("failed to create and setup client bl")
            else:

                # Handle gui elements
                self._ip_entry.config(state="disabled")
                self._port_entry.config(state="disabled")

                self._connect_button.config(state="disabled")
                self._disconnect_button.config(state="normal")
                self._send_button.config(state="normal")

        except Exception as e:
            # Must have since we can also get an error
            # for incorrect casting from string to int

            # If our problem occurred before the client
            # mean that our client will be None
            error = self._client and self._client.get_last_error() or e

            write_to_log(f"  Client    · an error has occurred : {error}")
            messagebox.showerror("Error on Connect", error)

    def __disconnect_event(self):
        """
        Disconnect client event
        """

        result = self._client.disconnect()

        if result:
            # Handle gui elements
            self._ip_entry.config(state="normal")
            self._port_entry.config(state="normal")

            self._connect_button.config(state="normal")
            self._disconnect_button.config(state="disabled")
            self._send_button.config(state="disabled")

            self._client = None
        else:
            messagebox.showerror("Error on Disconnect", self._client.get_last_error())

    def __send_data_event(self):
        """
        Send data from client to server event,
        and delay call to receive data event
        """

        cmd = self._cmd_entry.get()
        args = self._args_entry.get()

        if cmd != "":
            # self._window.after(100, self.__receive_data_event)
            self._client.send_data(cmd, args)

    def __receive_data_event(self, message):
        # message = self._client.receive_data()

        if message:
            self._receive_field.config(state="normal")
            self._receive_field.insert("end", " · " + message + "\n")
            self._receive_field.config(state="disabled")

    def __login_event(self):
        """
        Login event function,
        Set up a login window on button press
        """

        # Avoid creating more than one login
        if self._login_obj is None:
            def callback_login(data):
                print(f"  Client GUI    · login data from Login Window : {data}")

            def callback_register(data):
                print(f"  Client GUI    · register data from Login Window : {data}")

            # Create login window
            self._login_obj = c_login_gui(self._window,
                                          callback_register,
                                          callback_login,
                                          self.__destroy_login_event)

            # Draw the login window
            self._login_obj.draw()

    def __destroy_login_event(self, event_place_holder):
        """
        Unload login window callback,
        use to access login another time, without duplicating windows
        """

        self._login_obj = None

    def draw(self):
        """
        Draw the client window
        """

        self._window.mainloop()


#  endregion


#  region main program and entry point

# Main function
def main():
    client = c_client_gui()
    client.draw()


# Entry Point
if __name__ == "__main__":
    main()

#  endregion
