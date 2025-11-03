def validate_wallet_address(address: str) -> str:
    if not address or not isinstance(address, str):
        raise ValueError("Wallet address is required")
    
    address = address.strip().lower()
    
    if not address.startswith('0x'):
        raise ValueError("Address must start with 0x")
    
    if len(address) != 42:
        raise ValueError("Address must be 42 characters long")
    
    return address
