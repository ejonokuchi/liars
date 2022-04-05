import logging
import time
from dataclasses import dataclass, field
from typing import List, Optional, Sequence

import numpy as np

from liars.action import Action, GameResult, GameState, make_bet, make_bullshit
from liars.number import to_str
from liars.player_interface import PlayerInterface

LOG = logging.getLogger(__name__)


@dataclass
class NaivePlayer(PlayerInterface):
    """Example implementation of a memoryless naive player.

    Methods:
        setup: Initializes the player. For multiple rounds, the player will be reused.
        start_game: Starts a new game for the player.
        make_move: Makes the next move in the game, given the current game state.
        end_game: Ends the current game for the player, with the result.
    """

    name: str = "unknown"
    number: int = field(init=False)
    player_idx: int = field(init=False)
    n_players: int = field(init=False)

    def setup(self):
        """Setup the player. "Thinks" for up to half a second."""
        time.sleep(np.random.random() * 0.5)
        return

    def start_game(self, number: int, player_idx: int, n_players: int):
        """Records the current game parameters."""
        self.number = number
        self.player_idxs = player_idx
        self.n_players = n_players
        return

    def _get_random_digit(self):
        """Gets a random digit from the current number."""
        return int(np.random.choice(list(to_str(self.number))))

    def make_move(self, state: GameState) -> Action:
        """Takes the next action, naively selecting bullshit 20% of the time."""
        # Make the first move.
        if len(state) == 0:
            return make_bet(count=1, digit=self._get_random_digit())

        # Not first move, need to think.
        time.sleep(np.random.random() * 0.5)

        last_player, last_duration, last_action = state[-1]
        p_bullshit = 0.2 * last_action.count
        if np.random.random() < p_bullshit:
            return make_bullshit()
        else:
            return make_bet(count=last_action.count + 1, digit=self._get_random_digit())

    def end_game(
        self, result: GameResult, state: GameState, numbers: Optional[Sequence[int]]
    ):
        """Logs the result."""
        if result == 1:
            LOG.info(f"{self.name}: I won!")
        elif result == 0:
            LOG.info(f"{self.name}: Aww shucks!")
        elif result == -1:
            LOG.info(f"{self.name}: I was expecting worse!")
        else:
            LOG.warning(f"{self.name}: Huh?")
