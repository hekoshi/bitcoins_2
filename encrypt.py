#!/usr/bin/env python3
import random, io

def encodes(key, data):
    """ Encode data from provided string -> string """
    assert(isinstance(data, str))
    in_data = io.StringIO(data)
    out_data = io.StringIO()
    encode(key, in_data, out_data)
    return out_data.getvalue()

def decodes(key, data):
    """ Decode data from provided string -> string """
    assert(isinstance(data, str))
    in_data = io.StringIO(data)
    out_data = io.StringIO()
    decode(key, in_data, out_data)
    return out_data.getvalue()

def encode(key, infile, outfile):
    """ Encode data from a file object to another -> None """
    random.seed(key)
    while True:
        data = infile.read(1)
        if not len(data): return
        bit = ord(data)
        offset = random.randint(0,255)
        if bit+offset > 256: offset -= 256
        outfile.write(chr(bit+offset))
    random.seed()

def decode(key, infile, outfile):
    """ Decode data from a file object to another -> None """
    random.seed(key)
    while True:
        data = infile.read(1)
        if not len(data): return
        bit = ord(data)
        offset = random.randint(0,255)
        if bit-offset < 0: offset -= 256
        outfile.write(chr(bit-offset))
    random.seed()
