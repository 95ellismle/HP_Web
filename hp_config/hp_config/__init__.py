import logging
import sys

from pathlib import Path


path = Path(__file__).parent


# Setup logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)


dwelling_type = {name: i for i, name in enumerate(['Detached', 'Semi-Detached', 'Terraced', 'Flat/Maisonette', 'Other'])}
tenure = {'Freehold': 0, 'Leasehold': 1}

sort_index_len = 2500
