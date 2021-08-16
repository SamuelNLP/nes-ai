"""
Base env for every nes game
"""

from enum import Enum
from typing import Dict, Optional, Sequence, Tuple

from nes_py import NESEnv

from nes_ai.util.prerequisites import require_type


class BaseEnv(NESEnv):
    """
    A class that makes a custom NesEnv
    """

    # ram map for the specific environment
    # should have a enum as key and either a hex address or sequence as values
    RAM_INPUT_MAP: Dict = dict()

    def _read_byte(self, key: Enum) -> Optional[int]:
        """
        Reads a single address from the RAM, given that the address is in the enum
        """
        addr = self.RAM_INPUT_MAP.get(key)

        if addr:
            return self.ram[addr]
        return None

    def _read_bytes(self, key: Enum, big_endian: bool = False) -> int:
        """
        Reads a sequence of addresses from the RAM and takes into account what are the
            most significant bytes, considering the endianness.
        """
        values = self._read_bytes_array(key, big_endian)

        result = 0
        for idx, value in enumerate(values):
            result += 10 ** (2 * idx + 1) * (value >> 4)
            result += 10 ** (2 * idx) * (0x0F & value)

        return result

    def _read_bytes_array(self, key: Enum, big_endian: bool = False) -> Tuple[int, ...]:
        """
        Reads a sequence of addresses from the RAM and takes into account what are the
            most significant bytes, considering the endianness.
        """
        addrs = require_type(self.RAM_INPUT_MAP.get(key), Sequence)
        result = tuple(self.ram[addrs[0] : addrs[-1] + 1])

        if big_endian:
            result = tuple(reversed(result))

        return result
