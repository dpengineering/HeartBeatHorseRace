import enum
from p2p.dpea_p2p import Server

print('starting server')
class PacketType(enum.Enum):
    NULL = 0
    COMMAND1 = 1
    COMMAND2 = 2

#         |Bind IP       |Port |Packet enum
s = Server("172.17.21.3", 5001, PacketType)
print('server created')
s.open_server()
print('server opened, now waiting for connection!')
s.wait_for_connection()

assert s.recv_packet() == (PacketType.COMMAND1, b"Hello!")
s.send_packet(PacketType.COMMAND2, b"Hello back!")

s.close_connection()
s.close_server()