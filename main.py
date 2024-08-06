import os
from datetime import datetime, timezone
from rp2.configuration import Configuration
from rp2.plugin.country.us import us_plugin
from rp2_plugins.core_lightning import InTransaction

def main():
    # Load configuration
    config = Configuration("config.ini")

    # Set up date range for transaction fetch
    end_time = int(datetime.now(timezone.utc).timestamp())
    start_time = end_time - (365 * 24 * 60 * 60)  # 1 year ago

    # Fetch transactions
    rpc_path = config.get_option("core_lightning", "rpc_path")
    transactions = InTransaction.load_from_core_lightning(rpc_path, start_time, end_time)

    # Process transactions
    plugin = us_plugin()
    results = plugin.process_transactions(transactions)

    # Print results (you can customize this part)
    print(f"Total Profit/Loss: ${results.total_profit_and_loss}")
    print(f"Total Cost Basis: ${results.total_cost_basis}")
    print(f"Total Proceeds: ${results.total_proceeds}")

if __name__ == "__main__":
    main()