from typing import Any, Dict

from chia.types.blockchain_format.program import Program
from chia.types.blockchain_format.sized_bytes import bytes32
from chia.util.bech32m import decode_puzzle_hash, encode_puzzle_hash


class Cast:
    @staticmethod
    def hexstr_to_bytes(input_str: str) -> bytes:
        """
        Converts a hex string into bytes, removing the 0x if it's present.
        """
        if input_str.startswith("0x") or input_str.startswith("0X"):
            return bytes.fromhex(input_str[2:])
        return bytes.fromhex(input_str)

    @staticmethod
    def hexstr_to_bytes32(input_str: str) -> bytes32:
        """
        Converts a hex string into bytes, removing the 0x if it's present.
        """
        if input_str.startswith("0x") or input_str.startswith("0X"):
            return bytes.fromhex(input_str[2:])
        return bytes32(bytes.fromhex(input_str))

    @staticmethod
    def int_to_bytes(v: int) -> bytes:
        byte_count = (v.bit_length() + 8) >> 3
        if v == 0:
            return b""
        r: bytes = v.to_bytes(byte_count, "big", signed=True)
        # make sure the string returned is minimal
        # ie. no leading 00 or ff bytes that are unnecessary
        while len(r) > 1 and r[0] == (0xFF if r[1] & 0x80 else 0):
            r = r[1:]
        return r

    @staticmethod
    def str_to_hex(hex_str: str) -> str:
        return hex(int(hex_str, 16))[2:].zfill(64)

    @staticmethod
    def puzzle_to_address(puzzle_hash: bytes32) -> Any:
        return encode_puzzle_hash(puzzle_hash, "xch")

    @staticmethod
    def address_to_puzzle(address: str) -> bytes32:
        return decode_puzzle_hash(address)

    @staticmethod
    def metadata_to_program(metadata: Dict[str, Any]) -> Program:
        kv_list = []
        for key, value in metadata.items():
            if isinstance(value, dict):
                kv_list.append((key, Cast.metadata_to_program(value)))
            else:
                kv_list.append((key, value))
        return Program.to(kv_list)

    @staticmethod
    def program_to_metadata(program: Program) -> Dict[str, str]:
        metadata: Dict[str, str] = {}
        for key, value in program.as_python():
            k = str(key, "utf-8")
            try:
                metadata[k] = str(value, "utf-8")
            except Exception:
                # Try to covert byte to int
                metadata[k] = str(int.from_bytes(value, "big"))
        return metadata
