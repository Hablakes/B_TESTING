import random
import string
import time

from tkinter import filedialog, Tk

inverse_bytes_list = []
normal_bytes_list = []


def main():
    pass


def get_bytes_from_files(filename):
    try:
        with open(filename, 'rb') as f:
            for byte in f.read():
                yield byte

    except (TypeError, ValueError, UnicodeDecodeError, ZeroDivisionError) as e:
        print(e)
        separator()
        print('INPUT ERROR, PLEASE RETRY SELECTION USING NUMBER KEYS: ')
        return


def inverse_bytes():
    for bytes_found in get_bytes_from_files(tk_gui_file_selection_window()):
        bytes_found = int(bytes_found)
        bytes_remainder = int(256 - bytes_found)
        inverse_bytes_list.append(bytes_remainder)


def inverse_bytes_enumerated():
    for enumeration_number, bytes_found in enumerate(get_bytes_from_files(tk_gui_file_selection_window())):
        bytes_found = int(bytes_found)
        bytes_remainder = int(256 - bytes_found)
        inverse_bytes_list.append([enumeration_number, bytes_remainder])


def normal_bytes():
    for bytes_found in get_bytes_from_files(tk_gui_file_selection_window()):
        bytes_found = int(bytes_found)
        normal_bytes_list.append(bytes_found)


def normal_bytes_enumerated():
    for enumeration_number, bytes_found in enumerate(get_bytes_from_files(tk_gui_file_selection_window())):
        bytes_found = int(bytes_found)
        normal_bytes_list.append([enumeration_number, bytes_found])


def random_number_for_multiplier_bit():
    multiplier_digit = random.randint(1, 9)
    return int((multiplier_digit % 9) + 1)


def random_number_with_obscurer_digits(number_of_digits):
    number_range_start = 10 ** (number_of_digits - 1)
    number_range_end = (10 ** number_of_digits) - 1
    return random.randint(number_range_start, number_range_end)


def random_string_with_one_time_pad_characters(number_of_characters):
    one_time_pad_characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(one_time_pad_characters) for _ in range(number_of_characters))


def rotate_list_as_rotor(character_set, rotations):
    return character_set[rotations:] + character_set[:rotations]


def separator():
    for item in '\n', '-' * 100, '\n':
        print(item)


def tk_gui_file_selection_window():
    root = Tk()
    root.withdraw()
    root.update()
    selected_file = filedialog.askopenfilename()
    root.destroy()
    return selected_file


start = time.time()

if __name__ == '__main__':
    main()

end = time.time()
test_time = round(end - start, 2)
separator()
print('TIME ELAPSED:', test_time, 'Seconds')
separator()
