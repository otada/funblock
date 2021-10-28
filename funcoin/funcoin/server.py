import asyncio
from asyncio.exceptions import IncompleteReadError
from asyncio.streams import StreamReader, StreamWriter

import structlog
from marshmallow.exceptions import MarshmallowError

from funcoin.messages import BaseSchema
from funcoin.utils import get_external_ip

logger = structlog.getLogger() #---(7)
#---(7): Notice the import and usage of structlog—we’re
    # using it to replace the print() statements. It gives
    # highly readable output to the console when we run
    # our entire node. For example, it tells you which file
    # the log came from.

class Server:
    def __init__(self, blockchain, connection_pool, p2p_protocol):
        self.blockchain = blockchain #---(1)
        #---(1): This is how we “bootstrap” our modules to the
            # server: the server class (and anything attached to it)
            # will always have access to our blockchain via self.
            # blockchain.
        self.connection_pool = connection_pool
        self.p2p_protocol = p2p_protocol
        self.external_ip = None
        self.external_port = None
        
        if not (blockchain and connection_pool and p2p_protocol):
            logger.error("'blockchain', 'connection_pool', and 'gossip_protocol' must all be instatiated")
            raise Exception("Could not start")
            
    async def get_external_ip(self):
        # Finds our "external IP" so that we can advertize it to our peers
        self.external_ip = await get_external_ip() #---(2)
        #---(2): get_external_ip() yet, it’s responsible for finding our
            # external IP address.
        
    async def handle_connection(self, reader: StreamReader, writer: StreamWriter):
        # This function is called when we receive a new connection 
        # The `writer` object represents the connecting peer
        while True:
            try:
                # We handle and/or reply to the incoming data
                # Wait forever on new data to arrive
                data = await reader.readuntil(b"\n") #---(3)
                #---(3): Here, we wait forever until a message is sent to
                    # us terminated by a new line (\n) character. This is
                    # the first of some potential vulnerabilities that you
                    # should be on the lookout for, since anyone could
                    # just spam our server with a never-ending message.
                
                decoded_data = data.decode("utf8").strip() #---(4)
                #---(4): We try to decode the message by assuming it was
                    # sent to us as a UTF-8-formatted string.
                try:
                    message = BaseSchema().loads(decoded_data) #---(5)
                    #---(5): Perhaps the biggest surprise we’ll learn about
                        # shortly is the usage of marshmallow (the library we
                        # installed earlier) to parse and validate an incoming
                        # message from a peer.  
                except MarshmallowError:
                    logger.info("Received unreadable message", peer=writer)
                    break
                # Extract the address from the message, add it to the writer object
                writer.address = message["meta"]["address"]
                
                # Let's add the peer to our connection pool
                self.connection_pool.add_peer(writer)
                
                #...and handle the message
                await self.p2p_protocol.handle_message(message, writer) #---(6)
                #---(6): Once the message has been parsed successfully,
                    # further code can assume that all relevant fields exist,
                    # and we can use our p2p protocol to figure out what
                    # to do.
                
                await writer.drain()
                if writer.is_closing():
                    break
                             
            except (asyncio.exceptions.IncompleteReadError, ConnectionError):
                # An error happened, break out of the wait loop
                break
        # The connection has closed. Let's clean up...
        writer.close()
        await writer.wait_closed()
        self.connection_pool.remove_peer(writer) #---(7)
        #---(7): see (7) above
                
    async def listen(self, hostname="0.0.0.0", port=8888):
        # This is the listen method which spawns our server
        
        server = await asyncio.start_server(self.handle_connection, hostname, port)        
        logger.info(f"Server listening on {hostname}:{port}")
        
        self.external_ip = await self.get_external_ip()
        self.external_port = 8888
              
        async with server:
            await server.serve_forever()
        
    