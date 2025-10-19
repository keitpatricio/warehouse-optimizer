from dotenv import load_dotenv
from pathlib import Path
import kaggle 

def get_kaggle_data(source_path: str, destination_path: str|Path) -> None:
    
    # --- Set destination path ---
    if isinstance(destination_path, str):
        destination_path = Path(destination_path)
    
    destination_path.mkdir(parents=True, exist_ok=True)

    # --- Download dataset ---
    kaggle.api.dataset_download_files(
        source_path,                    # dataset handle
        path=str(destination_path),     # destination
        unzip=True                      # auto-extract zip
    )