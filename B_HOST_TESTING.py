import os
import pathlib
import platform
import pyfiglet
import pyttsx3

from tkinter import Button, Entry, Label, Tk, mainloop

engine = pyttsx3.init()


def main():
    while True:
        interface()


def create_and_manage_groups():
    current_groups = []
    new_groups = []

    print('GROUP OPTIONS: ', '\n', '\n', '1) CREATE OR VIEW CURRENT GROUPS       2) EDIT A GROUP', '\n',
          '\n', '3) REMOVE A GROUP', '\n', '\n', '0) RETURN TO MAIN MENU')
    separator_3()
    user_input = input('ENTER OPTION #: ')

    try:

        if int(user_input) == 1:
            separator_3()
            pass
        elif int(user_input) == 2:
            separator_3()
            pass
        elif int(user_input) == 3:
            separator_3()
            pass
        elif int(user_input) == 0:
            interface()

    except (TypeError, ValueError, UnicodeDecodeError, ZeroDivisionError) as e:
        print(e, '\n', ('-' * 100), '\n', 'INPUT ERROR, PLEASE RETRY SELECTION USING NUMBER KEYS: ')
        return


def create_programs_list():
    available_programs_list = []
    programs_list = []

    system_platform = platform.system()

    if str(system_platform).lower() in str("Windows").lower():
        print('COMPILING LIST OF AVAILABLE PROGRAMS')
        separator_3()

        for root, dirs, files in os.walk(r'C:/'):
            for programs in files:
                if programs.lower().endswith(r'.exe'):
                    program_names = programs[:-4]
                    available_programs_list.append([program_names, (pathlib.Path(root) / programs).as_posix()])

        for enumeration_number, listed_programs in enumerate(available_programs_list):
            programs_list.append([enumeration_number, '-', listed_programs[0], '-', listed_programs[1]])

    else:
        print("STILL WORKING ON LINUX")
        separator_3()

    return programs_list


def get_commands_gui():
    command_entered = []
    root = Tk()
    Label(root, text="YES?").grid(row=0)
    command = Entry(root)
    command.grid(row=0, column=1)

    def get_command_globals():
        command_entered.append(command.get())
        root.destroy()

    Button(root, text='ENTER COMMAND', command=get_command_globals).grid(row=0)
    mainloop()
    return command_entered[0]


def interface():
    separator_3()
    print(pyfiglet.figlet_format('BX-HOST', font='cybermedium'))
    separator_3()
    print('HOST OPTIONS: ', '\n', '\n', '1) GROUPS                               2) VIEW AVAILABLE PROGRAMS', '\n',
          '\n', '3) SEARCH PROGRAMS', '\n', '\n', '0) EXIT')
    separator_3()
    user_input = input('ENTER OPTION #: ')
    separator_3()

    try:

        if int(user_input) == 1:
            create_and_manage_groups()
        elif int(user_input) == 2:
            programs_list = [create_programs_list()]
            for programs_listed in programs_list:
                for programs in programs_listed:
                    print(programs[0], programs[1], programs[2], programs[3], programs[4])
        elif int(user_input) == 3:
            search_programs()
        elif int(user_input) == 0:
            exit()

    except (TypeError, ValueError, UnicodeDecodeError, ZeroDivisionError) as e:
        print(e, '\n', ('-' * 100), '\n', 'INPUT ERROR, PLEASE RETRY SELECTION USING NUMBER KEYS: ')
        return


def search_programs():
    programs_list = [create_programs_list()]
    commands_entered = [get_commands_gui()]

    narrowed_programs_list = []

    print('COMMAND ENTERED: ', commands_entered[0])
    separator_3()

    for programs_listed in programs_list:
        for programs in programs_listed:
            if str(commands_entered[0]).lower() in str(programs[2]).lower():
                narrowed_programs_list.append(programs)

    if narrowed_programs_list:
        for programs in narrowed_programs_list:
            print(programs[0], programs[1], programs[2], programs[3], programs[4])

        separator_3()
        print(' 1) LAUNCH A PROGRAM', '\n', '\n', '2) RETURN TO MAIN MENU')
        separator_3()
        user_input = input('ENTER OPTION #: ')

        try:

            if int(user_input) == 1:
                separator_3()
                program_selection = input('SELECT OPTION # FOR DESIRED PROGRAM: ')

                for listed_programs in narrowed_programs_list:
                    if int(program_selection) == int(listed_programs[0]):
                        os.startfile(str(listed_programs[4]))
                        engine.say('Launching:' + str(listed_programs[2]))
                        engine.runAndWait()
                        engine.stop()

            elif int(user_input) == 2:
                interface()

        except (TypeError, ValueError, UnicodeDecodeError, ZeroDivisionError) as e:
            print(e, '\n', ('-' * 100), '\n', 'INPUT ERROR, PLEASE RETRY SELECTION USING NUMBER KEYS: ')
            return

    elif not narrowed_programs_list:
        print('NO RESULTS FOUND: ')


def separator_3():
    for item in '\n', '-' * 100, '\n':
        print(item)


if __name__ == '__main__':
    main()
