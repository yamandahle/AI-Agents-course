import time
import os
import signal
import multiprocessing
from hw2_agent.services.watchdog import ProcessWatchdog

def slow_process(q):
    q.put(os.getpid())
    time.sleep(10)

def test_watchdog_termination():
    q = multiprocessing.Queue()
    p = multiprocessing.Process(target=slow_process, args=(q,))
    p.start()
    pid = q.get()
    
    # Watchdog with 1s timeout
    watchdog = ProcessWatchdog(pid, timeout_seconds=1.0)
    watchdog.run() # Run directly in this thread for testing
    
    p.join(timeout=1)
    assert not p.is_alive()
    # If it was killed by SIGKILL, exitcode should be -9 (or 247 on some systems)
    assert p.exitcode != 0
