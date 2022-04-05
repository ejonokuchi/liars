from dataclasses import dataclass
from typing import Literal, Optional, Sequence, Tuple


@dataclass(frozen=True)
class Action:
    """
    A valid game action.

    Must be one of the following:
        Exact: A claim that the previous action was exactly true.
        Bullshit: A claim that the previous action was an overstatement.
        Bet: A claim that there are _at least_ some number of some digit between all the
            numbers in the current game.
    """

    is_exact: bool = False
    is_bullshit: bool = False
    is_bet: bool = False
    count: Optional[int] = None
    digit: Optional[int] = None

    def __post_init__(self):
        """Validates arguments after initialization."""
        if not sum([self.is_exact, self.is_bullshit, self.is_bet]) == 1:
            raise ValueError(
                "Action must be exactly one of exact, bullshit, or bet. Found: "
                f"is_exact = {self.is_exact}, is_bullshit = {self.is_bullshit}, "
                f"is_bet = {self.is_bet}"
            )
        if self.is_bet:
            if self.count is None:
                raise ValueError("Bet must specify a count, found None")
            if self.digit is None:
                raise ValueError("Bet must specify a digit, found None")
            if self.count <= 0:
                raise ValueError(f"Bet count must be at least 1, found {self.count}")
            if not 0 <= self.digit <= 9:
                raise ValueError(f"Bet digit must be in [0, 9], found {self.digit}")
        return

    def __repr__(self):
        """Returns a string representation of an Action."""
        if self.is_exact:
            return "Action(Exact)"
        elif self.is_bullshit:
            return "Action(Bullshit)"
        else:
            return f"Action(Bet, count={self.count}, digit={self.digit})"


def ensure_valid_raise(bet: Action, previous_bet: Optional[Action] = None):
    """Ensures a bet is a valid, optionally considering a previous bet."""
    if previous_bet is None:
        return True
    if not previous_bet.is_bet:
        raise ValueError(
            "Cannot take another action after a non-bet action, previous action was "
            f"{previous_bet}"
        )
    if not (bet.digit > previous_bet.digit or bet.count > previous_bet.count):
        raise ValueError(
            f"Bet of {bet.count} {bet.digit}s was not a valid raise from previous bet "
            f"of {previous_bet.count} {previous_bet.digit}s"
        )
    return


def make_bet(count: int, digit: int) -> Action:
    """Makes a bet action with the specified count and digit."""
    return Action(is_bet=True, count=count, digit=digit)


def make_bullshit() -> Action:
    """Makes a Bullshit action."""
    return Action(is_bullshit=True)


def make_exact() -> Action:
    """Returns an Exact action."""
    return Action(is_exact=True)


GameState = Sequence[Tuple[int, float, Action]]
"""Game state, including all player actions as [(player_id, duration, action)]."""

GameResult = Literal[1, 0, -1]
"""Game result, specific to each player. 1 is a win, 0 is a loss, and -1 is a tie."""
