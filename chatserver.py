import socket
import threading

global_lock = threading.Lock()
clients_list  = []


clients_threads_list = []

def broadcast(client_conn, msg):
    with global_lock:
        print("There are ", len(clients_list))
        for client in clients_list:
            if client != client_conn:
                print("Sending msgs to clients")
                client.send(msg.encode())

def remove_client(client_conn):
    with global_lock:
        client_conn.close()
        clients_list.remove(client_conn)
    
def client_handling(client_conn):
    global clients_list, clients_threads_list
    client_conn.send("Welcome To the CHAT ROOM!".encode())
    client_name = client_conn.recv(24).decode()
    with global_lock:
        clients_list.append(client_conn)
    lock = threading.Lock()
    with lock:
        print(client_name+ " has entered the chat")
        broadcast(client_conn, client_name+ " has entered the chat")
    while True:
        msg = client_conn.recv(4096).decode()
        with lock:
            if msg and msg != "bye":
                print(client_name + " : "+ msg)
                broadcast(client_conn, client_name + " : "+ msg)
            else:
                print(client_name + " has left the chat")
                broadcast(client_conn, client_name + " has left the chat")
                remove_client(client_conn)
                break



def server(hostname, port):
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Socket Created!")
        server_socket.bind((hostname, port))
        print("Socket Binded to", (hostname, port))
        server_socket.listen(5)
        print("Listening for active connections!!")
        
    except:
        print("Error occured in creating Socket")


    try:
        for _ in range(5):
            conn, addr = server_socket.accept()
            # clients_list.append(conn)
            clients_threads_list.append(threading.Thread(target=client_handling, args=(conn,)))
            clients_threads_list[-1].start()

        for thread in clients_threads_list:
            thread.join()
        print("Server Exiting Successfully")
    except KeyboardInterrupt:
        broadcast(None, "Server Exited!")
        print("Server Exited!!")

    except:
        print("Error occured in accepting Connections")

def recieveMsgs(client_socket):
    try:
        while True:
            msg = client_socket.recv(4096).decode()
            if msg:
                print(msg)
            else:
                client_socket.close()
                break
    except:
        pass


def client(hostname, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((hostname, port))
    print(client_socket.recv(4096).decode())
    name = input("Enter Your Name: ")
    client_socket.send(name.encode())
    t = threading.Thread(target=recieveMsgs, args=(client_socket,))
    t.start()
    while True:
        msg = input()
        client_socket.send(msg.encode())
        if (msg == "bye"):
            break



def main():
    print("Server or Client")
    x = input("Enter Option: ")
    hostname = input("Enter Ip address: ")
    port = int(input("Enter Port number: "))
    if (x == 'Server'):
        server(hostname, port)
    else:
        client(hostname, port)

if __name__ == "__main__":
    main()