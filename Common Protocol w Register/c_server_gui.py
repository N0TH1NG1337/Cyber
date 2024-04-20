"""
    Server_GUI.py - Server Application Later

    last update : 20/04/2024
"""

#  region Libraries

from c_server_bl import *
from tkinter import *

from tkinter import ttk as tk_extension
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


#  region Server GUI Class

class c_server_gui:

    def __init__(self):

        self._server = None

        self._window = None

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

        self._last_client = None
        self.__setup_window()

    #  region Setup Window

    def __setup_window(self):
        """
            Setup Server GUI Window
        """

        # Create and save window root
        self._window = Tk()

        # Set window title
        self._window.title("Server GUI")

        # Disable resize to fit with the background image
        self._window.resizable(False, False)

        # Setup images
        self.__setup_images()

        self._window.geometry("{}x{}".format(self._images["background"]["size"][0],
                                             self._images["background"]["size"][1]))

        self._back_canvas = Canvas(self._window,
                                   width=self._images["background"]["size"][0],
                                   height=self._images["background"]["size"][1])

        self._back_canvas.pack(fill='both', expand=True)
        self._back_canvas.create_image(0, 0,
                                       anchor="nw", image=self._images["background"]["image"])
        self._back_canvas.create_image(0, self._images["background"]["size"][1] / 2,
                                       anchor="nw", image=self._images["background"]["image"])

        # In-Application title
        self._back_canvas.create_text(20, 30, text="Server", font=FONT_TITLE, fill=COLOR_DARK_GRAY, anchor="nw")

        self.__create_elements()

    def __create_elements(self):
        """
            Create the ui elements in the window
        """

        buttons_x = self._images["background"]["size"][0] - self._images["button"]["size"][0] - 30

        # Start Button
        self.__create_button(
            "Start", "start_button",
            buttons_x, 40,
            self.__on_event_server_start)

        # Stop Button
        self.__create_button(
            "Stop", "stop_button",
            buttons_x, 40 + 46 + 30,
            self.__on_event_server_stop,
            "disabled")

        # IP Entry
        self.__create_text_input("IP:", "ip_entry", 10, 150, None, DEFAULT_IP)

        # Port Entry
        self.__create_text_input("Port:", "port_entry", 10, 150 + 40, None, str(PORT))

        # Receive Field
        self._back_canvas.create_text(10, 150 + 80, text="Receive:", font=FONT_BUTTON, fill=COLOR_BLACK,
                                      anchor="nw")
        self._ui["receive_field"] = Text(self._back_canvas, width=44, height=6, state="disabled")
        self._ui["receive_field"].place(x=10 + 100, y=150 + 80)

        # Client Table
        self._back_canvas.create_text(10, 150 + 80 * 3, text="Clients:", font=FONT_BUTTON, fill=COLOR_BLACK,
                                      anchor="nw")

        self._ui["client_table"] = tk_extension.Treeview(self._back_canvas, columns=("ip", "port"))
        self._ui["client_table"].place(x=10 + 100, y=150 + 80 * 3)

        self._ui["client_table"].column("#0", width=0, minwidth=0)

        self._ui["client_table"].heading("ip", text="client ip")
        self._ui["client_table"].column("ip", width=120, minwidth=120)

        self._ui["client_table"].heading("port", text="client port")
        self._ui["client_table"].column("port", width=120, minwidth=120)

        # Kick Button
        self.__create_button(
            "Kick Client", "kick_button",
            110, 150 + 80 * 6,
            self.__on_event_client_kick,
            "disabled")

        self._ui["client_table"].bind("<<TreeviewSelect>>", self.__on_event_focus_on_client)

    def __setup_images(self):
        """
        Setup client gui images and save their data
        """

        # Load images
        self._images["background"]["image"] = PhotoImage(file=BACKGROUND_IMAGE)
        self._images["button"]["image"] = PhotoImage(file=BUTTON_IMAGE)

        # Save their vectors
        self._images["background"]["size"] = [self._images["background"]["image"].width(),
                                              self._images["background"]["image"].height() * 2]

        self._images["button"]["size"] = [self._images["button"]["image"].width(),
                                          self._images["button"]["image"].height()]

    def draw(self):
        """
            Draw the server's window
        """

        self._window.mainloop()

    #  endregion

    #  region Server GUI Helpers

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

    #  endregion

    #  region Server Events

    def __on_event_server_start(self):
        """
            Server Start Event
        """

        try:
            ip = self._ui["ip_entry"].get()
            port = int(self._ui["port_entry"].get())

        except Exception as e:

            # Warn the user about invalid port input
            messagebox.showerror("Casting Error", "Please enter valid number as port")

            return

        # Handle GUI
        self._ui["start_button"].config(state="disabled")
        self._ui["stop_button"].config(state="normal")
        self._ui["ip_entry"].config(state="disabled")
        self._ui["port_entry"].config(state="disabled")

        self._server = c_server_bl()
        self._server.setup_server(ip, port)

        if self._server.get_success():

            self._server.register_callback("server_receive",
                                           self.__on_event_receive,
                                           "gui_receive")

            self._server.register_callback("client_connect",
                                           self.__on_event_client_connect,
                                           "gui_client_connect")

            self._server.register_callback("client_disconnect",
                                           self.__on_event_client_disconnect,
                                           "gui_client_disconnect")

            threading.Thread(target=self._server.start_server).start()

        else:

            # Otherwise we alart the user with the last error occurred in the
            # server bl side
            messagebox.showerror("Error on Start", self._server.get_last_error())

    def __on_event_server_stop(self):
        """
            Server Stop Process Event
        """

        self._ui["start_button"].config(state="normal")
        self._ui["stop_button"].config(state="disabled")

        self._ui["ip_entry"].config(state="normal")
        self._ui["port_entry"].config(state="normal")

        self._server.stop_server()

    def __on_event_receive(self, event):
        """
            Server Receive Event
        """

        message = f"{event.get('username')} - {event.get('cmd')} : {event.get('args')}"
        self._ui["receive_field"].config(state="normal")
        self._ui["receive_field"].insert("end", message + "\n")
        self._ui["receive_field"].config(state="disabled")

    def __on_event_client_connect(self, event):
        """
            Client Connect Event
        """

        client_addr = event.get("address")
        client_index = len(self._ui["client_table"].get_children())

        self._ui["client_table"].insert("", "end", values=(client_addr[0], client_addr[1]))

    def __on_event_client_disconnect(self, event):
        """
            Client Disconnect Event
        """

        client_addr = event.get("client_addr")

        # to delete from our table
        # we loop through all our available rows
        for item in self._ui["client_table"].get_children():

            # from the row we can get the port and ip values
            item_ip = self._ui["client_table"].item(item, "values")[0]
            item_port = self._ui["client_table"].item(item, "values")[1]

            # and compare them with our client we want to delete from
            # the table

            # NOTE ! need to compare both port and ip, since some clients can connect
            # from the same ip but different port.
            if (item_ip == client_addr[0] and
                    str(item_port) == str(client_addr[1])):
                # found our client, we delete him
                self._ui["client_table"].delete(item)

                # stop searching since we found it
                return

        # we didn't find our user. log error
        write_to_log(f"  Server    · failed to find client by ip / port : {client_addr}")

    def __on_event_focus_on_client(self, _):
        """
            Focus on client in the Table
        """

        selection = self._ui["client_table"].selection()

        if selection:
            # get the last client that
            # was focused in the table by TreeviewSelect event
            self._last_client = selection[0]

            self._ui["kick_button"].config(state="normal")

    def __on_event_client_kick(self):
        """
            Force the client to disconnect
        """

        if self._last_client is not None:
            values = self._ui["client_table"].item(self._last_client)["values"]

            self._server.kick_client((values[0], values[1]))

            self._last_client = None
            self._ui["kick_button"].config(state="disabled")

    #  endregion


#  endregion


#  region Entry Point

def main():
    c_server_gui().draw()


if __name__ == "__main__":
    main()

#  endregion
