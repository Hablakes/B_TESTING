import os
import random
import string
import time

import pyfiglet
from tkinter import filedialog, Tk


def main():
    while True:
        interface()


def interface():

    # interface for using the program
    separator_3()
    print(pyfiglet.figlet_format('BX-CRYPT', font='cybermedium'))
    separator_1()
    print('\n', '\n', 'ENCRYPTION OPTIONS: ', '\n', '\n', '1) ENCRYPT A MESSAGE         2) DECRYPT A MESSAGE', '\n',
          '\n', '3) ENCRYPT A FILE            4) DECRYPT A FILE', '\n', '\n', '0) EXIT')
    separator_3()

    user_input = input('ENTER OPTION #: ')

    separator_3()

    try:

        if int(user_input) == 1:
            encrypt_ui(interface_selection=1)
        elif int(user_input) == 2:
            decrypt_ui(interface_selection=1)
        elif int(user_input) == 3:
            encrypt_ui(interface_selection=2)
        elif int(user_input) == 4:
            decrypt_ui(interface_selection=2)
        elif int(user_input) == 0:
            exit()

    except (TypeError, ValueError, UnicodeDecodeError, ZeroDivisionError) as e:
        print(e, '\n', ('-' * 100), '\n', 'INPUT ERROR, PLEASE RETRY SELECTION USING NUMBER KEYS: ')
        return


def encrypt_ui(interface_selection):
    file_bytes_list = []
    key_list = []
    user_file_filename_list = []

    try:

        if int(interface_selection) == 1:
            print(pyfiglet.figlet_format('ENTER MESSAGE TO ENCRYPT: ', font='cybermedium'))
            separator_3()

            message = input('ENTER MESSAGE: ')

            # loop through bytes in message and encode them to unicode (UTF-8)
            for message_bytes in bytes(message.encode('utf-8')):

                # append each number to "file_bytes_list"
                file_bytes_list.append(message_bytes)

        elif int(interface_selection) == 2:
            print(pyfiglet.figlet_format('INPUT FILE TO ENCRYPT: ', font='cybermedium'))
            separator_3()

            # use tk gui module to select file to encrypt
            user_file = tk_gui_file_selection_window()

            # grab the filename of the "user-file" selected for output display
            user_file_filename = user_file.rsplit('/', 1)[-1]
            user_file_filename_list.append(user_file_filename)

            print('FILE SELECTED: ', user_file_filename)

            # loop through bytes in file selected and encode them to unicode (UTF-8)
            # append each number to "file_bytes_list"
            file_bytes_list.extend(get_bytes_from_files(user_file))

    except (TypeError, ValueError, UnicodeDecodeError, ZeroDivisionError) as e:
        print(e, '\n', ('-' * 100), '\n', 'INPUT ERROR, PLEASE RETRY SELECTION USING NUMBER KEYS: ')
        return

    # get length of the digits in the file_bytes_list to be used if creating a one-time pad
    file_bytes_length = int(len(file_bytes_list))

    separator_3()
    print('SYMMETRICAL KEY OPTIONS: ', '\n', '\n', '1) USE CUSTOM KEY            2) CREATE ONE TIME PAD')
    separator_3()

    key = input('ENTER OPTION #: ')

    separator_3()

    try:

        if int(key) == 1:

            # allow user to input a custom key, of any desired length
            key = input('ENTER KEY: ')
            key_list.append(key)

        elif int(key) == 2:

            # create container for key with the file extension .bxk
            one_time_pad_file_path = os.path.expanduser(r'~/{0}').format('ENCRYPTED_MESSAGE.bxk')

            # create one-time pad that is the same length in digits or characters as the message or file-bytes
            # to encrypt
            key_list.append(random_string_with_one_time_pad_characters(file_bytes_length))

            with open(one_time_pad_file_path, 'w') as f:

                # loop through the key characters found and write them out to the file specified in the
                # "one_time_pad_file_path"
                for key_characters in key_list:
                    f.write(key_characters)

            # display path of the key file
            print('KEY FILE LOCATION: ', os.path.abspath(one_time_pad_file_path))

    except (TypeError, ValueError, UnicodeDecodeError, ZeroDivisionError) as e:
        print(e, '\n', ('-' * 100), '\n', 'INPUT ERROR, PLEASE RETRY SELECTION USING NUMBER KEYS: ')
        return

    separator_3()

    # create the encrypted numbers list and rotate based on parameters in the "encrypt_function"
    rotated_semantic_encryption_list = encrypt(key_list, file_bytes_list)

    if int(interface_selection) == 1:

        encrypted_file_path = os.path.expanduser(r'~/{0}').format('ENCRYPTED_MESSAGE.bxc')

        with open(encrypted_file_path, 'w') as f:

            # loop through "rotated_semantic_encryption_list" and write out numbers found as the final encrypted file
            # to the path / name of the "encrypted_file_path"
            for rotated_encrypted_numbers in rotated_semantic_encryption_list:
                f.write(str(int(rotated_encrypted_numbers)))
                f.write('\n')
            f.close()

        print(pyfiglet.figlet_format('MESSAGE ENCRYPTED SUCCESSFULLY', font='cybermedium'))
        separator_3()

        # display path of the encrypted message / file
        print('ENCRYPTED FILE LOCATION: ' + os.path.abspath(encrypted_file_path))

    elif int(interface_selection) == 2:

        # append .bxc to the original file-name of the "user_file" selected
        encrypted_file_path = os.path.expanduser(r'~/{0}').format(user_file_filename_list[0]) + '.bxc'

        # loop through "rotated_semantic_encryption_list" and write out numbers found as the final encrypted file
        # to the path / name of the "encrypted_file_path"
        with open(encrypted_file_path, 'w') as f:
            for encrypted_numbers in rotated_semantic_encryption_list:
                f.write(str(int(encrypted_numbers)))
                f.write('\n')
            f.close()

        print(pyfiglet.figlet_format('FILE ENCRYPTED SUCCESSFULLY', font='cybermedium'))
        separator_3()
        print('ENCRYPTED FILE LOCATION: ' + os.path.abspath(encrypted_file_path))


def encrypt_message(key, text):

    # use encrypt function to loop through characters in message
    return encrypt(key, [ord(x) for x in text.encode('utf-8')])


def encrypt(key_list, file_byte_numbers_list):
    encrypted_numbers_list = []
    semantic_encryption_list = []

    # get the current time in integer form
    current_time = int(time.time())

    # get a pseudo-random three digit number based on the current time
    time_bit = int(abs(current_time) % 1000)

    # get the length of the "time_bit" grabbed
    time_bit_length = int(len(str(time_bit)))

    # grab a random number to use as a multiplier for the "numbers in part of the encryption schema"
    multiplier_bit = int(random_number_for_multiplier_bit())

    # loop through and enumerate the numbers (in rows) gotten from the "file_byte_numbers_list"
    for enumeration_number, file_byte in enumerate(file_byte_numbers_list):

        # get the unicode (UTF-8) number that represents each of the character(s) in the message to encrypt
        file_byte_character_ordinal = int(file_byte)

        # get the unicode (UTF-8) number that represents each of the character(s) in the key used to encrypt
        key_enumeration_ordinal = int(ord(''.join(key_list)[enumeration_number % len(''.join(key_list))]))

        # use the pseudo-random numbers and apply the first encryption schema below to each digit of the message or
        # line in the file-bytes if encrypting a file
        multiplied_file_bytes_number_integer = int(
            (file_byte_character_ordinal * key_enumeration_ordinal) * multiplier_bit)

        # append results to "encrypted_numbers_list"
        encrypted_numbers_list.append(multiplied_file_bytes_number_integer)

    # loop though the "encrypted_numbers_list"
    for multiplied_numbers in encrypted_numbers_list:

        # apply second layer of encryption schema to create a changing /
        # semantic result (so that the an identical message encrypted with the same key does not always output the
        # same result, helping with frequency analysis attacks"
        pseudo_random_multiplied_numbers = int(multiplied_numbers + (time_bit * multiplier_bit))

        # append results to the "semantic_encryption_list"
        semantic_encryption_list.append(pseudo_random_multiplied_numbers)

    # get total amount of the average size of the numbers in the read out file-bytes
    encrypted_number_lengths = [len(str(x)) for x in semantic_encryption_list]

    # get the average length of the numbers in the set "encrypted number lengths"
    average_encrypted_number_length = int(sum(encrypted_number_lengths) / len(encrypted_number_lengths))

    # get the appropriate length for the "time_bit_obscurer"
    time_bit_obscurer_length = int(average_encrypted_number_length - time_bit_length)

    # pick a random number between 2-9 for as many digits as needed based on the results of
    # "time_bit_obscurer_length"
    time_bit_obscurer_random_number = random_number_with_obscurer_digits(time_bit_obscurer_length)

    # create the "obscurer_bits" variable to hide this in the message
    # (which will be needed for decryption on the other side)
    obscurer_bits = int(str(time_bit) + str(multiplier_bit) + str(time_bit_obscurer_random_number))

    # append the "obscurer_bits" to the end of the "semantic_encryption_list"
    semantic_encryption_list.append(obscurer_bits)

    # rotate the entire "semantic_encryption_list" forwards by the "average_encrypted_number_length"
    rotated_semantic_encryption_list = rotate_list_as_rotor(semantic_encryption_list, average_encrypted_number_length)

    return rotated_semantic_encryption_list


def decrypt_ui(interface_selection):
    key_list = []

    print(pyfiglet.figlet_format('ENTER FILE TO DECRYPT: ', font='cybermedium'))
    separator_3()

    # use tk gui module to select file to decrypt
    user_file = tk_gui_file_selection_window()

    # grab the filename of the "user-file" selected
    user_file_filename = user_file.rsplit('/', 1)[-1]

    # strip the .bxc file extension from the "user_file"
    user_file_original_filename = user_file.rsplit('.', 1)[0].rsplit('/', 1)[-1]

    print('ENCRYPTED FILE SELECTED: ', user_file_filename)
    separator_3()
    print('SYMMETRICAL KEY OPTIONS: ', '\n', '\n', '1) USE CUSTOM KEY            2) IMPORT ONE TIME PAD')
    separator_3()

    key = input('ENTER OPTION #: ')

    separator_3()

    try:
        if int(key) == 1:
            # ask the user for the known key, to be typed in via the console
            key = input('ENTER KEY: ')
            key_list.append(key)
            separator_3()

        elif int(key) == 2:
            # use tk gui module to select one-time pad to use for decryption
            key_file = tk_gui_file_selection_window()

            with open(key_file, 'r') as f:
                for key_characters in f:
                    key_list.append(key_characters)

    except (TypeError, ValueError, UnicodeDecodeError, ZeroDivisionError) as e:
        print(e, '\n', ('-' * 100), '\n', 'INPUT ERROR, PLEASE RETRY SELECTION USING NUMBER KEYS: ')
        return

    # create tuple with the "key_list" and the "user_file" to be decrypted
    decrypted_file_bytes_list = decrypt_file(key_list, user_file)

    try:

        if int(interface_selection) == 1:
            decrypted_message_list = []

            # display key used for decryption
            print('KEY SELECTED: ', key_list[0])
            separator_3()
            print(pyfiglet.figlet_format('MESSAGE DECRYPTED SUCCESSFULLY', font='cybermedium'))
            separator_3()

            print('DECRYPTED MESSAGE: ', '\n', '\n')

            # loop through the numbers in the "decrypted_message_list", and use the number(s) to get the character
            # that number represents from the unicode (UTF-8) set
            for decrypted_numbers in decrypted_file_bytes_list:
                decrypted_message_list.append(chr(decrypted_numbers))

            # display decrypted message in the console
            print(''.join(decrypted_message_list))

        elif int(interface_selection) == 2:
            decrypted_file_path = os.path.expanduser(r'~/{0}').format(user_file_original_filename)

            try:

                # re-construct the file after decryption
                with open(decrypted_file_path, 'wb') as f:
                    f.write(bytearray(decrypted_file_bytes_list))

            except (TypeError, ValueError, UnicodeDecodeError, ZeroDivisionError) as e:
                print("KEY ERROR: ", e, '\n')
                return

            print(pyfiglet.figlet_format('FILE DECRYPTED SUCCESSFULLY', font='cybermedium'))
            separator_3()

            # display path of the decrypted file
            print('DECRYPTED FILE LOCATION: ' + os.path.abspath(decrypted_file_path))

    except (TypeError, ValueError, UnicodeDecodeError, ZeroDivisionError) as e:
        print(e, '\n', ('-' * 100), '\n', 'INPUT ERROR, PLEASE RETRY SELECTION USING NUMBER KEYS: ')
        return


def decrypt_file(key_list, user_file):
    encrypted_numbers_list = []

    # get file-bytes and append one line after another into a list
    with open(user_file) as f:
        for encrypted_numbers in f:
            encrypted_numbers_list.append(int(encrypted_numbers.rstrip('\n')))
    return decrypt(key_list, encrypted_numbers_list)


def decrypt(key_list, encrypted_numbers_list):
    rotated_encrypted_file_list = []
    semantic_encrypted_file_list = []
    decrypted_file_list = []

    # get amount of numbers in the read out file-bytes
    encrypted_number_lengths = [len(str(x)) for x in encrypted_numbers_list]

    # get the average length of the numbers in the set "encrypted number lengths"
    average_encrypted_number_length = int(sum(encrypted_number_lengths) / len(encrypted_number_lengths))

    # get the negative equivalent value of "average_encrypted_number_length" for use with rotation function
    inverse_average_encrypted_number_length = (average_encrypted_number_length - (average_encrypted_number_length * 2))

    # rotate the "encrypted_numbers_list" backwards according to the "inverse_average_encrypted_number_length"
    rotated_encrypted_file = rotate_list_as_rotor(encrypted_numbers_list, inverse_average_encrypted_number_length)

    # loop though numbers in the "rotated_encrypted_file" and append to another list
    for file_byte_numbers in rotated_encrypted_file:
        rotated_encrypted_file_list.append(file_byte_numbers)

    # grab the last number in the list, which will always be the "obscurer_bits"
    obscurer_bits = rotated_encrypted_file_list.pop()

    # grab the first three digits of the "obscurer_bits", which will be the "time_bit"
    time_bit = int(str(obscurer_bits)[:3])

    # get the "multiplier_bit", which will be the first number after the time bit, before the random numbers that were
    # inserted to make the 'obscurer_bits" number the same as the average length of the numbers in the
    # "rotated_encrypted_file_list"
    multiplier_bit = int(str(obscurer_bits)[3])

    # loop through the "rotated_encrypted_file_list"
    for multiplied_numbers in rotated_encrypted_file_list:

        # perform second layer of decryption schema to get the first layer to decrypt
        pseudo_random_multiplied_numbers = int(multiplied_numbers - (time_bit * multiplier_bit))

        # append each first layer decrypted number "semantic_encrypted_file_list"
        semantic_encrypted_file_list.append(pseudo_random_multiplied_numbers)

    # loop through and enumerate the numbers (in rows) gotten from the "semantic_encrypted_file_list"
    for enumeration_number, character in enumerate(semantic_encrypted_file_list):

        # get the unicode (UTF-8) number that represents each of the character(s) in the message to decrypt
        # (null if dealing with numbers from file-bytes of a file instead of a message)
        file_byte_character_integer = int(character)

        # get the unicode (UTF-8) number that represents each of the character(s) in the key used to encrypt original
        # message or file
        key_enumeration_ordinal = int(ord(''.join(key_list)[enumeration_number % len(''.join(key_list))]))

        # perform first layer of decryption schema to arrive at the original message / file-bytes
        divided_file_byte_integer = int((file_byte_character_integer / key_enumeration_ordinal) / multiplier_bit)

        # append each now fully decrypted number to the "decrypted_file_list"
        decrypted_file_list.append(divided_file_byte_integer)

    return decrypted_file_list


# read out the file or message in file-bytes
def get_bytes_from_files(filename):

    try:

        with open(filename, 'rb') as f:
            for byte in f.read():
                yield byte

    except (TypeError, ValueError, UnicodeDecodeError, ZeroDivisionError) as e:
        print(e, '\n', ('-' * 100), '\n', 'INPUT ERROR, PLEASE RETRY SELECTION USING NUMBER KEYS: ')
        return


# pick a random number between 2-9
def random_number_for_multiplier_bit():
    return random.randint(2, 9)


# create random number, based on the number of numbers requested
def random_number_with_obscurer_digits(number_of_digits):
    number_range_start = 10 ** (number_of_digits - 1)
    number_range_end = (10 ** number_of_digits) - 1

    return random.randint(number_range_start, number_range_end)


# create random string of all character types, based on the number of characters requested
def random_string_with_one_time_pad_characters(number_of_characters):
    one_time_pad_characters = string.ascii_letters + string.digits + string.punctuation

    return ''.join(random.choice(one_time_pad_characters) for _ in range(number_of_characters))


# rotation function, to rotate a list a given number of places depending on number of rotations requested
def rotate_list_as_rotor(character_set, rotations):
    return character_set[rotations:] + character_set[:rotations]


# formatting lines, just to make it look clean
def separator_1():
    print('-' * 100)


# formatting lines, just to make it look clean
def separator_3():
    for item in '\n', '-' * 100, '\n':
        print(item)


# tk gui module function to select files
def tk_gui_file_selection_window():
    root = Tk()
    root.withdraw()
    root.update()
    selected_file = filedialog.askopenfilename()
    root.destroy()

    return selected_file


if __name__ == '__main__':
    main()
