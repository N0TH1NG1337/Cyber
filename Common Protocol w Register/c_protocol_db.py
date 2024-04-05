"""
    Protocol_db.py - protocol version for database

    last update : 05/04/2024
"""

#  region Libraries

from c_protocol import *

import sqlite3

#  endregion


#  region Protocol DataBase

class c_protocol_db(c_protocol, ABC):

    def __init__(self):

        self._valid_cmds = {
            "REGISTER": self.__register_user,
            "LOGIN": self.__login_user
        }

        self._last_error: str = ""
        self._last_success: bool = False

        self._database_name: str = "Users.db"

        self.__create_table()

    def create_request(self, cmd: str, args: str, data: dir) -> str:
        """
            Creates a request message by formatting the command and arguments.
        """

        return format_data(f"{cmd}>{args}")

    def create_response(self, cmd: str, args: list, data: dir) -> str:
        """
            Create valid response information,

            In case unsupported request "Non-supported cmd" will be returned
        """

        response = "None Supported CMD"

        if cmd in self._valid_cmds:
            self._last_success, key = self._valid_cmds[cmd](args)

            if self._last_success:
                # TODO : Remake and set Const in Protocol.py
                response = f"success,{cmd},{args[0]},{args[1]}"

                if key is not None:
                    response = response + f",{key}"
            else:
                response = self._last_error

        write_to_log(f"  Protocol Login  · response to client : {response} ")

        return format_data(f"REGISTRATION_INFO>{response}")

    #  region DataBase Manipulation

    def __create_table(self):
        connection = sqlite3.connect(self._database_name)
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            key TEXT NOT NULL);
        """)

        connection.commit()
        connection.close()

    def __register_user(self, information) -> (bool, str):

        connection = None
        success = False

        # Create new key for user
        key = Fernet.generate_key()
        cipher_suite = Fernet(key)

        try:
            connection = sqlite3.connect(self._database_name)
            cursor = connection.cursor()

            cursor.execute("""
            INSERT INTO users (username, password, key) VALUES (?, ?, ?);
            """, (cipher_suite.encrypt(information[0].encode()),
                  cipher_suite.encrypt(information[1].encode()), key.decode()))

            success = True
        except Exception as e:
            self._last_error = str(e)
            success = False

        if connection:
            connection.commit()
            connection.close()

        return success, key.decode()

    def __login_user(self, information) -> bool:

        connection = None
        success = False

        try:
            connection = sqlite3.connect(self._database_name)
            cursor = connection.cursor()

            cursor.execute("SELECT * FROM users WHERE username=?", (information[0],))

            received_data = cursor.fetchone()

            if received_data:
                password_raw = received_data[2]
                if password_raw == information[1]:
                    success = True
                else:
                    raise Exception("incorrect password")
            else:
                raise Exception("user not found")

        except Exception as e:
            self._last_error = str(e)
            success = False

        if connection:
            connection.close()

        return success

    #  endregion

    def get_last_success(self) -> bool:
        return self._last_success

    def get_cmds(self) -> list:
        """
            Returns valid cmds for Current Protocol
        """

        result = []

        for cmd_name in self._valid_cmds:
            result.append(cmd_name)

        return result

#  endregion
