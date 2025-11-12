from pydantic import BaseModel
from typing import Dict, Any
from enum import Enum


class pubsubMessage(BaseModel):
    channel: str
    data: Any

class ChannelNames(Enum):
    
    AUTOMATION = "automation_channel"
    PORTFOLIO = "portfolio_channel"
    RISK = "risk_channel"
    MARKET_DATA = "market_data_channel"
    SOCIAL = "social_channel"
    ONCHAIN = "onchain_channel"
    EXECUTION = "execution_channel"
    MACRO = "macro_channel"
    RESEARCH = "research_channel"
    X402 = "x402_channel"
    YIELD = "yield_channel"