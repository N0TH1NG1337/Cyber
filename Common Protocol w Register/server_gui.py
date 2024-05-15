"""
    c_server_gui.py - Server Application Layer File

    last update : 15/05/2024
"""

#  region @ Libraries

from server_bl import *
from tkinter import *

from tkinter import ttk as tk_extension

#  endregion


#  region @ Constants

DEFAULT_IP: str = "0.0.0.0"

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


#  region @ Server GUI Class

class c_server_gui:

    def __init__(self):
        self._server = None

        # Client window obj
        self._window = None

        # Images data
        self._button_img = c_image()
        self._background_img = c_image()

        # Back canvas
        self._back_canvas = None

        # UI Elements handler
        self._ui = {}

        self._last_client = None

        # Setup window
        self.__setup_window()

    #  region GUI Setup

    def __setup_window(self):
        """
            Setup window
        """
        # Create and save window root
        self._window = Tk()

        # Set window title
        self._window.title("Server GUI")

        # Disable resize to fit with the background image
        self._window.resizable(False, False)

        # Setup images
        self.__setup_images()

        # Set window Size
        self._window.geometry(f"{self._background_img.x}x{self._background_img.y * 2}")

        # Setup background
        self._back_canvas = Canvas(self._window, width=self._background_img.x, height=self._background_img.y * 2)
        self._back_canvas.pack(fill='both', expand=True)
        self._back_canvas.create_image(0, 0, anchor="nw", image=self._background_img())
        self._back_canvas.create_image(0, self._background_img.y, anchor="nw", image=self._background_img())

        # In-Application title
        self._back_canvas.create_text(20, 30, text="Server", font=FONT_TITLE, fill=COLOR_DARK_GRAY, anchor="nw")

        self.__create_elements()

    def __create_elements(self):
        """
            Create interface elements
        """

        button_x_axis = self._background_img.x - self._button_img.x - 30

        # Start Server Button
        self.create_button("Start", "start_button",
                           button_x_axis, 40,
                           self.__on_event_server_start)

        # Stop Server Button
        self.create_button("Stop", "stop_button",
                           button_x_axis, 40 + 46 + 30,
                           self.__on_event_server_stop,
                           "disabled")

        # Ip Entry
        self.create_text_input("IP:", "ip_entry", 10, 150, None, DEFAULT_IP)

        # Port Entry
        self.create_text_input("Port:", "port_entry", 10, 190, None, str(DEFAULT_PORT))

        # Receive Field
        self.create_big_text_input("Receive:", "receive_field", 10, 150 + 80, "disabled", 45, 8)

        # Client Table
        setup = self.create_table("Clients:", "client_table", 10, 150 + 80 * 3, ("ip", "port", "log_in", "username"))
        setup("#0", 0)
        setup("ip", 120, "client ip")
        setup("port", 120, "client port")
        setup("log_in", 120, "logged in")
        setup("username", 120, "client username")

        # Kick Button
        self.create_button("Kick Client", "kick_button",
                           110, 150 + 80 * 6,
                           self.__on_event_client_kick,
                           "disabled")

        # Bind function to interact event to the Table
        # __on_event_focus_on_client
        self._ui["client_table"].bind("<<TreeviewSelect>>", self.__on_event_focus_on_client)

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
            Create a new single line text input in the menu
        """

        if text:
            self._back_canvas.create_text(x_axis, y_axis, text=text, font=FONT_BUTTON, fill=COLOR_BLACK,
                                          anchor="nw")

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
            self._back_canvas.create_text(x_axis, y_axis, text=text, font=FONT_BUTTON, fill=COLOR_BLACK,
                                          anchor="nw")

        self._ui[index] = Text(self._back_canvas, width=width, height=height)
        self._ui[index].place(x=x_axis + 100, y=y_axis)

        if default_state:
            self._ui[index].config(state=default_state)

    def create_table(self, text, index, x_axis, y_axis, default_columns):
        """
            Create a new table in the menu
        """

        if text:
            self._back_canvas.create_text(x_axis, y_axis, text=text, font=FONT_BUTTON, fill=COLOR_BLACK,
                                          anchor="nw")

        self._ui[index] = tk_extension.Treeview(self._back_canvas, columns=default_columns)
        self._ui[index].place(x=x_axis + 100, y=y_axis)

        def setup_column(column_id, width, header=None):
            if header:
                self._ui[index].heading(column_id, text=header)

            self._ui[index].column(column_id, width=width, minwidth=width)

        return setup_column

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

    def set(self, index, *args, **kwargs):
        """
            Set to specific item a new value
        """

        if index not in self._ui:
            raise Exception("Invalid UI Index")

        self._ui[index].insert(*args, **kwargs)

    def find_client(self, ip, port) -> any:
        """
            Try to find a client in the table using ip and port

            Return None on fail and item on success
        """

        for item in self._ui["client_table"].get_children():

            # From the row we can get the port and ip values
            item_ip = self._ui["client_table"].item(item, "values")[0]
            item_port = self._ui["client_table"].item(item, "values")[1]

            # Compare
            if (item_ip == ip and
                    str(item_port) == str(port)):

                # Return if found
                return item

        # Failed
        return None

    #  endregion

    #  region GUI Events

    @utils.safe_call(True, write_to_log)
    def __on_event_server_start(self):
        """
            Server start event
        """

        ip = self.get("ip_entry")
        port = self.get("port_entry", int)

        # Handle GUI
        self.update_state("start_button", "disabled")
        self.update_state("stop_button", "normal")
        self.update_state("ip_entry", "disabled")
        self.update_state("port_entry", "disabled")

        # Create and setup server bl object
        self._server = c_server_bl()
        self._server.setup_server(ip, port)

        # Check setup result
        if not self._server("success"):
            raise Exception(self._server("last_error"))

        # Register callback functions
        self._server("server_receive") + (self.__on_event_server_receive, "gui_receive", True)
        self._server("client_connect") + (self.__on_event_client_connect, "gui_client_connect", True)
        self._server("client_disconnect") + (self.__on_event_client_disconnect, "gui_client_disconnect", True)
        self._server("client_log_in") + (self.__on_event_client_log_in, "gui_client_log_in", True)

        # Start a thread to catch messages
        threading.Thread(target=self._server.start_server).start()

    @utils.safe_call(True, write_to_log)
    def __on_event_server_stop(self):
        """
            Server stop event
        """

        # Handle GUI
        self.update_state("start_button", "normal")
        self.update_state("stop_button", "disabled")

        self.update_state("ip_entry", "normal")
        self.update_state("port_entry", "normal")

        # Stop the server
        self._server.stop_server()

    @utils.safe_call(True, write_to_log)
    def __on_event_server_receive(self, event):
        """
            Server received message evnet
        """

        # Get event information
        username = event("username")
        command = event("command")
        arguments = event("arguments")

        # Format message
        message = f"{username} - {command} : {arguments}"

        # Update the receive field
        self.update_state("receive_field", "normal")
        self.set("receive_field", "end", message + "\n")
        self.update_state("receive_field", "disabled")

    @utils.safe_call(True, write_to_log)
    def __on_event_client_connect(self, event):
        """
            Client connects to the server event
        """

        # Get client address
        client_addr = event("address")
        if client_addr is None:
            return

        # Insert to the table
        self._ui["client_table"].insert("", "end", values=(client_addr[0], client_addr[1], "False"))

    @utils.safe_call(True, write_to_log)
    def __on_event_client_disconnect(self, event):
        """
            Client disconnects from the server event
        """

        # Get client address
        client_addr = event("client_addr")
        if client_addr is None:
            return

        # Find it
        item = self.find_client(client_addr[0], client_addr[1])
        if item is None:
            return

        # Delete from the table
        self._ui["client_table"].delete(item)

    @utils.safe_call(True, write_to_log)
    def __on_event_client_log_in(self, event):
        """
            Client successfully logs in
        """

        # Get client address
        client_addr = event("address")
        if client_addr is None:
            return

        # Find it in the table
        item = self.find_client(client_addr[0], client_addr[1])
        if item is None:
            return

        # Update information
        self._ui["client_table"].set(item, "log_in", "True")
        self._ui["client_table"].set(item, "username", event("username"))

    @utils.safe_call(True, write_to_log)
    def __on_event_focus_on_client(self, _):
        """
            Select client in the table event
        """

        selection = self._ui["client_table"].selection()

        if selection:
            # get the last client that
            # was focused in the table by TreeviewSelect event
            self._last_client = selection[0]

            self.update_state("kick_button", "normal")

    @utils.safe_call(True, write_to_log)
    def __on_event_client_kick(self):
        """
            Kick button press event
        """

        if self._last_client is None:
            return

        if self._server is None:
            return

        # Get the information from the client we want to kick
        values = self._ui["client_table"].item(self._last_client)["values"]

        # Kick
        self._server.kick_client((values[0], values[1]))

        # Update the information
        self._last_client = None
        self.update_state("kick_button", "disabled")

    #  endregion

    def run(self):
        """
            Draw menu
        """

        self._window.mainloop()


#  endregion


# Entry Point

def main():
    c_server_gui().run()


if __name__ == "__main__":
    main()
