import asyncio
from l3_atom.off_chain import Coinbase, Binance
import sys

mapping = {
    'coinbase': Coinbase,
    'binance': Binance
}

def main():
    exchange_feed = mapping[sys.argv[1]]()
    loop = asyncio.get_event_loop()
    exchange_feed.start(loop)

    loop.run_forever()

if __name__ == "__main__":
    main()