import socket, os, json
from executor import execute_command

SOCKET_PATH = os.getenv("IPC_SOCKET_PATH", "/tmp/agent_one.sock")

def ipc_server():
    if os.path.exists(SOCKET_PATH):
        os.remove(SOCKET_PATH)
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(SOCKET_PATH)
    server.listen(1)
    while True:
        conn, _ = server.accept()
        data = conn.recv(4096)
        if not data:
            break
        directive = json.loads(data.decode())
        result = execute_command(directive["command"], directive["payload"])
        conn.sendall(json.dumps(result).encode())
    conn.close()

def ipc_client(command, payload):
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect(SOCKET_PATH)
    client.sendall(json.dumps({"command": command, "payload": payload}).encode())
    result = client.recv(4096)
    client.close()
    return json.loads(result.decode())
