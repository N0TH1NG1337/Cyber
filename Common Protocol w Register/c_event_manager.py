"""
    Event.py - event object file

    last update : 05/04/2024
"""

from c_protocol import try_to_extract


def convert_args_to_dir(*args) -> dir:
    """
    Converts the arguments to dir

    first Arg : index
    send Arg : value
    """

    result = {}

    list_of_args = list(args)

    list_len = len(list_of_args)

    # Need to check for invalid arguments
    if list_len % 2 != 0:
        return None

    for i in range(0, list_len, 2):
        result[list_of_args[i]] = list_of_args[i + 1]

    return result


class c_event:

    def __init__(self, *args):
        # _event_data will store the current event information in dir
        # will get the event object as argument in callback
        # and access the data

        self._event_data = convert_args_to_dir(*args)

    def add(self, index: str, value: any) -> None:  # NOTE ! can be also to update argument
        self._event_data[index] = value

    def get(self, index) -> any:
        return try_to_extract(self._event_data, index)


class c_event_manager:

    def __init__(self, *args):
        self._events_handler = {}

        for event_name in list(args):
            self._events_handler[event_name] = {}

    def add_event(self, event_name):
        self._events_handler[event_name] = {}

    def register(self, event_name: str, function: any, function_name: str, get_args: bool) -> bool:
        self._events_handler[event_name][function_name] = {"method": function, "allow_args": get_args}
        return True

    def unregister(self, event_name, function_name):
        pass

    def call_event(self, event_name: str, event_obj: any) -> bool:
        if not self._events_handler[event_name]:
            return False

        if event_obj is None:
            event_obj = c_event()  # Create empty event_object

        for name in self._events_handler[event_name]:
            callback = self._events_handler[event_name][name]

            if callback["allow_args"]:
                callback["method"](event_obj)
            else:
                callback["method"]()

        return True
