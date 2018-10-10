# by David Reyes
import socket

TCP_IP = '127.0.0.1'
TCP_PORT = 5005
BUFFER_SIZE = 5000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))

while True:
    message = input("Enter name of city to receive weather info: ")
    s.sendall(message.encode('utf-8'))
    weather_info = s.recv(BUFFER_SIZE)
    print(weather_info.decode('utf-8'))

    again = input("\nWould you like the weather info of another city? \n(Y/n): ")
    if again != "Y":
        break

s.close()
