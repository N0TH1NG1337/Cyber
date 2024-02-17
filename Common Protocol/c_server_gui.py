"""

Server GUI      .py

last update:    17/02/2024

"""

#  region Libraries

from c_server_bl import *
from tkinter import *

#  endregion


#  region Constants

DEFAULT_IP: str = "0.0.0.0"

FONT_TITLE: tuple = ("Calibri", 20)
FONT_BUTTON: tuple = ("Calibri", 14)

COLOR_BLACK: str = "#000000"
COLOR_DARK_GRAY: str = "#808080"
COLOR_LIGHT_GRAY: str = "#c0c0c0"

BUTTON_IMAGE: str = "Images\\gui_button.png"
BACKGROUND_IMAGE: str = "Images\\gui_bg.png"


#  endregion


#  region Client GUI Class

class c_server_gui:
    def __init__(self):
        self._server = None  # server bl obj

        self._window = None

        self._back_img = None
        self._btn_img = None

        self._back_canvas = None

        # UI
        self._start_button = None
        self._stop_button = None
        self._ip_entry = None
        self._port_entry = None
        self._receive_field = None

        self._back_img_size = [0, 0]
        self._btn_img_size = [0, 0]

        self.__setup_window()

    def __setup_window(self):
        """
        Setup server window
        """

        # Create and save window root
        self._window = Tk()

        # Set window title
        self._window.title("Server GUI")

        # Disable resize to fit with the background image
        self._window.resizable(False, False)

        # Setup images
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
        self._back_canvas.create_text(20, 30, text="Server", font=FONT_TITLE, fill=COLOR_DARK_GRAY, anchor="nw")

        self.__create_elements()

    def __create_elements(self):
        """
        Create the ui elements in the window
        """

        # Buttons
        self._start_button = Button(self._back_canvas,
                                    text="Start", font=FONT_BUTTON, command=self.__start_event, bd=0,
                                    image=self._btn_img, borderwidth=0, compound="center", fg="#c0c0c0",
                                    width=self._btn_img_size[0], height=self._btn_img_size[1],
                                    highlightthickness=0)
        self._start_button.place(x=self._back_img_size[0] - self._btn_img_size[0] - 30, y=40)

        self._stop_button = Button(self._back_canvas,
                                   text="Stop", font=FONT_BUTTON, command=self.__stop_event, bd=0,
                                   state="disabled",
                                   image=self._btn_img, borderwidth=0, compound="center", fg="#c0c0c0",
                                   width=self._btn_img_size[0], height=self._btn_img_size[1],
                                   highlightthickness=0)
        self._stop_button.place(x=self._back_img_size[0] - self._btn_img_size[0] - 30, y=40 + 46 + 30)

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

        # Receive
        self._back_canvas.create_text(10, 150 + 80, text="Received:", font=FONT_BUTTON, fill=COLOR_BLACK, anchor="nw")
        self._receive_field = Text(self._back_canvas, width=44, height=6, state="disabled")
        self._receive_field.place(x=10 + 100, y=150 + 80)

    def __setup_images(self):
        """
        Setup server gui images and save their data
        """

        # Load images
        self._back_img = PhotoImage(file=BACKGROUND_IMAGE)
        self._btn_img = PhotoImage(file=BUTTON_IMAGE)

        # Save their vectors
        self._back_img_size = [self._back_img.width(), self._back_img.height()]
        self._btn_img_size = [self._btn_img.width(), self._btn_img.height()]

    def __start_event(self):
        self._start_button.config(state="disabled")
        self._stop_button.config(state="normal")

        self._ip_entry.config(state="disabled")
        self._port_entry.config(state="disabled")

        ip = self._ip_entry.get()
        port = int(self._port_entry.get())

        self._server = c_server_bl(ip, port, self.__receive_event)

        if self._server and self._server.success:
            server_handle_thread = threading.Thread(target=self._server.server_process)
            server_handle_thread.start()

    def __stop_event(self):
        self._start_button.config(state="normal")
        self._stop_button.config(state="disabled")

        self._ip_entry.config(state="normal")
        self._port_entry.config(state="normal")

        self._server.update_server_flag(False)

    def __receive_event(self, msg):

        if msg:
            self._receive_field.config(state="normal")
            self._receive_field.insert("end", msg + "\n")
            self._receive_field.config(state="disabled")

    def draw(self):
        """
        Draw the client window
        """

        self._window.mainloop()


#  endregion


#  region main program and entry point

# Main function
def main():
    server = c_server_gui()
    server.draw()


# Entry Point
if __name__ == "__main__":
    main()

#  endregion
