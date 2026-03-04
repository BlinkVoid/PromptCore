"""Configuration settings for PromptCore."""

import os
from pathlib import Path

class Settings:
    """Application settings."""
    
    def __init__(self):
        # Default to project root / data
        default_data_dir = Path(__file__).parent.parent.parent / "data"
        self.DATA_DIR = Path(os.getenv("PROMPTCORE_DATA_DIR", str(default_data_dir)))
        
        # Default DB path
        # Default DB path
        db_path = os.getenv(
            "PROMPTCORE_DB_PATH",
            str(self.DATA_DIR / "reasoning_logs.db")
        )
        # Ensure it's a valid SQLAlchemy URL
        if "://" not in db_path:
            self.DB_PATH = f"sqlite:///{db_path}"
        else:
            self.DB_PATH = db_path

settings = Settings()
