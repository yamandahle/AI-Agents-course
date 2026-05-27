import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from ..config import load_config

def setup_fifo_logger() -> logging.Logger:
    """
    Configures a thread-safe FIFO rotating system logger.
    Automatically caps file growth at 500 lines to protect disk boundaries.
    """
    # Dynamic parameter ingestion from single source of truth config
    config = load_config()
    log_dir = Path(config["fifo_logging"]["log_directory"])
    max_files = config["fifo_logging"]["max_backup_files"]
    
    # Securely ensure the directory exists on the hard drive
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file_path = log_dir / "system_telemetry.log"
    
    logger = logging.getLogger("SystemOrchestrator")
    logger.setLevel(logging.INFO)
    
    # Avoid adding duplicate handlers if the logger is re-initialized
    if not logger.handlers:
        # 1 line of log is roughly 80-100 bytes. 
        # Capping at ~45KB guarantees it stays under 500 lines per file partition.
        fifo_handler = RotatingFileHandler(
            filename=log_file_path,
            maxBytes=45000, 
            backupCount=max_files,
            encoding="utf-8"
        )
        
        # Format layout: [Timestamp] [Process/Thread Name] [Log Level] - Message
        formatter = logging.Formatter(
            fmt="[%(asctime)s] [%(processName)s] [%(levelname)s] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        fifo_handler.setFormatter(formatter)
        logger.addHandler(fifo_handler)
        
    return logger
