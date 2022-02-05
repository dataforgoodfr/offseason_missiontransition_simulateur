import hashlib

import numpy as np


def intmd5(source: str, nbytes=4) -> int:
    """
    Generate a predictive random integer of nbytes*8 bits based on a source string.

    :param source:
    seed string to generate random integer.

    :param nbytes:
    size of the integer.
    """

    hashobj = hashlib.md5(source.encode())
    return int.from_bytes(hashobj.digest()[:nbytes], byteorder="big", signed=False)


v_intmd5 = np.vectorize(intmd5)
