import asyncio
import structlog
import aiohttp

from funcoin.messages import (
    create_peers_message,
    create_block_message,
    create_transaction_message,
    create_ping_message,
)

from funcoin.transactions import validate_transaction

logger = structlog.getLogger(__name__)


class P2PError(Exception):
    pass


class P2PProtocol:
    def __init__(self, server):
        self.server = server
        self.blockchain = server.blockchain
        self.connection_pool = server.connection_pool

    @staticmethod
    async def send_message(writer, message):
        # Sends a message to a particular peer (the writer object)
        writer.write(message.encode() + b"\n")

    async def handle_message(self, message, writer):
        # Handles an incoming messsage passed by the server
        # Hands this message off to a more specific method: handle_<method name>()
        message_handlers = {
            "block": self.handle_block,
            "ping": self.handle_ping,
            "peers": self.handle_peers,
            "transaction": self.handle_transaction,
        }

        handler = message_handlers.get(message["name"])
        if not handler:
            raise P2PError("Missing handler for message")

        await handler(message, writer)

    async def handle_ping(self, message, writer):
        # Handles in incoming "ping" message
        block_height = message["payload"]["block_height"]

        # If they're a miner, let's mark them as such
        writer.is_miner = message["payload"]["is_miner"]

        # Let's send our 20 most "alive" peers to this user
        peers = self.connection_pool.get_alive_peers(20)

        peers_message = create_peers_message(
            self.server.external_ip, self.server.exteranl_port, peers
        )

        await self.send_message(writer, peers_message)

        if block_height < self.blockchain.last_block["height"]:
            # Send them each block in succession, from their height
            for block in self.blockchain.chain[block_height + 1]:
                await self.send_message(
                    writer,
                    create_block_message(
                        self.server.external_ip, self.server.external_port, block
                    ),
                )

    async def handle_transaction(self, message, writer):
        # Handles in incoming "transactions" message
        """
        Executed when we receive a transaction that was broadcast by a peer
        """
        logger.info("Received transaction")

        # Validate the transaction
        tx = message["payload"]

        if validate_transaction(tx) is True:
            # Add the tx to our pool, and propagate it to our peers
            if tx not in self.blockchain.pending_transactions:
                self.blockchain.pending_transactions.append(tx)

                for peer in self.connection_pool.get_alive_peers(20):
                    await self.send_message(
                        peer,
                        create_transaction_message(
                            self.server.external_ip, self.server.external_port, tx
                        ),
                    )
        else:
            logger.warning("Received invalid transaction")

    async def handle_block(self, message, writer):
        # Handles in incoming "block" message
        """
        Executed when we receive a block that was broadcast by a peer
        """
        logger.info("Recieved new block")

        block = message["payload"]

        # Give the block to the blockchain to append if valid
        self.blockchain.add_block(block)

        # Transmit the block to our peers
        for peer in self.connection_pool.get_alive_peers(20):
            await self.send_message(
                peer,
                create_block_message(
                    self.server.external_ip, self.server.external_port, block
                ),
            )

    async def handle_peers(self, message, writer):
        # Handles in incoming "peers" message
        """
        Executed when we receive a block that was broadcast by a peer
        """
        logger.info("Received new peers")

        peers = message["payload"]
