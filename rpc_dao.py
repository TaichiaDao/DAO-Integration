import json
import os
from pathlib import Path
from pprint import pprint
from typing import Dict, Optional

import aiohttp
from chia.rpc.full_node_rpc_client import FullNodeRpcClient
from chia.types.blockchain_format.coin import Coin
from chia.types.blockchain_format.sized_bytes import bytes32
from chia.types.coin_record import CoinRecord
from chia.types.coin_spend import CoinSpend
from chia.types.spend_bundle import SpendBundle
from chia.util.config import load_config
from chia.util.ints import uint16, uint32


async def get_client():
    try:
        config_path = Path(os.path.expanduser("./")).resolve()
        config = load_config(config_path, "config.yaml")

        self_hostname = config["self_hostname"]
        full_node_rpc_port = config["full_node"]["rpc_port"]
        full_node_client = await FullNodeRpcClient.create(
            self_hostname, uint16(full_node_rpc_port), config_path, config
        )
        return full_node_client
    except Exception as e:
        if isinstance(e, aiohttp.ClientConnectorError):
            pprint(
                f"Connection error. Check if full node is running at {full_node_rpc_port}"
            )
        else:
            pprint(f"Exception from 'harvester' {e}")
        return None


async def get_coins_by_id(coin_id: bytes32) -> Optional[CoinRecord]:
    try:
        node_client = await get_client()
        coin_record = await node_client.get_coin_record_by_name(coin_id)
        return coin_record
    except Exception as e:
        pprint(f"Failed to get coin info, coin id: {str(coin_id)}, error: {e}")
        return None
    finally:
        node_client.close()
        await node_client.await_closed()


async def get_coins_by_puzzle_hash(puzzle_hash: bytes32, show_spent=False, start_height: Optional[int] = None) -> Dict:
    try:
        node_client = await get_client()
        coin_records = await node_client.get_coin_records_by_puzzle_hashes(
            [puzzle_hash], show_spent, start_height
        )
        coin_records = [rec.to_json_dict() for rec in coin_records]
        cr_dict = {}
        for record in coin_records:
            cr_dict[Coin.from_json_dict(record["coin"]).name().hex()] = record
        return cr_dict
    finally:
        node_client.close()
        await node_client.await_closed()


async def get_coins_by_parent(parent_id: bytes32, show_unspend=False):
    try:
        node_client = await get_client()
        coin_records = await node_client.get_coin_records_by_parent_ids(
            [parent_id], show_unspend
        )
        coin_records = [rec.to_json_dict() for rec in coin_records]
        cr_dict = {}
        for record in coin_records:
            cr_dict[Coin.from_json_dict(record["coin"]).name().hex()] = record
        return cr_dict
    finally:
        node_client.close()
        await node_client.await_closed()


async def get_coin_details(coin_id: bytes32, block_height: uint32) -> CoinSpend:
    try:
        node_client = await get_client()
        coin_spend = await node_client.get_puzzle_and_solution(coin_id, block_height)
        return coin_spend
    except Exception as e:
        pprint(f"Failed to get coin details, coin id: {str(coin_id)}, error: {e}")
        return None
    finally:
        node_client.close()
        await node_client.await_closed()


async def get_blockchain_state() -> Dict:
    try:
        node_client = await get_client()
        try:
            result = await node_client.get_blockchain_state()
            return result
        except Exception as e:
            pprint(f"Failed to get blockchain state, error: {e}")
            raise e
    finally:
        node_client.close()
        await node_client.await_closed()


async def push_tx(spend_bundle: SpendBundle) -> bool:
    try:
        node_client = await get_client()
        try:
            result = await node_client.push_tx(spend_bundle)
            result = json.dumps(result, sort_keys=True, indent=4)
            pprint(result)
            return True if result.find('"success": true') > 0 else False
        except Exception as e:
            pprint(f"Failed to push tx, error: {e}")
            if str(e).find("DOUBLE_SPEND") > 0:
                return True
            raise e
    finally:
        node_client.close()
        await node_client.await_closed()
