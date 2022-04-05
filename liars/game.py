import itertools
import logging
from dataclasses import dataclass, field
from typing import Dict, Generator, Optional, Sequence, Tuple

import numpy as np

from liars.action import ensure_valid_raise
from liars.execution_time import ExecutionTime, to_min_sec
from liars.number import get_random_numbers, to_counts
from liars.player_interface import PlayerInterface

LOG = logging.getLogger(__name__)


@dataclass
class Game:
    """A Liar's Poker game.

    Args:
        players: A list of the players for this game.

    Attributes:
        player_generator: Iterator to cycle through the players.

    Methods:
        setup: Sets up each player in the game.
        play: Plays a single round.
        play_many: Plays many rounds of the game.
    """

    players: Sequence[PlayerInterface]
    player_generator: Generator[Tuple[int, PlayerInterface], None, None] = field(
        init=False
    )

    def __post_init__(self):
        """Create the player iterator."""
        self.player_generator = itertools.cycle(enumerate(self.players))

    def setup(self):
        """Sets up each player in the game, logging setup times."""
        LOG.info(f"Initializing {len(self.players)} players...")
        for idx, player in enumerate(self.players):
            with ExecutionTime() as t:
                player.setup()

            LOG.debug(
                f"Setup for player {idx} ({type(player).__name__}) took "
                f"{to_min_sec(t.elapsed)}"
            )

    def play(self, first_move: Optional[int] = None) -> Tuple[int, int]:
        """Plays a round of the game.

        Randomly assigns numbers and cycles through the players' moves. The game ends
        when any player calls Exact or Bullshit.
            If the Exact call is right, the game ends in a tie.
            If the Exact call is wrong, the player with the previous bet wins.
            If the Bullshit call is right, the player calling Bullshit wins.
            If the Bullshit call is wrong, the player with the previous bet wins.

        Args:
            first_move: If not None, the first move is given to this player. Otherwise,
                the first move is given to a random player.

        Raises:
            ValueError: If a player makes a Bet that is invalid. See ensure_valid_raise.
            RuntimeError: If the first move of the game is a non-bet action, i.e. Exact
                or Bullshit.

        Returns:
            winner_idx: Index of the winning player. -1 if the game ends in a tie.
        """
        LOG.debug(f"Assigning numbers")
        numbers = get_random_numbers(n=len(self.players))
        for idx, player in enumerate(self.players):
            player.start_game(
                number=numbers[idx], player_idx=idx, n_players=len(self.players)
            )

        # Assign first move and cycle the generator to the right index.
        if first_move is not None:
            first_idx = first_move
        else:
            first_idx = np.random.randint(len(self.players))

        while True:
            idx, player = next(self.player_generator)
            if ((idx + 1) % len(self.players)) == first_idx:
                break

        LOG.info(
            f"Playing game, first move to player {first_idx} "
            f"({type(self.players[first_idx]).__name__})"
        )

        # Core game loop
        total_counts = np.sum([to_counts(number) for number in numbers], axis=0)

        game_state = []
        prev_idx, prev_action = None, None
        winner_idx = None
        while winner_idx is None:
            idx, player = next(self.player_generator)
            LOG.debug(f"Getting next action for player {idx} ({type(player).__name__})")
            with ExecutionTime() as t:
                action = player.make_move(state=game_state)
            LOG.debug(f"Player selected {action} after {to_min_sec(t.elapsed)}")

            game_state.append((idx, t.elapsed, action))

            # Process the action
            if action.is_bet:
                # Raise
                ensure_valid_raise(bet=action, previous_bet=prev_action)
                prev_idx, prev_action = idx, action
                continue

            elif prev_action is None:
                raise RuntimeError(
                    "Cannot take a non-bet action as the first move of the game!"
                )

            elif action.is_exact:
                # Exact, right
                if prev_action.count == total_counts[prev_action.digit]:
                    winner_idx = -1
                # Exact, wrong
                else:
                    winner_idx = prev_idx

            else:
                # Bullshit, right
                if prev_action.count > total_counts[prev_action.digit]:
                    winner_idx = idx
                # Bullshit, wrong
                else:
                    winner_idx = prev_idx

        LOG.info(f"Winner is player {idx} ({type(player).__name__}), notifying players")

        # Notify the players of their results.
        for idx, player in enumerate(self.players):
            if winner_idx == -1:
                result = -1
            elif winner_idx == idx:
                result = 1
            else:
                result = 0
            player.end_game(
                result=result,
                state=game_state,
                numbers=numbers,
            )

        return winner_idx

    def play_many(self, n_rounds: int) -> Dict[int, Tuple[str, float]]:
        """Runs a simulation of many rounds of a game.

        Args:
            n_rounds: Number of rounds to play. In subsequent games, the winner is given
                the first move.

        Returns:
            winner_idxs: List of winning player indices.

        See Also:
            game.play
        """
        LOG.info(f"Running simulation for {n_rounds} rounds...")

        winner_idxs = []
        last_winner_idx = None
        for _ in range(n_rounds):
            winner_idx = self.play(first_move=last_winner_idx)
            winner_idxs.append(winner_idx)
            last_winner_idx = winner_idx if winner_idx != -1 else None

        return winner_idxs
