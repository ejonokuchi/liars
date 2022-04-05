from timeit import default_timer
from typing import Any


def to_min_sec(elapsed_s: float) -> str:
    """Returns elapsed seconds as minutes and seconds for readability, e.g. 21m 23s."""
    minutes, seconds = map(int, divmod(elapsed_s, 60))
    return f"{minutes}m {seconds}s"


class ExecutionTime:
    """Context manager to record execution time using the system's default timer.

    The execution time is persisted in the `elapsed` attribute.

    Attributes:
        elapsed: Elapsed time in seconds, between the start time and the end time.
            Measured after the block exits.

    Examples:
        >>> with ExecutionTime() as t:
        >>>     time.sleep(0.5)
        >>> t.elapsed
        0.500211765000131
    """

    def __enter__(self) -> "ExecutionTime":
        """Begins the timer. Executed on context manager initialization."""
        self.start_time = default_timer()
        return self

    def __exit__(self, *exc: Any) -> bool:
        """Records the elapsed time. Executed on context manager teardown."""
        self.end_time = default_timer()
        self.elapsed = self.end_time - self.start_time
        return False
