import argparse
import sys
import socket
import select
import threading


class ProxyServer:
    def __init__(self, target_host, target_port, server_addr, server_port):
        self.__target_host = target_host
        self.__target_port = target_port
        self.__server_addr = server_addr
        self.__server_port = server_port
        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__socket_pairs = []
        self.__close = False

    def run(self):
        self.__server_socket.bind((self.__server_addr, self.__server_port))
        self.__server_socket.listen(5)
        self.__reader_thread = threading.Thread(target=self.__reader_loop)
        self.__reader_thread.start()
        try:
            while True:
                client, addr = self.__server_socket.accept()
                print("[*] Accepted connection from {}".format(addr))
                target_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    target_sock.connect((self.__target_host, self.__target_port))
                    self.__socket_pairs.append((client, target_sock))
                except Exception as e:
                    print("[!!] Could not connect to target machine")
                    print(e)
                    client.shutdown(socket.SHUT_RDWR)
                    client.close()
        except KeyboardInterrupt:
            print("[!!] Caught keybboard interrupt. Closing down")
        except Exception as e:
            print("[!!] Caught exception")
            print(e)
        finally:
            self.__close = True
            self.__reader_thread.join()
            for (x,y) in self.__socket_pairs:
                x.shutdown(socket.SHUT_RDWR)
                x.close()
                y.shutdown(socket.SHUT_RDWR)
                y.close()
            self.__server_socket.shutdown(socket.SHUT_RDWR)
            self.__server_socket.close()

    def __reader_loop(self):
        while not self.__close:
            flatlist = [item for tempList in self.__socket_pairs for item in tempList]
            (rs, ws, xs) = select.select(flatlist, [], [], 0.1)
            for s in rs:
                matching_sock = None
                pair = None
                for (x, y) in self.__socket_pairs:
                    if x == s:
                        matching_sock = y
                        pair = (x,y)
                        print("[<==] Received message")
                        break
                    if y == s:
                        matching_sock = x
                        print("[==>] Received message")
                        break
                        pair = (x,y)
                buffer = s.recv(4096)
                if len(buffer) == 0 or buffer == b'\xff\xf4\xff\xfd\x06':
                    self.__socket_pairs.remove(pair)
                    s.shutdown(socket.SHUT_RDWR)
                    s.close()
                    matching_sock.shutdown(socket.SHUT_RDWR)
                    matching_sock.close()
                    continue
                matching_sock.send(buffer)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--client', default='127.0.0.1', dest='client', type=str, help='Address to bind to')
    parser.add_argument('-o', '--client-port', default=9001, dest='clientport', type=int, help='Port to bind to')
    parser.add_argument('-t', '--target', dest='target', required=True, type=str, help='Target address')
    parser.add_argument('-p', '--port', dest='targetport', required=True, type=int, help='Target port')
    parser.add_argument('-r', '--receive-first', type=bool, default=False, help='Receive first')
    return parser.parse_args(sys.argv[1:])

def main():
    args = parse_args()
    server = ProxyServer(args.target, args.targetport, args.client, args.clientport)
    server.run()


if __name__ == "__main__":
    main()