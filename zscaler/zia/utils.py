#!/usr/bin/env python

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import time


def obfuscate_api_key(seed):
    now = int(time.time() * 1000)
    n = str(now)[-6:]
    r = str(int(n) >> 1).zfill(6)
    key = "".join(seed[int(str(n)[i])] for i in range(len(str(n))))
    for j in range(len(str(r))):
        key += seed[int(str(r)[j]) + 2]

    return {"timestamp": now, "key": key}


__version__ = "1.0.0"
