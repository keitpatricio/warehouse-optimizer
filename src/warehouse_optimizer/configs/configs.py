from dataclasses import dataclass
from pathlib import Path

@dataclass
class Config:
    kaggle_source_path: str = 'mustafakeser4/sap-dataset-bigquery-dataset'
    raw_data_path: Path = Path(r'C:\Users\keitpatricio\projects\warehouse_optimizer\data\raw')