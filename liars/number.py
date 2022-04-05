from typing import List

import numpy as np

NUM_DIGITS = 8


def to_str(number: int) -> str:
    """Returns a zero-padded string representation of a number."""
    return format(number, f"0{NUM_DIGITS}d")


def to_counts(number: int) -> np.ndarray:
    """Returns a dictionary of digit counts for a number."""
    counts = np.zeros(10, dtype=np.uint8)
    for digit in map(int, to_str(number)):
        counts[digit] += 1
    return counts


def get_random_number() -> int:
    """Returns a random number in the configured range."""
    return np.random.randint(0, 10**NUM_DIGITS)


def get_random_numbers(n: int) -> List[int]:
    """Returns a random sequence of unique numbers in the configured range."""
    numbers = set()
    while len(numbers) < n:
        numbers.add(get_random_number())
    return list(numbers)
