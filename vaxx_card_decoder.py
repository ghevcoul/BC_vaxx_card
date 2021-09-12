
import sys
import base64
import zlib

import cv2


class VaxxCardDecoder:

    def __init__(self, qr_image_file: str):

        self.header: str
        self.payload: str
        self.signature: bytes

        self.get_data_from_image(qr_image_file)

    def get_qr_data(self, qr_image_filename: str) -> str:
        """Given a file path to an image containing a QR code, get the data it encodes"""
        image = cv2.imread(qr_image_filename)

        # initialize the cv2 QRCode detector
        detector = cv2.QRCodeDetector()
        data, vertices_array, binary_qrcode = detector.detectAndDecode(image)

        if vertices_array is None:
            raise Exception("Couldn't parse file as a valid QR code!")
        
        if not data.startswith('shc:/'):
            raise Exception("File is a QR code, but not a valid SMART Health Card")

        return data

    def convert_data_to_ascii(self, data_string: str) -> str:
        """
        Convert data from numbers into ASCII characters
        Read pairs of numbers, add 45 and convert to ASCII
        """
        char_array = []
        for i in range(5, len(data_string[5:]), 2):
            char_pair = int(data_string[i] + data_string[i+1]) + 45
            char_array.append(chr(char_pair))

        return ''.join(char_array)

    def base64_decode(self, base64_string: str):

        # The string should contain two periods, which are not valid Base64 characters
        # These are delimiters for the three sections of the data
        pieces = base64_string.split('.')

        decoded = []
        for piece in pieces:
            # Base64 decoding requires strings that are a multiple of 4, if ours isn't pad it
            padding = 4 - (len(piece) % 4)
            padded_piece = piece.ljust(len(piece)+padding, '=')
            decoded.append(base64.urlsafe_b64decode(padded_piece))

        return decoded

    @staticmethod
    def payload_decode(payload: bytes) -> str:
        """Inflate the DEFLATED payload"""
        return zlib.decompress(payload, wbits=-8).decode('utf-8')

    def get_data_from_image(self, qr_image_filename: str):

        qr_data = self.get_qr_data(qr_image_filename)
        ascii_data = self.convert_data_to_ascii(qr_data)
        header, payload, signature = self.base64_decode(ascii_data)

        self.header = header.decode('utf-8')
        self.payload = self.payload_decode(payload)
        self.signature = signature


if __name__ == '__main__':
    filename = sys.argv[1]

    decoder = VaxxCardDecoder(filename)
    print(decoder.payload)
