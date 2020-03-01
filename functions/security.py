#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
version: python 3+
securiy.py defines the hash function and compare function
Dani van Enk, 11823526
"""

# used libraries
import os
import hashlib
import binascii


def hash_psswd(password):
    """
    hashes the given password using the sha512 algorithm

    parameters:
        password - is the password to be hashed

    returns the hash string
    """

    # generate a random salt and use that to hash the password
    psswd_salt = hashlib.sha512(os.urandom(64)).hexdigest().encode("utf-8")
    psswd_hash = hashlib.pbkdf2_hmac('sha512', bytearray(password, 'utf-8'),
                                     bytearray(psswd_salt), 500000)

    # convert the salt and hash to hex
    psswd_salt_hex = psswd_salt.decode("utf-8")
    psswd_hash_hex = binascii.hexlify(psswd_hash).decode("utf-8")

    # begin with an empty hash string
    hash_string = ""

    # combine the salt and the hash into 1 string
    for i in range(len(psswd_salt_hex)):
        hash_string += psswd_salt_hex[i]
        hash_string += psswd_hash_hex[i]

    return hash_string


def compare_hash(stored, psswd):
    """
    compare a stored hash to a given password

    parameter:
        stored	- is the hash you want to compare to
        psswd	- is the password which results to the stored hash

    returns the comparison between stored and the hash resulting from psswd
    """

    # begin with an empty string for the salt
    hash_salt = ""

    # extract the salt from the stored hash string
    for i in range(len(stored)):
        if i % 2 == 0:
            hash_salt += stored[i]

    # hash the given password with the extracted salt and convert it to hex
    hash_passwd = hashlib.pbkdf2_hmac('sha512', bytearray(psswd, 'utf-8'),
                                      bytearray(hash_salt.encode('utf-8')),
                                      500000)
    hash_passwd_hex = binascii.hexlify(hash_passwd).decode("utf-8")

    # begin with an empty hash string
    hash_string = ""

    # combine the hash and salt
    for i in range(len(hash_passwd_hex)):
        hash_string += hash_salt[i]
        hash_string += hash_passwd_hex[i]

    return hash_string == stored
