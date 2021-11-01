from ctypes import addressof
import structlog
from more_itertools import take

logger = 

class ConnectionPool:
    def __init__(self):
        #---(1): Here we use a dict, mapping address to writer (representing the peer connection).      
        self.connection_pool = dict() #---(1)
    
    def broadcast(self, message):
        for user in self.connection_pool:
            user.write(f"{message}".encode())
            
    @staticmethod
    def get_address_string(writer):
        ip = writer.address["ip"]
        port = writer.address["port"]
        #---(2):The address string in the mapping is simply the ip:port combination of the peer
        return f"{ip}:{port}" ##---(2)
    
    def add_peer(self, writer):
        address = self.get_address_string(writer)
        self.connection_pool[address] = writer
        logger.info("Added new peer to pool", address=address)
        
    def remove_peer(self, writer):
        address = self.get_address_string(writer)
        self.connection_pool.pop(address)
        logger.info("Removed peer from pool", address=address)
        
    def get_alive_peers(self, count):
        # TODO: (Reader): Sort these by most active, but let's just get the first *count* of them for now
        
        #---(3): We use the take() function to return count number of peers from our pool.
        return take(count, self.connection_pool.items()) #---(3)