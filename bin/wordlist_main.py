import re

import pyfiglet
import logging
import os.path
import sqlite3
import termcolor

from logging.handlers import RotatingFileHandler
from time import sleep

# TODO: Abs/Rel Paths are fucked I think

"""
wordlist_main.py
Usage:
Options:
  -h, --help                Show this help
Examples:
"""

# What to cover:
# 1) Passwords
# 2) Usernames
# 3) Subdomains
# 5) File Extensions

# Basic Functionality for each:
# 1) Build an initial DB of values
# 2) Be able to insert \n separated list and add to the existing DB if not already present
# 3) Any duplicates are ignored
# 4) Ability to export DB back into a \n separated txt
# 5) Interactive functionality for arguments/logs/choosing what category the user wants to add shit to

# Random shit when done
# 1) PEP8
# 2) Post to github w/ complete guide
# 3) Fill out """ """ documentation in each function. And fill out """ """ usage section above this

# Classes ---------------------------------------------

class Bcolours:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# Program Start --------------------------------------------------------

def main():
    logger = _build_logger()
    print_menu(logger)

def print_menu(logger):
    ascii_title = pyfiglet.figlet_format("Wordlist Creator/Generator", font="slant")
    print(termcolor.colored(ascii_title, color='cyan'))

    wordlist_options = {
        0: [_help_main, 'Help'],
        1: [_password_main, 'Import New Passwords'],
        2: [_username_main, 'Import New Usernames'],
        3: [_subdomain_main, 'Import New Subdomains'],
        4: [_extension_main, 'Import New Extensions'],
        5: [_export_main, 'Export wordlist'],
        6: [_exit_main, 'Exit Program']
    }

    print(f"{Bcolours.OKBLUE}Please choose an option below")

    while True:
        print("")
        for key in wordlist_options.keys():
            print(f"{Bcolours.OKBLUE}{key} - {wordlist_options[key][1]}")
        print("")

        option = int(input("Enter your choice: "))
        if option not in range(0,7):
            print(f"{Bcolours.OKBLUE}Invalid option. Select 0-6\n")
            sleep(1)
            continue

        wordlist_options[option][0](logger)


# Primary Functionality --------------------------------------------------

def _help_main(logger):
    pass


def _password_main(logger):

    wordlist_options = {
        0: [_password_add_new, 'Create New Password Database'],
        1: [_password_add_existing, 'Add Passwords to Existing Database'],
        2: [None,'Return to Main Menu']
    }

    print(f"{Bcolours.OKBLUE}Adding wordlist to existing DB, or creating new DB?")

    while True:
        print("")
        for key in wordlist_options.keys():
            print(f"{Bcolours.OKBLUE}{key} - {wordlist_options[key][1]}")
        print("")

        option = int(input("Enter your choice: "))
        if option not in range(0,3):
            print(f"{Bcolours.OKBLUE}Invalid option. Select 0-2\n")
            sleep(1)
            continue

        if option == 2:
            return

        wordlist_options[option][0](logger)


def _password_add_new(logger):
    path = input("Input Abs/Rel path to password file: ")
    verification = _verify_path_exist(logger, path)

    if not verification:
        return

    sql_return = _db_build_main(logger, "password")
    conn, sql_cursor = sql_return[0], sql_return[1]
    sql_cursor.execute("""
                   CREATE TABLE pass_db(
                   password TEXT);
                    """)

    with open(path, errors='ignore') as passfile:
        print("Importing Passwords. This may take time depending on the size of the wordlist...")
        for line in passfile:
            line = line.replace("\n", "")
            sql_cursor.execute("INSERT INTO pass_db VALUES (?)", (line,))

        print(f"{Bcolours.OKGREEN}Passwords successfully imported\n")
        logger.info("Completed importing passwords to blank DB")

    conn.commit()
    conn.close()


def _password_add_existing(logger):
    new_pass_path = input("Input Abs/Rel path to password file: ")
    verification_pass = _verify_path_exist(logger, new_pass_path)
    if not verification_pass:
        return

    db_path = input("Input Abs/Rel path to existing password wordlist: ")
    verification_db = _verify_db_exist(db_path)
    if not verification_db:
        print(f"Could not find wordlist database at {db_path} or not a .db file. Check file path")
        return

    conn = sqlite3.connect(db_path)
    sql_cursor = conn.cursor()

    with open(new_pass_path, errors='ignore') as passfile:
        print("Importing Passwords. This may take time depending on the size of the wordlist...")
        for line in passfile:
            line = line.replace("\n", "")

            sql_cursor.execute("SELECT password FROM pass_db WHERE password =?", (line,))
            result = sql_cursor.fetchone()

            if not result:
                sql_cursor.execute("INSERT INTO pass_db VALUES (?)", (line,))

    print(f"{Bcolours.OKGREEN}Passwords successfully imported\n")
    logger.info(f"Completed importing passwords from {new_pass_path} to {db_path}")

    conn.commit()
    conn.close()

def _username_main(logger):
    pass

def _subdomain_main(logger):
    pass

def _extension_main(logger):
    pass

def _export_main(logger):
    pass

def _db_build_main(logger, option):
    path = f"..\\db\\{option}.db"

    if _verify_db_exist(path):
        print(f"Program attempted to create database at {path} but file already exists. Check file and try again.")
        logger.info(f"Attempted to create database at {path} but file already exists")
        return

    conn = sqlite3.connect(f"..\\db\\{option}.db")
    sql_cursor = conn.cursor()

    logger.info(f"Database at {path} created")
    return conn, sql_cursor

def _exit_main(logger):
    logger.info("Program Exit")
    print(f"{Bcolours.OKGREEN}Successfully Exited Program")
    exit(0)


# SQL -------------------------------------------------------------------

def _sql_add_main(logger):
    pass

# Loggers & File Verifiers  ---------------------------------------------
def _verify_db_exist(path):
    regex = re.compile(r'\.db$')
    if os.path.isfile(path) and regex.search(path):
        return True
    return False


def _verify_path_exist(logger, path):
    if os.path.isfile(path):
        try:
            with open(path, 'r') as file:
                file.readline()
                return True

        except IOError as e:
            print("File found but unreadable. Check log")
            logger.error(f"File at {path} found but unreadable. Error: {e}")
            return False

        except UnicodeDecodeError as e:
            print("File found but invalid characters. Check log")
            logger.error(f"File at {path} found but Unicode Error. Error: {e}")
            return False

    print(f"Cannot find file at {path}. Check path and try again")
    logger.info(f"Failed to find file at {path}")
    return False


def _build_logger():
    """ Build Logger for the program """
    directory = os.path.dirname(os.path.abspath(__file__))
    os.chdir(directory)

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    file_handler_info = RotatingFileHandler('../logs/main_info.log', maxBytes=1048576)
    file_handler_warning = RotatingFileHandler('../logs/main_warn.log', maxBytes=1048576)
    file_handler_error = RotatingFileHandler('../logs/main_error.log', maxBytes=1048576)

    file_handler_info.setLevel(logging.INFO)
    file_handler_warning.setLevel(logging.WARNING)
    file_handler_error.setLevel(logging.ERROR)

    handlers = [file_handler_info, file_handler_warning, file_handler_error]
    formatter = logging.Formatter('%(asctime)s || %(levelname)s || %(message)s || %(name)s')

    for handler in handlers:
        logger.addHandler(handler)
        handler.setFormatter(formatter)

    return logger


if __name__ == "__main__":
    main()