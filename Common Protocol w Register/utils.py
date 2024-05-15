"""
    utils.py - Utilities File

    last update : 15/05/2024
"""

#  region @ Libraries

from functools import wraps
import random
import time
from tkinter import messagebox

#  endregion


#  region @ Utils Handle

class utils:

    @staticmethod
    def extract(directory: dict, index: any, direct_cast=None) -> any:
        """
            Handle extraction from directory,
            since python cannot just return None on fail.

            Return value on success,
            None on fail
        """

        index_type = type(index)

        if index_type != int and index_type != str:
            return None

        try:
            value = directory[index]

            if direct_cast is not None:
                return direct_cast(value)

            return value
        except Exception:
            return None

    @staticmethod
    def find_key(data: dict) -> any:
        """
            Will try to find the key in the data
        """

        return utils.extract(data, "key")

    @staticmethod
    def safe_call(show_messagebox=False, call_on_fail=None):
        """
            Safe call wrap function
        """

        def decorator(function):
            @wraps(function)
            def safe_fn(*args, **kwargs):

                try:
                    return function(*args, **kwargs)

                except Exception as e:

                    error_msg = f"Found error in function {function.__name__}:\n{e}"

                    if show_messagebox:
                        messagebox.showerror(title="Error Occurred",
                                             message=error_msg)

                    if call_on_fail is not None:
                        call_on_fail(error_msg)

                    return None

            return safe_fn

        return decorator

#  endregion


#  region @ Xor Encryption Class

class c_encryption:
    """
        XOR Encryption Class.

        Much easier to use than Fernet but less "secure"
    """

    def __init__(self, key: any):
        # Key - can be or string or dict with the key

        self._key = None

        if type(key) == dict:
            # Try to find the key
            key = utils.find_key(key)

        if key is None or type(key) != str:
            return

        try:
            self._key = bytes.fromhex(key)
        except Exception:
            self._key = key.encode()

    def encrypt(self, message: any) -> bytes:
        """
            Encrypt the message (string / bytes)

            Return encrypted bytes
        """

        if type(message) == str:
            return self.encrypt(message.encode())

        if self._key is None:
            return message

        encrypted_bytes = []

        for i in range(len(message)):
            # Perform XOR operation for each character and key byte
            encrypted_bytes.append(message[i] ^ self._key[i % len(self._key)])

        return bytes(encrypted_bytes)

    def decrypt(self, message: any) -> bytes:
        """
            Decrypts the message (string / bytes)

            Return decrypted bytes
        """

        if type(message) == str:
            return self.decrypt(message.encode())

        if self._key is None:
            return message

        decrypted_bytes = []

        for i in range(len(message)):
            # Perform XOR operation for each byte and key byte
            decrypted_bytes.append(message[i] ^ self._key[i % len(self._key)])

        return bytes(decrypted_bytes)

    @staticmethod
    def random_key(key_length: int = 16) -> str:
        """
            Generate random key
        """

        if key_length < 0:
            raise Exception("Invalid Key Length")

        # Seed the random number generator
        random.seed(time.time())

        # Characters to choose from
        characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

        # Generate random characters
        random_letters = []
        for _ in range(key_length):
            random_letters.append(random.choice(characters))

        key = "".join(random_letters)

        return key

#  endregion


#  region @ Events Classes and Handles

class c_event:
    """
        Event Class.
    """

    def __init__(self):

        # Event information
        self._event_data = {}

        # Event callback functions
        self._event_functions = {}

    def __get(self, index) -> any:
        """
            Receive event data function.

            Called within the callback function
        """

        return utils.extract(self._event_data, index)

    def __call__(self):
        """
            Execute the event and call all the functions
        """

        for function_name in self._event_functions:
            method_data = self._event_functions[function_name]

            if method_data["allow_args"]:
                method_data["method"](self.__get)
            else:
                method_data["method"]()

    def __add__(self, information: tuple):
        """
            Add data to event or register callback function
        """

        data_len: int = len(information)

        if data_len == 2:
            # We want to add/update information
            self._event_data[information[0]] = information[1]

            return

        if data_len == 3:
            # We want to add function
            self._event_functions[information[1]] = {
                "method": information[0],
                "allow_args": information[2]
            }

            return

        raise Exception("Invalid data structure added")

#  endregion
