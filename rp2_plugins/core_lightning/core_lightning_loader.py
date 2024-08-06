import os
from datetime import datetime, timezone
from typing import List
from decimal import Decimal

from pyln.client import LightningRpc
from rp2.abstract_transaction import AbstractTransaction
from rp2.rp2_decimal import RP2Decimal

class CoreLightningRP2Loader:
    def __init__(self, rpc_path: str):
        self.rpc = LightningRpc(rpc_path)

    def fetch_transactions(self, start_time: int, end_time: int) -> List[AbstractTransaction]:
        # Fetch on-chain transactions
        onchain_txs = self.rpc.listtransactions()
        
        # Fetch Lightning Network transactions
        lightning_txs = self.rpc.listpays()
        
        # Convert transactions to RP2 AbstractTransactions
        rp2_transactions = []
        for tx in onchain_txs:
            rp2_tx = self._convert_onchain_to_rp2(tx)
            if rp2_tx and start_time <= rp2_tx.timestamp.timestamp() <= end_time:
                rp2_transactions.append(rp2_tx)
        
        for tx in lightning_txs:
            rp2_tx = self._convert_lightning_to_rp2(tx)
            if rp2_tx and start_time <= rp2_tx.timestamp.timestamp() <= end_time:
                rp2_transactions.append(rp2_tx)

        return rp2_transactions

    def _convert_onchain_to_rp2(self, cl_tx) -> AbstractTransaction:
        # Convert satoshis to BTC
        amount_btc = RP2Decimal(str(Decimal(cl_tx['amount_msat']) / Decimal(100_000_000_000)))
        
        # Determine transaction type
        if amount_btc > 0:
            tx_type = 'receive'
        else:
            tx_type = 'send'
            amount_btc = abs(amount_btc)

        # Fetch spot price (you may need to implement this separately)
        spot_price = self._get_spot_price(cl_tx['timestamp'])

        return AbstractTransaction(
            timestamp=datetime.fromtimestamp(cl_tx['timestamp'], tz=timezone.utc),
            asset="BTC",
            from_exchange="CoreLightning" if tx_type == 'send' else "external",
            from_holder="user" if tx_type == 'send' else "unknown",
            to_exchange="CoreLightning" if tx_type == 'receive' else "external",
            to_holder="user" if tx_type == 'receive' else "unknown",
            spot_price=spot_price,
            crypto_in=amount_btc if tx_type == 'receive' else RP2Decimal('0'),
            crypto_fee=RP2Decimal('0'),  # Fees are typically included in the amount for on-chain transactions
            fiat_in=RP2Decimal('0') if tx_type == 'receive' else amount_btc * spot_price,
            fiat_fee=RP2Decimal('0')
        )

    def _convert_lightning_to_rp2(self, cl_tx) -> AbstractTransaction:
        # Convert millisatoshis to BTC
        amount_btc = RP2Decimal(str(Decimal(cl_tx['amount_msat']) / Decimal(100_000_000_000)))
        
        # Determine transaction type
        tx_type = 'send' if cl_tx['direction'] == 'outgoing' else 'receive'

        # Fetch spot price (you may need to implement this separately)
        spot_price = self._get_spot_price(cl_tx['created_at'])

        return AbstractTransaction(
            timestamp=datetime.fromtimestamp(cl_tx['created_at'], tz=timezone.utc),
            asset="BTC",
            from_exchange="CoreLightning" if tx_type == 'send' else "LightningNetwork",
            from_holder="user" if tx_type == 'send' else "unknown",
            to_exchange="LightningNetwork" if tx_type == 'send' else "CoreLightning",
            to_holder="unknown" if tx_type == 'send' else "user",
            spot_price=spot_price,
            crypto_in=amount_btc if tx_type == 'receive' else RP2Decimal('0'),
            crypto_fee=RP2Decimal('0'),  # Lightning Network fees are typically very small and can be ignored for tax purposes
            fiat_in=RP2Decimal('0') if tx_type == 'receive' else amount_btc * spot_price,
            fiat_fee=RP2Decimal('0')
        )

    def _get_spot_price(self, timestamp: int) -> RP2Decimal:
        # Implement a method to fetch the spot price at the time of the transaction
        # This could involve calling an external API or using a local price database
        # For simplicity, we're returning a placeholder value here
        return RP2Decimal('30000')  # Placeholder: $30,000 per BTC
