import logging
from l3_atom.stream_processing.standardiser import Standardiser
from l3_atom.off_chain import Gemini
from decimal import Decimal


class GeminiStandardiser(Standardiser):
    exchange = Gemini

    async def _trade(self, message):
        msg = dict(
            symbol=self.normalise_symbol(message['symbol']),
            price=Decimal(message['price']),
            size=Decimal(message['quantity']),
            taker_side=message['side'],
            trade_id=str(message['event_id']),
            event_timestamp=message['timestamp'],
            atom_timestamp=message['atom_timestamp']
        )
        await self.send_to_topic("trades", **msg)

    async def _book(self, message):
        symbol = self.normalise_symbol(message['symbol'])
        atom_timestamp = message['atom_timestamp']
        event_timestamp = atom_timestamp // 1000
        for event in message['changes']:
            side, price, size = event
            msg = dict(
                symbol=symbol,
                price=Decimal(price),
                size=Decimal(size),
                side=side,
                event_timestamp=event_timestamp,
                atom_timestamp=atom_timestamp
            )
            await self.send_to_topic("lob", **msg)

    async def _candle(self, message):
        symbol = self.normalise_symbol(message['symbol'])
        atom_timestamp = message['atom_timestamp']
        for m in message['changes']:
            event_timestamp, o, h, l, c, v = m
            end = event_timestamp
            start = end - 60 * 1000
            msg = dict(
                symbol=symbol,
                start=start,
                end=end,
                o=Decimal(str(o)),
                h=Decimal(str(h)),
                l=Decimal(str(l)),
                c=Decimal(str(c)),
                v=Decimal(str(v)),
                event_timestamp=event_timestamp,
                atom_timestamp=atom_timestamp,
                closed=None,
                interval='1m',
                trades=-1
            )
            await self.send_to_topic("candle", **msg)

    async def handle_message(self, msg):
        if msg['type'] == 'trade':
            await self._trade(msg)
        elif msg['type'] == 'l2_updates':
            await self._book(msg)
        elif msg['type'] == 'candles_1m_updates':
            await self._candle(msg)
        else:
            logging.warning(f"{self.id}: Unhandled message: {msg}")
