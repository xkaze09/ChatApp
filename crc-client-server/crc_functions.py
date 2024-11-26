'''
Authors: Kristina Celis & Christian Salinas

Description: crc_functions.py contains functions for 
CRC or Cyclic Redundancy Check which is a method of detecting accidental
changes/errors in the communication channel.
'''

import random
import logging

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG)

def string_to_binary(input_string):
    ''' 
    Convert a string to binary representation (7-bit encoding)
    Parameters: input_string (str): string to convert
    Return: str: binary rep of the input string
    '''
    return ''.join(format(ord(char), '07b') for char in input_string)


def mod_2_division(dividend, divisor):
    ''' 
    Perform modulo 2 division and return the remainder 
    Parameters: dividend (str): msg with appended 0s
                divisor (str): binary string divisor/generator
    Returns: str: remainder after mod 2 division
    '''

    # Input validation for binary strings
    if not all (bit in '01' for bit in dividend) or not all(bit in '01' for bit in divisor):
        raise ValueError("Both dividend and divisor must be binary strings")
    if len(divisor) == 0:
        raise ValueError("Divisor cannot be empty")
    
    logging.debug(f"Initial Dividend: {dividend}")
    logging.debug(f"Divisor: {divisor}")

    # Convert dividend and divisor to lists for XOR
    dividend = list(dividend)
    divisor = list(divisor)

    # Lenght of divisor
    len_divisor = len(divisor)

    # Perform division
    for i in range(len(dividend) - len_divisor + 1):
        # If leading bit is '1', perform XOR with divisor
        if dividend[i] == '1':
            for j in range(len_divisor):
                # XOR operation on each bit
                dividend[i + j] = str(int(dividend[i + j]) ^ int(divisor[j]))
            logging.debug(f"Step {i}: Dividend after XOR: {''.join(dividend)}")

    # Extract remainder (last len_divisor - 1 bits)
    remainder = ''.join(dividend[-(len_divisor - 1):])
    logging.debug(f"Final Remainder: {remainder}")
    return remainder

def crc(data, generator):
    ''' 
    Compute the CRC Checksum 
    Parameters: data (str): binary data string
                generator (str): binary str generator (divisor) 
    Return: str: CRC checksum
    '''
    padded_data = data + '0' * (len(generator) - 1)     # Append n '0s'
    crc = mod_2_division(padded_data, generator)
    return crc

def validate_crc(received_msg, generator):
    ''' 
    Validate CRC of a received message 
    Parameters: received_msg (str): msg containing data and crc
                generator (str): binary str generator
    Return: bool: True if CRC valid, False otherwise
    '''
    try:
        # Split msg into data and crc
        data, received_crc = received_msg[:-len(generator) + 1], received_msg[-len(generator) + 1:]
        
        # Compute CRC using provided generator
        computed_crc = crc(data, generator)

        # Check if received crc matches computed crc
        return received_crc == computed_crc
    
    except Exception as e:
        # Log errors (like invalid inputs)
        print(f"CRC validation failed: {e}")
        return False


def introduce_error(msg, error_chance=5):
    ''' 
    Introduce a 5% chance of adding 1 bit to T(X)
    Parameters: msg (str): original msg
                error_chance (int): probability of adding a bit
    Return: msg (str): modified message with one bit added when error occurs
    
    '''
    # Check if an error should be introduced
    if random.randint(1, 100) <= error_chance:
        # Choose a random position to add a bit
        position = random.randint(0, len(msg))
        new_bit = random.choice(['0', '1']) 
        # Add the bit at the chosen position
        msg = msg[:position] + new_bit + msg[position:]
        print(f"Error introduced: Bit '{new_bit}' added at position {position}.")
    return msg