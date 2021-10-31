import asyncio
import structlog
import aiohtt

class P2PError(Exception):
    pass
class P2PProtocol:
    def __init__(self, server):
        ...
        
    @staticmethod
    async def send_message(writer, message):
        # Sends a message to a particular peer (the writer object)
        ...
    
    async def handle_message(self, message, writer):
        # Handles an incoming messsage passed by the server
        # Hands this message off to a more specific method: handle_<method name>()
        ...
    
    async def handle_ping(self, message, writer):
        # Handles in incoming "ping" message
        ...
        
    async def handle_block(self, message, writer):    
        # Handles in incoming "block" message
        ...
        
    async def handle_transactions(self, message, writer):    
        # Handles in incoming "transactions" message
        ...
        
    async def handle_peers(self, message, writer):    
        # Handles in incoming "peers" message
        ...