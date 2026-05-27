import os
import signal
import time
import threading
from .fifo_logger import setup_fifo_logger

# Initialize our FIFO telemetry logger
logger = setup_fifo_logger()

class ProcessWatchdog(threading.Thread):
    """
    A background supervisor thread that monitors process execution latencies.
    Forcefully terminates a stalled child process if it violates timeout parameters.
    """
    def __init__(self, target_pid: int, timeout_seconds: float):
        # Initialize the parent thread class
        super().__init__()
        self.target_pid = target_pid
        self.timeout = timeout_seconds
        self.start_time = time.time()
        self._is_active = True
        # Setting daemon=True ensures this thread dies instantly when main.py exits
        self.daemon = True

    def stop(self) -> None:
        """Signals that the monitored process completed its turn successfully."""
        self._is_active = False

    def run(self) -> None:
        """Executes the passive countdown monitoring loop."""
        logger.info(f"Watchdog activated for Process ID [{self.target_pid}] with a {self.timeout}s limit.")
        
        while self._is_active:
            elapsed_time = time.time() - self.start_time
            
            if elapsed_time > self.timeout:
                logger.warning(
                    f"🚨 TIMEOUT BREACH! Process [{self.target_pid}] hung for {elapsed_time:.1f}s. "
                    f"Executing forceful OS termination."
                )
                self._force_terminate()
                break
                
            # Sleep in short intervals to remain highly responsive to stop requests
            time.sleep(0.1)

    def _force_terminate(self) -> None:
        """Issues an active kernel-level SIGKILL to instantly clear the hung process from memory."""
        try:
            os.kill(self.target_pid, signal.SIGKILL)
            logger.info(f"Successfully sent SIGKILL to stalled Process ID [{self.target_pid}].")
        except ProcessLookupError:
            # The process might have finished right at the millisecond the timeout fired
            logger.info(f"Process ID [{self.target_pid}] was already terminated before SIGKILL landed.")
        except Exception as e:
            logger.error(f"Failed to issue SIGKILL to process {self.target_pid}: {str(e)}")
