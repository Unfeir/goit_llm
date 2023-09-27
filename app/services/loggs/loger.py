import logging
from os.path import abspath, join
from os.path import dirname as d

filepath = join(d(d(abspath(__file__))), 'loggs/app.log')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)

fh = logging.FileHandler(filepath)
fh.setLevel(logging.WARNING)
fh.setFormatter(formatter)
logger.addHandler(fh)
