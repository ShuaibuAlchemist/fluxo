from utils.utils import load_abis,CHAINLINK_ORACLES_CONTRACTS
from core.config import MANTLE_RPC_URL

from web3 import Web3,AsyncHTTPProvider
from eth_utils import to_checksum_address

# Initialize Web3 instance for Mantle network
w3_mantle = Web3(AsyncHTTPProvider(MANTLE_RPC_URL))

ABIS = load_abis()

class ChainlinkService:
    def __init__(self):
        self.web3 = w3_mantle
        self.oracles = {}
        for pair, address in CHAINLINK_ORACLES_CONTRACTS.items():
            checksum_address = to_checksum_address(address)
            contract = self.web3.eth.contract(address=checksum_address, abi=ABIS[pair])
            self.oracles[pair] = contract

    async def get_price(self, pair: str) -> float:
        """Fetch the latest price for a given pair from Chainlink oracle."""
        if pair not in self.oracles:
            raise ValueError(f"Oracle for pair {pair} not found.")
        
        oracle_contract = self.oracles[pair]
        latest_round_data = await oracle_contract.functions.latestRoundData().call()
        # The price is typically in the second element of the returned tuple
        price = latest_round_data[1]
        # Adjust price based on decimals
        decimals = await oracle_contract.functions.decimals().call()
        adjusted_price = price / (10 ** decimals)
        return adjusted_price