"""
utilities.zipper

Author: Michael Redmond

"""

from zlib import compress as compress_, decompress as decompress_


def decompress(compressed_data):
    return decompress_(compressed_data, -15)


def compress(uncompressed_data, compression_level=6):
    return compress_(uncompressed_data, compression_level)[2:-4]


if __name__ == '__main__':
    data = 'aaasdfsddfdddfdsaasasssssdfdfddddddsadfasdfdfasdssssdfffddsassddfdfd'
    data_compressed = compress(data.encode())
    print(data_compressed)
    data_decompressed = decompress(data_compressed)
    print(data_decompressed)