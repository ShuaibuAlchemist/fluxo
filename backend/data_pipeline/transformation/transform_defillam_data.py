from typing import List
from ..schemas.data_schemas import ProtocolData,YieldlProtocol


def transform_protocol_data(protocols_data:List)->list[ProtocolData]|None:
    if not protocols_data:
        return None
    
    transformed_protocols_data = []
    for protocol_data in protocols_data:

        transformed_protocols_data.append(ProtocolData(
            name=protocol_data['name'],
            slug=protocol_data['slug'],
            chain=protocol_data['chain'],
            tvl=protocol_data['tvl'],
            category=protocol_data['category'],
            url=protocol_data['url'],
            twitter=protocol_data['twitter']
        ))
    
    return transformed_protocols_data


def transform_yield_protocol(yield_datas:List)->List[YieldlProtocol] | None:
    if not yield_datas:
        return None
    
    transformed_yield_data = []
    for yield_data in yield_datas:

        transformed_yield_data.append(YieldlProtocol(
            project=yield_data['project'],
            symbol=yield_data['symbol'],
            tvlUsd=yield_data['tvlUsd'],
            apy=yield_data['apy'],
            apyBase=yield_data['apyBase'],
            apyReward=yield_data['apyReward']
        ))

    return transformed_yield_data