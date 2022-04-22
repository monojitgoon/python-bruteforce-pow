import hashlib
import itertools
import socket
import ssl
import string
import constants


def get_ck_sum_in_hex(auth_param, second_param):
    return hashlib.sha1((auth_param + second_param).encode("utf-8")).hexdigest()


class PythonClient(object):
    def __init__(self, host, port, cert, key):
        self.context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        self.context.load_cert_chain(certfile=cert, keyfile=key)
        self.host = host
        self.port = port

    def connect(self):
        while True:
            conn = None
            try:
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                conn = self.context.wrap_socket(client, server_side=False)
                conn.connect((self.host, self.port))

                auth_data = ""
                while True:
                    args = conn.recv(constants.bufsize).decode("utf-8").strip().split(' ')
                    if args[0] == constants.HELO:
                        conn.write((constants.TOAKUEI + '\n').encode("utf-8"))
                    elif args[0] == constants.ERROR:
                        print('ERROR: ' + ' '.join(args[1:]))
                        break
                    elif args[0] == constants.POW:
                        auth_data, difficulty = args[1], int(args[2])
                        while True:
                            suffix = self.get_suffix(auth_data, difficulty)
                            if suffix:
                                conn.write((suffix + '\n').encode("utf-8"))
                                break
                    elif args[0] == constants.END:
                        conn.write('OK\n'.encode("utf-8"))
                        break
                    elif args[0] == constants.NAME:
                        conn.write(
                            (get_ck_sum_in_hex(auth_data, args[1]) + ' ' + constants.USER_NAME + '\n').encode("utf-8"))
                    elif args[0] == constants.MAILNUM:
                        conn.write((get_ck_sum_in_hex(auth_data, args[1]) + ' ' + constants.USER_MAILNUM + '\n').encode(
                            "utf-8"))
                    elif args[0] == constants.MAIL1:
                        conn.write(
                            (get_ck_sum_in_hex(auth_data, args[1]) + ' ' + constants.USER_MAIL1 + '\n').encode("utf-8"))
                    elif args[0] == constants.SKYPE:
                        conn.write(
                            (get_ck_sum_in_hex(auth_data, args[1]) + ' ' + constants.USER_SKYPE + '\n').encode("utf-8"))
                    elif args[0] == constants.BIRTHDATE:
                        conn.write(
                            (get_ck_sum_in_hex(auth_data, args[1]) + ' ' + constants.USER_BIRTHDATE + '\n').encode(
                                "utf-8"))
                    elif args[0] == constants.COUNTRY:
                        conn.write((get_ck_sum_in_hex(auth_data, args[1]) + ' ' + constants.USER_COUNTRY + '\n').encode(
                            "utf-8"))
                    elif args[0] == constants.ADDRNUM:
                        conn.write((get_ck_sum_in_hex(auth_data, args[1]) + ' ' + constants.USER_ADDRNUM + '\n').encode(
                            "utf-8"))
                    elif args[0] == constants.ADDRLINE1:
                        conn.write(
                            (get_ck_sum_in_hex(auth_data, args[1]) + ' ' + constants.USER_ADDRLINE1 + '\n').encode(
                                "utf-8"))
                    elif args[0] == constants.ADDRLINE2:
                        conn.write(
                            (get_ck_sum_in_hex(auth_data, args[1]) + ' ' + constants.USER_ADDRLINE2 + '\n').encode(
                                "utf-8"))
                conn.close()
                break
            except Exception as ex:
                print('Execution error : {0}'.format(ex))
                conn.close()
                break

    @staticmethod
    def get_suffix(auth_param, difficulty_param):
        # to generate random string, the source set of character can be chosen as more large set of characters
        chars = string.ascii_lowercase
        unwanted_chars = "\n\r\t "
        usable_chars = [s for s in chars if s not in unwanted_chars]

        for suffix_length in range(constants.SUFFIX_MIN_LENGTH, constants.SUFFIX_MAX_LENGTH):
            for predicted_suffix in itertools.product(usable_chars,
                                                      repeat=suffix_length):
                predicted_suffix = ''.join(predicted_suffix)
                ck_sum_in_hex = get_ck_sum_in_hex(auth_param, predicted_suffix)
                if ck_sum_in_hex.startswith('0' * difficulty_param):
                    return predicted_suffix


if __name__ == "__main__":
    PythonClient(constants.SERVER_ADDRESS, constants.PORT, constants.CERTIFICATE_PATH, constants.KEY_PATH).connect()
