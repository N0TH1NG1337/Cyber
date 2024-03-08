"""
    Login GUI   .py

    date :      06/03/2024

    TODO :

"""

#  region Libraries

from c_protocol import *
from tkinter import *  # Import tkinter library

#  endregion


#  region Constants

FONT_TITLE: tuple = ("Calibri", 20)
FONT_BUTTON: tuple = (" Calibri", 14)

COLOR_BLACK: str = "#000000"
COLOR_DARK_GRAY: str = "#808080"
COLOR_LIGHT_GRAY: str = "#c0c0c0"

BUTTON_IMAGE: str = "..\\Images\\gui_button.png"
BACKGROUND_IMAGE: str = "..\\Images\\gui_bg.png"

#  endregion


#  region Login GUI Class


class c_login_gui:

    def __init__(self, parent_wnd):

        self._user_info = {
            "username": "",
            "password": ""
        }

        self._parent_wnd = parent_wnd
        self._this_wnd = None

        self._event_manager = c_event("register", "login", "unload")

        self._back_img = None
        self._btn_img = None

        self._back_canvas = None

        self._entry_username = None
        self._entry_password = None
        self._button_register = None
        self._button_login = None

        self._back_img_size = [0, 0]
        self._btn_img_size = [0, 0]

        self.__setup_window()

        # After we set up the window
        # we want to handle the unload event of it
        # to be able to create another one
        self._this_wnd.bind("<Destroy>", self.__unload_event)

    def __setup_window(self):
        """
        Setup everything related to the login_gui window
        """

        # Create Login Window,
        # set the Client window as top level / parent window
        self._this_wnd = Toplevel(self._parent_wnd)

        # Set title
        self._this_wnd.title("Login GUI")

        # Disable resize
        self._this_wnd.resizable(False, False)

        # Setup images
        self.__setup_images()

        # Setup window size
        self._this_wnd.geometry("{}x{}".format(self._back_img_size[0], self._back_img_size[1]))

        # Create and set the background with the correct images
        self._back_canvas = Canvas(self._this_wnd, width=self._back_img_size[0], height=self._back_img_size[1])
        self._back_canvas.pack(fill='both', expand=True)
        self._back_canvas.create_image(0, 0, anchor="nw", image=self._back_img)

        self.__create_elements()

    def __create_elements(self):
        """
                Create the ui elements in the window
                """

        # Username Label
        self._back_canvas.create_text(20, 30,
                                      text="Username:", font=FONT_BUTTON, fill=COLOR_BLACK, anchor="nw")

        # Username text box
        self._entry_username = Entry(self._back_canvas, font=FONT_BUTTON)
        self._entry_username.place(x=20, y=60)

        # Password Label
        self._back_canvas.create_text(20, self._back_img_size[1] / 2 + 30,
                                      text="Password:", font=FONT_BUTTON, fill=COLOR_BLACK, anchor="nw")

        # Password text box
        self._entry_password = Entry(self._back_canvas, font=FONT_BUTTON, show="*")
        self._entry_password.place(x=20, y=(self._back_img_size[1] / 2 + 60))

        # Button register
        self._button_register = Button(self._back_canvas,
                                       text="Register", font=FONT_BUTTON, command=self.__event_register, bd=0,
                                       image=self._btn_img, borderwidth=0, compound="center", fg="#c0c0c0",
                                       width=self._btn_img_size[0], height=self._btn_img_size[1],
                                       highlightthickness=0)
        self._button_register.place(
            x=(self._back_img_size[0] - self._btn_img_size[0] - 30),
            y=40)

        # Button login
        self._button_login = Button(self._back_canvas,
                                    text="Login", font=FONT_BUTTON, command=self.__event_login, bd=0,
                                    image=self._btn_img, borderwidth=0, compound="center", fg="#c0c0c0",
                                    width=self._btn_img_size[0], height=self._btn_img_size[1],
                                    highlightthickness=0)
        self._button_login.place(
            x=(self._back_img_size[0] - self._btn_img_size[0] - 30),
            y=40 + 60)

    def __setup_images(self):
        """
        Setup client gui images and save their data,

        use default images just resize them.
        we want to find out their original sizes,
        and decrease them
        """

        # Load images
        tmp_back_img = PhotoImage(file=BACKGROUND_IMAGE)
        tmp_btn_img = PhotoImage(file=BUTTON_IMAGE)

        # Save new sizes
        self._back_img_size = [int(tmp_back_img.width() / 1.5), int(tmp_back_img.height() / 1.5)]
        self._btn_img_size = [int(tmp_btn_img.width() / 1.5), int(tmp_btn_img.height() / 1.5)]

        # Delete temp images objects
        # since we dont need them
        del tmp_back_img
        del tmp_btn_img

        # Create new ones
        # with new sizes
        self._back_img = PhotoImage(file=BACKGROUND_IMAGE, width=self._back_img_size[0],
                                    height=self._back_img_size[1])
        self._btn_img = PhotoImage(file=BUTTON_IMAGE, width=self._btn_img_size[0], height=self._btn_img_size[1])

    def draw(self):
        """
        Draw function for the login gui window
        """

        self._this_wnd.mainloop()

    def __event_register(self):
        """
        Register event handle function,

        will get the username and password from the entries
        and call the callback function of register passing the json like data
        """

        self._username = self._entry_username.get()
        self._password = self._entry_password.get()

        data = {
            "username": self._username,
            "password": self._password
        }

        # self._register_callback(data)
        self._event_manager.call_event("register", data)

    def __event_login(self):
        """
        Login event handle function,

        will get the username and password from the entries
        and call the callback function of login passing the json like data
        """

        self._username = self._entry_username.get()
        self._password = self._entry_password.get()

        data = {
            "username": self._username,
            "password": self._password
        }

        # self._login_callback(data)
        self._event_manager.call_event("login", data)

    def __unload_event(self, _):
        self._event_manager.call_event("unload")

    def register_callback(self, *args):
        self._event_manager.register(*args)


#  endregion
