""" All message type about P2P network. """

# --------------------------------------------------
# Message type: client and server

# client -> server
REGISTER = 'REGISTER'

# client -> server
EXIT_NETWORK = 'EXIT_NETWORK'

# server -> client
REGISTER_ERROR = 'REGISTER_ERROR'

# server -> client
REGISTER_SUCCESS = 'REGISTER_SUCCESS'

# (server -> client) or (client -> server)
LISTPEER = 'LISTPEER'

# -------------------------------------------------
# Message type: client and client

# (client A -> client B) or (client B -> client A)
DISCONNECT = 'DISCONNECT'

# client A -> client B
REQUEST = 'REQUEST'

# client B -> client A
CHAT_ACCEPT = 'CHAT_ACCEPT'

# client B -> client A
CHAT_REFUSE = 'CHAT_REFUSE'

# (client A -> client B) or (client B -> client A)
CHAT_MESSAGE = 'CHAT_MESSAGE'

# cilent A <-> client B
FILE_TRANSFER = 'FILE_TRANSFER'

# client A -> client B
FILE_TRANSFER_REQUEST = 'FILE_TRANSFER_REQUEST'

# client B -> client A
FILE_TRANSFER_ACCEPT = 'FILE_TRANSFER_ACCEPT'

# client B -> client A
FILE_TRANSFER_REFUSE = 'FILE_TRANSFER_REFUSE'
