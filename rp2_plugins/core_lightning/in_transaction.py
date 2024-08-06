from rp2.abstract_transaction import AbstractTransaction
from rp2.rp2_decimal import RP2Decimal

class InTransaction(AbstractTransaction):
    def __init__(self, abstract_tx: AbstractTransaction):
        super().__init__(
            timestamp=abstract_tx.timestamp,
            asset=abstract_tx.asset,
            from_exchange=abstract_tx.from_exchange,
            from_holder=abstract_tx.from_holder,
            to_exchange=abstract_tx.to_exchange,
            to_holder=abstract_tx.to_holder,
            spot_price=abstract_tx.spot_price,
            crypto_in=abstract_tx.crypto_in,
            crypto_fee=abstract_tx.crypto_fee,
            fiat_in=abstract_tx.fiat_in,
            fiat_fee=abstract_tx.fiat_fee
        )

    @classmethod
    def load_from_core_lightning(cls, rpc_path: str, start_time: int, end_time: int):
        from .core_lightning_loader import CoreLightningRP2Loader
        loader = CoreLightningRP2Loader(rpc_path)
        transactions = loader.fetch_transactions(start_time, end_time)
        return [cls(tx) for tx in transactions]
    