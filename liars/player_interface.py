from abc import ABCMeta, abstractmethod
from typing import Optional, Sequence

from liars.action import Action, GameResult, GameState


class PlayerInterface(metaclass=ABCMeta):
    """Player in the Liar's Poker game.

    Methods:
        setup: Initializes the player. In a multi-game simulation, the player is reused.
        start_game: Starts a new game for the player.
        make_move: Makes the next move in the current game, given the game state.
        end_game: Ends the current game for the player and provides the result.
    """

    @abstractmethod
    def setup(self):
        pass

    @abstractmethod
    def start_game(self, number: int, player_idx: int, n_players: int):
        pass

    @abstractmethod
    def make_move(self, state: GameState) -> Action:
        pass

    @abstractmethod
    def end_game(
        self,
        result: GameResult,
        state: GameState,
        numbers: Optional[Sequence[int]],
    ):
        pass
