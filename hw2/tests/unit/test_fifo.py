import logging
from pathlib import Path
from hw2_agent.services.fifo_logger import setup_fifo_logger
from hw2_agent.config import load_config

def test_fifo_logger_rotation(tmp_path, monkeypatch):
    # Mock config
    test_log_dir = tmp_path / "logs"
    def mock_load_config():
        return {
            "fifo_logging": {
                "log_directory": str(test_log_dir),
                "max_backup_files": 2
            }
        }
    monkeypatch.setattr("hw2_agent.services.fifo_logger.load_config", mock_load_config)
    
    # We need to force re-initialization of the logger since it's a singleton-ish in the module
    # Actually, setup_fifo_logger() gets a logger by name "SystemOrchestrator"
    # I'll use a different name for testing or clear handlers
    
    logger = logging.getLogger("TestFIFO")
    logger.setLevel(logging.INFO)
    
    log_file = test_log_dir / "test.log"
    test_log_dir.mkdir(parents=True, exist_ok=True)
    
    from logging.handlers import RotatingFileHandler
    # 1KB limit for easy testing
    handler = RotatingFileHandler(log_file, maxBytes=1000, backupCount=2)
    logger.addHandler(handler)
    
    # Write ~1.5KB of data
    for i in range(20):
        logger.info("A" * 100) # 100 bytes + overhead
        
    # Should have test.log and test.log.1
    assert log_file.exists()
    assert (test_log_dir / "test.log.1").exists()
