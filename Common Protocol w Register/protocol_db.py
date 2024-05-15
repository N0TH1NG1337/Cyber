"""
    c_protocol_db.py - Protocol Version For DataBase File

    last update : 15/05/2024
"""

#  region @ Libraries

from protocol import *
from utils import *

import sqlite3

#  endregion


#  region @ Protocol DB Class

class c_protocol_db(c_protocol, ABC):

    def __init__(self):

        # Current protocol commands
        self._valid_cmds = {
            "REGISTER": self.__register_command,
            "LOGIN": self.__login_command
        }

        # Default header to response with log in information
        self._register_header = "REGISTRATION_INFO"

        # Some variables to use
        self._last_error: str = ""
        self._last_success: bool = False
        self._last_key_used: str = None

        # Current database file name
        self._database_name: str = "Users.db"

        # Call and setup users table
        self.__setup_table()

    def create_request(self, cmd: str, args: str, data: dict) -> str:
        """
            Creates a request message by formatting the command and arguments.
        """

        return c_protocol.format_value(f"{cmd}>{args}")

    def create_response(self, cmd: str, args: list, data: dict) -> str:
        """
            Create valid response information,

            In case unsupported request "Non-supported cmd" will be returned
        """

        response = "None Supported CMD"

        # Check if command is valid and can use
        if cmd in self._valid_cmds:

            # Get the operation result and set the last success
            self._last_success = self._valid_cmds[cmd](args)

            # If we logged in
            if self._last_success:

                # Set response with needed information
                response = f"{SUCCESS_CMD},{cmd},{args[0]}"

                if cmd == "REGISTER":
                    # Only in Register operation we receive the key
                    response = response + f",{self._last_key_used}"

            else:

                # Something went wrong. inform the client
                response = self._last_error

        # Log
        write_to_log(f"  Protocol DB   - response to client : {response} ")

        # Return formatted response
        return c_protocol.format_value(f"{self._register_header}>{response}")

    def get_cmds(self) -> any:
        """
            Returns valid cmds for current protocol
        """

        result = []

        for cmd_name in self._valid_cmds:
            result.append(cmd_name)

        return result

    def __setup_table(self):
        """
            Setup users table.

            If the table already exist ignore call
        """

        try:

            # Connect
            connection = sqlite3.connect(self._database_name)
            cursor = connection.cursor()

            # Create table if it doesn't exist
            cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    key TEXT NOT NULL);
            """)

            # Commit changes and close connection
            connection.commit()
            connection.close()

        except Exception as e:

            # Handle Fail
            self._last_error = str(e)
            write_to_log(f"  Protocol DB   - catch an exception on setup table() : {e}")

    def __register_command(self, information) -> bool:
        """
            Register client command function.

            Return the result and save the created key
        """

        connection = None
        success = False

        # Generate new key
        key = c_encryption.random_key(32)
        encryption = c_encryption(key)

        try:
            # Connect to database
            connection = sqlite3.connect(self._database_name)
            cursor = connection.cursor()

            # Insert user information
            cursor.execute("""
                INSERT INTO users (username, password, key) VALUES (?, ?, ?);""",
                (
                    information[0],                                 # Username
                    encryption.encrypt(information[1]).decode(),    # Encrypted password
                    key)                                            # Encryption Key
            )

            success = True

        except Exception as e:

            self._last_error = str(e)
            success = False

        # If our connection succeeded and we can finish
        if connection:
            connection.commit()
            connection.close()

        # Save key
        self._last_key_used = key

        # Return result
        return success

    def __login_command(self, information) -> bool:
        """
            Login client command function.

            Return the result
        """

        connection = None
        success = False

        key = None

        try:
            # Connect to database
            connection = sqlite3.connect(self._database_name)
            cursor = connection.cursor()

            # Search by username
            cursor.execute("SELECT * FROM users WHERE username=?",
                           (information[0],))

            # Get data
            received_data = cursor.fetchone()

            # Check if valid
            if not received_data:
                raise Exception("user not found")

            # We found user

            # Prepare for decryption
            key = received_data[3]
            encryption = c_encryption(key)

            # Both bytes
            original_password = encryption.decrypt(received_data[2])
            received_password = encryption.decrypt(information[1])

            if not original_password == received_password:
                raise Exception("incorrect password")

            success = True

        except Exception as e:

            success = False
            self._last_error = str(e)

        # Close connection
        if connection:
            connection.close()

        # Save key
        self._last_key_used = key

        # Return result
        return success

    def __call__(self, value_name: str) -> any:

        if value_name == "last_error":
            return self._last_error

        if value_name == "last_success":
            return self._last_success

        if value_name == "last_key":
            return self._last_key_used

        if value_name == "register_header":
            return self._register_header

        return None

#  endregion
