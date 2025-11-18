import logging
from typing import List,Optional,AsyncIterator
from pydantic import BaseModel

from web3 import Web3,AsyncHTTPProvider,AsyncWeb3,WebSocketProvider
from eth_utils import to_checksum_address
from eth_abi import decode
from eth_abi.exceptions import InsufficientDataBytes

from core.config import MANTLE_RPC_URL,MANTLE_WSS_URL

logger = logging.getLogger(__name__)

class TranferReponse(BaseModel):
    token: str
    from_address: str
    to_address: str
    amount: int
    transaction_hash: str
    block_number: int

class MantleAPI:
    def __init__(self):
        transfer_event_signature = "Transfer(address,address,uint256)"
        self.tranfer_topic = [ AsyncWeb3.keccak(text=transfer_event_signature)]
        self.subscription_id : Optional[str] = None
        self.w3 = None
        self.web3 = AsyncWeb3(AsyncHTTPProvider(MANTLE_RPC_URL))

    # Fetch MNT user balance
    async def get_balance(self, address: str) -> float:
        """Fetch the balance of an address on the Mantle network."""
        checksum_address = to_checksum_address(address)
        balance_wei = await self.web3.eth.get_balance(checksum_address)
        balance_eth = self.web3.fromWei(balance_wei, 'ether')
        return balance_eth
    
    # fetch user token balance
    async def get_token_balance(self, token_address: str, wallet_address: str) -> float:
        """
        Fetch the ERC20 token balance of a wallet on the Mantle network.
        """
        checksum_token_address = to_checksum_address(token_address)
        checksum_wallet_address = to_checksum_address(wallet_address)
        
        # ERC20 Token ABI (only the balanceOf function)
        erc20_abi = [
            {"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"},
            {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"},
        ]
        
        token_contract = self.web3.eth.contract(address=checksum_token_address, abi=erc20_abi)
        balance = await token_contract.functions.balanceOf(checksum_wallet_address).call()
        decimals = await token_contract.functions.decimals().call()
        adjusted_balance = balance / (10 ** decimals)
        return adjusted_balance


    # Listen to tokens Transfer Events
    async def tranfers_event(self) -> AsyncIterator[dict]:
        """"
        This function get all the token transfer happening in mantle Network
        
        return:
            AsyncIterato[dict]
            TranferReponse(
                token=to_checksum_address(log.get("address")),
                from_address=from_address,
                to_address=to_address,
                amount=amount,
                transaction_hash= "0x" + log.get("transactionHash").hex(),
                block_number=log.get("blockNumber")
            )
        """
        async with AsyncWeb3(WebSocketProvider(MANTLE_WSS_URL)) as w3:
            self.w3 = w3

            params = {
                "address": None,
                "topics": self.tranfer_topic
            }
            self.subscription_id = await w3.eth.subscribe("logs", params)
            print(f"Subscribed to Transfer events with subscription ID: {self.subscription_id}")

            async for payload in w3.socket.process_subscriptions():
                if payload.get("subscription") != self.subscription_id:
                        continue
                        
                log = payload.get("result")
                if not log:
                    continue
                
                # Determine event type from topic0
                topic0 = log.get("topics", [])[0] if log.get("topics") else None
                if not topic0:
                    continue

                if topic0 != self.tranfer_topic[0]:
                    continue

                transfer_event = await self._parse_transfer_event(log)
                if not transfer_event:
                    continue
                yield transfer_event

    # Pasrse Transfer Event Log
    async def _parse_transfer_event(self,log:dict)->TranferReponse|None:
        try:
            topics = log.get("topics", [])
            data = log.get("data", "0x")

            from_address = to_checksum_address("0x" + topics[1].hex()[24:])
            to_address = to_checksum_address("0x" + topics[2].hex()[24:])
            
            if isinstance(data, str):
                data =  bytes.fromhex(data[2:] if data.startswith('0x') else data)
        
            amount = decode(['uint256'], data)[0]
            return TranferReponse(
                token=to_checksum_address(log.get("address")),
                from_address=from_address,
                to_address=to_address,
                amount=amount,
                transaction_hash= "0x" + log.get("transactionHash").hex(),
                block_number=log.get("blockNumber")
            )
        except InsufficientDataBytes as e:
            logger.error(f"Error decoding event data: {e}")
            return None