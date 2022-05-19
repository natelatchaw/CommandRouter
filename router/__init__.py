# support type annotations for Python versions < v3.9
from __future__ import annotations

import logging
import sys

"""
Command Router

A module-based command handler.
"""

__version__ = '0.0.2'
__author__ = 'Nathan Latchaw'



logging.basicConfig(filename='.log', encoding='utf-8', level=logging.DEBUG)

logger: logging.Logger= logging.getLogger()
handler: logging.StreamHandler = logging.StreamHandler(sys.stdout)
formatter: logging.Formatter = logging.Formatter('[%(asctime)s] [%(pathname)s:%(lineno)d] [%(levelname)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
