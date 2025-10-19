from warehouse_optimizer.helpers.source import get_kaggle_data
from warehouse_optimizer.configs.configs import Config

def ingest_kaggle_data(config: Config) -> None:
    get_kaggle_data(
        source_path = config.kaggle_source_path,
        destination_path = config.raw_data_path
    )