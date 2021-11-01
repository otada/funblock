import asyncio

from funcoin.blockchain import Blockchain
from funcoin.connections import ConnectionPool
from funcoin.peers import P2PProtocol
from funcoin.server import Server

# Instantiate the blockchain and our pool for "peers"
blockchain = Blockchain()
connection_pool = ConnectionPool()

# Instantiate the server and "bolt of" our modules
server = Server(blockchain, connection_pool, P2PProtocol)

async def main():
    # Start the server
    await server.listen()
    
asyncio.run(main())