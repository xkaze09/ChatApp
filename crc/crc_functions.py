'''
Authors: Kristina Celis & Christian Salinas

Description: crc_functions.py contains functions for 
CRC or Cyclic Redundancy Check which is a method of detecting accidental
changes/errors in the communication channel.
'''

import random

def string_to_binary(input_string):
    data = (''.join(format(ord(x), 'b') for x in input_string))
    return data
    

def mod_2_division(dividend, divisor):
    ''' Perform modulo 2 division and return the remainder
    Args:
    - dividend: message with appended 0s
    - divisor: binary string of generator
    Returns:
    - Remainder as a binary string'''

    # Convert the binary string to a list for XOR
    dividend = list(dividend)
    divisor = list(divisor)
    len_divisor = len(divisor)

    for i in range(len(dividend) - len_divisor + 1):
        # Only perform XOR if the leading but is 1
        if dividend[i] == '1':
            for j in range(len_divisor):
                # Perform XOR and store the result
                dividend[i+j] = str(int(dividend[i+j]) ^ int(divisor[j]))
    
    # Return the remainder, used as the CRC checksum
    return ''.join(dividend[-(len_divisor -1):])  # last n-1 bits of the dividend

def crc(data, generator): 
    '''
    Compute the CRC Checksum for the message using a generator polynomial G(X)
    '''
    padded_data = data + '0' * (len(generator)-1) # Append n 0s to M(X)
    remainder = mod_2_division(padded_data, generator)
    return remainder

def validate_crc(received_msg, generator):
    '''
    Validate CRC of a received message
    '''

    # Split the message and checksum
    data, received_crc = received_msg[:-len(generator)+1], received_msg[-len(generator)+1:]
    # Recompute CRC for the received data
    computed_crc = crc(data, generator)
    return received_crc == computed_crc

def introduce_error(msg, error_chance=5):
    '''
    Introduce a 5% chance of adding 1 bit to T(X)
    '''

    if random.randint(1,100) <= error_chance:
        bit_to_flip = random.randint(0, len(msg)-1)
        flipped_bit = '1' if msg[bit_to_flip] == '0' else '0'
        msg = msg[:bit_to_flip] + flipped_bit + msg[bit_to_flip + 1:]
        print(f"Error introduced at bit {bit_to_flip}.")
    return msg



