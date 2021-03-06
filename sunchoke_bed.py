# sunchoke_bed.py
# @author: Isaac Caswell
# @date: 3/3/2017
#
# Interface for deniable encryption system.
#
# Usage:
#   $ python sunchoke_bed.py encrypt --size_constraint 1024
#
# Please read README.txt for further description and usage notes.

import argparse

from core import encrypt_all_messages, decrypt_message
from header_prefix import HEADER_PREFIX

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', type=str, help="either `encrypt` or `decrypt`", choices=['encrypt', 'decrypt'])
    parser.add_argument('--password', type=str, help="password for decryption.  Only use when in mode `decrypt`.", default=None)
    parser.add_argument('--size_constraint', type=int, help="Total bytes in output.  Only use when in mode `encrypt`.", default=None)
    parser.add_argument('--messages_file', type=str, help="file containing keys and messages to be encrypted. "
        "Use only with mode `encrypt`.", default="input.txt")
    parser.add_argument('--encrypted_file', type=str, help="file into which to dump the encrypted output "
        "if mode is `encrypt`, and otherwise the file with the message.", default="output.txt")

    args = parser.parse_args()
    if args.mode == 'decrypt' and args.password is None:
        raise ValueError("need a password to decrypt")
    if args.mode == 'decrypt' and args.size_constraint is not None:
        raise ValueError("Don't need a size constraint to decrypt")
    if args.password is not None and args.mode == 'encrypt':
        raise ValueError("The pass-sword for encryption should be in your input file. Are you confused?")
    return args

args = parse_args()


if args.mode == 'encrypt':
    #-------------------------------------------------------------------------------
    # Read in and encrypt data
    with open(args.messages_file, 'r') as f:
        data = f.read()
        messages = eval(data)

    ciphertext = encrypt_all_messages(messages, args.size_constraint)

    #-------------------------------------------------------------------------------
    # check to make passwords are long enough
    for key in messages:
        if key and len(key) < 8: # note that the empty key corresponds to the chaff message
            print("WARNING: password '%s' too short!"%key)

    #-------------------------------------------------------------------------------
    # check to make sure that the header size is appropriate

    prob_header_randomly_occurs = lambda n, k: 1 - (1- ((9.0/256)*(256**-k)))**(n/16 - k)
    p = prob_header_randomly_occurs(len(ciphertext), len(HEADER_PREFIX))
    if p > 1e-3:
        print("WARNING: there is a probability of %s that there will be some corruption of your data."%p + \
            "  Please try decrypting your message to make sure it works.")

    #-------------------------------------------------------------------------------
    # write data
    with open(args.encrypted_file, 'w') as f:
        f.write(ciphertext)

elif args.mode == 'decrypt':
    with open(args.encrypted_file, 'rb') as f:
        ciphertext = f.read()
    plaintext = decrypt_message(args.password, ciphertext)
    print(plaintext)

else:
    raise ValueError("inexplicable error")
