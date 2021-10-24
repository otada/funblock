import asyncio

class ConnectionPool:
    def __init__(self):
        self.connection_pool = set()
        
    def send_welcome_message(self, writer):
        """
        Sends a welcome message to a newly connected client
        """
        pass
    
    def broadcast(self, writer, message):
        """
        Broadcasts a general message to the entire pool
        """
        pass
    
    def broadcast_user_join(self, writer):
        """
        Calls the broadcast method with a "user joining" message
        """
        pass
    
    def broadcast_user_quit(self, writer):
        pass