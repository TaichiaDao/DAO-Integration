import asyncio
from typing import Dict, Optional, Any

from rpc_dao import get_coins_by_puzzle_hash, get_coin_details
from cast import Cast
from chia.types.blockchain_format.coin import Coin
from chia.types.coin_spend import CoinSpend
from chia.util.ints import uint64, uint32
# Replace this with your DAO puzzle hash or the metadata puzzle hash you want to use as the root
DAO_ROOT_PUZHASH = "0c1c2a3fe23beb22ab89845dee3de61e4348586f173bd22ec6ddcf7e03bcbf69"
visited_puzhash = set()


async def load_metadata(puzhash: str) -> Optional[Dict[str, Any]]:
    try:
        if puzhash in visited_puzhash:
            return None
        visited_puzhash.add(puzhash)
        # Get coins in your metadata puzzle hash
        coin_records: Dict[str, Dict] = await get_coins_by_puzzle_hash(Cast.hexstr_to_bytes32(puzhash), show_spent=True)
        if coin_records is None or len(coin_records) == 0:
            return None
        # Get the latest spent coin
        coin: Optional[Coin] = None
        spent_block_height = 0
        for record in coin_records.values():
            if record["spent_block_index"] > spent_block_height:
                coin = Coin(
                    Cast.hexstr_to_bytes32(record["coin"]["parent_coin_info"]),
                    Cast.hexstr_to_bytes32(record["coin"]["puzzle_hash"]),
                    uint64(record["coin"]["amount"]),
                )
                spent_block_height = record["spent_block_index"]
        if coin is None:
            # No valid coin
            return None
        # Get coin solution
        coin_spend: CoinSpend = await get_coin_details(
            coin.name(), spent_block_height
        )
        if coin_spend is None:
            return None
        # Extract metadata
        metadata: Optional[Dict[str, Any]] = Cast.program_to_metadata(coin_spend.solution.to_program().first())
        # Recursive loading
        for key, value in metadata.items():
            try:
                # Check if the value is a byte32
                Cast.hexstr_to_bytes32(value)
                child_metadata = await load_metadata(value)
                if child_metadata is not None:
                    # This is a valid metadata puzzle hash
                    metadata[key] = child_metadata
            except Exception:
                pass
        return metadata
    except Exception as e:
        print(e)
        return None


async def load_my_config():
    metadata = await load_metadata(DAO_ROOT_PUZHASH)
    print(metadata)


def main():
    asyncio.run(load_my_config())


if __name__ == "__main__":
    main()
