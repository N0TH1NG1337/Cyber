"""
    Protocol_db.py - protocol version for database

    last update : 20/04/2024
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
        self._last_key_used: str = None

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
                response = f"success,{cmd},{args[0]}"

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

            _pass = cipher_suite.encrypt(information[1].encode()).decode()
            print(information[1])
            print(len(information[1]))
            print(_pass)

            cursor.execute("""
            INSERT INTO users (username, password, key) VALUES (?, ?, ?);
            """, (information[0], _pass, key.decode()))

            success = True
        except Exception as e:
            self._last_error = str(e)
            success = False

        if connection:
            connection.commit()
            connection.close()

        self._last_key_used = key.decode()

        return success, self._last_key_used

    def __login_user(self, information) -> (bool, str):

        connection = None
        success = False

        key = None

        try:
            connection = sqlite3.connect(self._database_name)
            cursor = connection.cursor()

            cursor.execute("SELECT * FROM users WHERE username=?", (information[0],))

            received_data = cursor.fetchone()

            if received_data:

                # Due to some odd reason our encryption value different,
                # Although it is the same key
                key = received_data[3]
                cipher = Fernet(received_data[3])
                original = cipher.decrypt(received_data[2].encode()).decode()
                received = cipher.decrypt(information[1].encode()).decode()

                if original == received:
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

        self._last_key_used = key

        return success, None

    #  endregion

    def get_last_success(self) -> bool:
        return self._last_success

    def get_last_key(self) -> str:
        return self._last_key_used

    def get_cmds(self) -> list:
        """
            Returns valid cmds for Current Protocol
        """

        result = []

        for cmd_name in self._valid_cmds:
            result.append(cmd_name)

        return result

#  endregion
