'''
Authors: Kristina Celis & Christian Salinas

Description: crc_functions.py contains functions for 
CRC or Cyclic Redundancy Check which is a method of detecting accidental
changes/errors in the communication channel.
'''

import random

def string_to_binary(input_string):
    ''' Convert a string to binary representation (7-bit encoding) '''
    return ''.join(format(ord(char), '07b') for char in input_string)

def mod_2_division(dividend, divisor):
    ''' Perform modulo 2 division and return the remainder '''
    print(f"Initial Dividend: {dividend}")
    print(f"Divisor: {divisor}")
    dividend = list(dividend)
    divisor = list(divisor)
    len_divisor = len(divisor)
    for i in range(len(dividend) - len_divisor + 1):
        if dividend[i] == '1':
            for j in range(len_divisor):
                dividend[i + j] = str(int(dividend[i + j]) ^ int(divisor[j]))
            print(f"Step {i}: Dividend after XOR: {''.join(dividend)}")
    remainder = ''.join(dividend[-(len_divisor - 1):])
    print(f"Remainder: {remainder}")
    return remainder

def crc(data, generator):
    ''' Compute the CRC Checksum '''
    padded_data = data + '0' * (len(generator) - 1)
    remainder = mod_2_division(padded_data, generator)
    return remainder

def validate_crc(received_msg, generator):
    ''' Validate CRC of a received message '''
    try:
        data, received_crc = received_msg[:-len(generator) + 1], received_msg[-len(generator) + 1:]
        computed_crc = crc(data, generator)
        return received_crc == computed_crc
    except Exception as e:
        print(f"CRC validation failed: {e}")
        return False


def introduce_error(msg, error_chance=5):
    ''' Introduce a 5% chance of adding 1 bit to T(X) '''
    if random.randint(1, 100) <= error_chance:
        bit_to_flip = random.randint(0, len(msg) - 1)
        flipped_bit = '1' if msg[bit_to_flip] == '0' else '0'
        msg = msg[:bit_to_flip] + flipped_bit + msg[bit_to_flip + 1:]
        print(f"Error introduced at bit {bit_to_flip}.")
    return msg