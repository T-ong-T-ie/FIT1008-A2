from __future__ import annotations
from data_structures.referential_array import ArrayR
from data_structures.hash_table_separate_chaining import HashTableSeparateChaining
from enums import TeamGameResult, PlayerPosition
from player import Player
from typing import Collection, TypeVar

T = TypeVar("T")

class Team:
    # Use ArrayR to store position to index mapping
    _POSITION_MAPPING = ArrayR(len(PlayerPosition.__members__))
    _POSITION_MAPPING[0] = PlayerPosition.GOALKEEPER
    _POSITION_MAPPING[1] = PlayerPosition.DEFENDER
    _POSITION_MAPPING[2] = PlayerPosition.MIDFIELDER
    _POSITION_MAPPING[3] = PlayerPosition.STRIKER

    # Static mapping of TeamGameResult to points using HashTableSeparateChaining, and use the name of the enum as the key
    _POINTS_MAP = HashTableSeparateChaining()
    _POINTS_MAP[TeamGameResult.WIN.name] = 3
    _POINTS_MAP[TeamGameResult.DRAW.name] = 1
    _POINTS_MAP[TeamGameResult.LOSS.name] = 0

    def __init__(self, team_name: str, initial_players: ArrayR[Player], history_length: int) -> None:
        """
        Constructor for the Team class

        Args:
            team_name (str): The name of the team
            initial_players (ArrayR[Player]): The players the team starts with initially
            history_length (int): The number of `GameResult`s to store in the history

        Returns:
            None

        Complexity:
            Best Case Complexity: O(N), where N is the number of initial players.
            Worst Case Complexity: O(N), where N is the number of initial players.
        """
        self.name = team_name
        self.points = 0
        self._history_length = history_length
        # Initialize players array based on number of enum members
        max_pos = len(self._POSITION_MAPPING) - 1
        self.players = ArrayR(max_pos + 1)
        self.player_counts = ArrayR(max_pos + 1)  # Track number of players per position
        self.player_count = 0
        # Pre-allocate space for each position (assuming max 100 players per position)
        MAX_PLAYERS_PER_POSITION = 100
        for i in range(max_pos + 1):
            self.players[i] = ArrayR(MAX_PLAYERS_PER_POSITION)  # Pre-allocate with max size
            self.player_counts[i] = 0
        # Populate initial players
        for player in initial_players:
            pos_idx = 0
            while pos_idx < len(self._POSITION_MAPPING) and self._POSITION_MAPPING[pos_idx] != player.position:
                pos_idx += 1
            if pos_idx >= len(self._POSITION_MAPPING):
                raise ValueError("Invalid player position")
            current_count = self.player_counts[pos_idx]
            if current_count >= MAX_PLAYERS_PER_POSITION:
                raise ValueError("Too many players in this position")
            self.players[pos_idx][current_count] = player
            self.player_counts[pos_idx] += 1
            self.player_count += 1
        # Initialize history and posts
        self.history = ArrayR(history_length)
        self.history_start = 0
        self.history_count = 0
        self.posts = HashTableSeparateChaining()

    def add_player(self, player: Player) -> None:
        """
        Adds a player to the team.

        Args:
            player (Player): The player to add

        Returns:
            None

        Complexity:
            Best Case Complexity: O(1)
            Worst Case Complexity: O(1)
        """
        pos_idx = 0
        while pos_idx < len(self._POSITION_MAPPING) and self._POSITION_MAPPING[pos_idx] != player.position:
            pos_idx += 1
        if pos_idx >= len(self._POSITION_MAPPING):
            raise ValueError("Invalid player position")
        current_count = self.player_counts[pos_idx]
        if current_count >= len(self.players[pos_idx]):
            raise ValueError("Too many players in this position")
        self.players[pos_idx][current_count] = player
        self.player_counts[pos_idx] += 1
        self.player_count += 1

    def remove_player(self, player: Player) -> None:
        """
        Removes a player from the team.

        Args:
            player (Player): The player to remove

        Returns:
            None

        Complexity:
            Best Case Complexity: O(N), where N is the number of players in the position.
            Worst Case Complexity: O(N), where N is the number of players in the position.
        """
        pos_idx = 0
        while pos_idx < len(self._POSITION_MAPPING) and self._POSITION_MAPPING[pos_idx] != player.position:
            pos_idx += 1
        if pos_idx >= len(self._POSITION_MAPPING):
            raise ValueError("Invalid player position")
        current_count = self.player_counts[pos_idx]
        found = False
        for i in range(current_count):
            if self.players[pos_idx][i] == player:
                found = True
                # Shift elements to maintain order
                for j in range(i, current_count - 1):
                    self.players[pos_idx][j] = self.players[pos_idx][j + 1]
                self.players[pos_idx][current_count - 1] = None
                self.player_counts[pos_idx] -= 1
                self.player_count -= 1
                break
        if not found:
            raise ValueError(f"Player {player.name} not found in team {self.name}")

    def get_players(self, position: PlayerPosition | None = None) -> Collection[Player]:
        """
        Returns the players of the team that play in the specified position.

        Args:
            position (PlayerPosition or None): The position of the players to return

        Returns:
            Collection[Player]: The players that play in the specified position

        Complexity:
            Best Case Complexity: O(1), when position is specified and list is empty.
            Worst Case Complexity: O(N + P * M), where N is total players, P is number of positions, M is max players per position.
        """
        if position is not None:
            pos_idx = 0
            while pos_idx < len(self._POSITION_MAPPING) and self._POSITION_MAPPING[pos_idx] != position:
                pos_idx += 1
            if pos_idx >= len(self._POSITION_MAPPING):
                raise ValueError("Invalid player position")
            count = self.player_counts[pos_idx]
            result = ArrayR(count)
            for i in range(count):
                result[i] = self.players[pos_idx][i]
            return result
        result = ArrayR(self.player_count)
        idx = 0
        for pos_idx in range(len(self._POSITION_MAPPING)):
            count = self.player_counts[pos_idx]
            for i in range(count):
                player = self.players[pos_idx][i]
                if player is not None:
                    result[idx] = player
                    idx += 1
        return result

    def add_result(self, result: TeamGameResult) -> None:
        """
        Add the `result` to this `Team`'s history

        Args:
            result (TeamGameResult): The result to add

        Complexity:
            Best Case Complexity: O(1)
            Worst Case Complexity: O(1)
        """
        # Update points using HashTableSeparateChaining with enum name as key
        self.points += self._POINTS_MAP[result.name]
        # Add to history
        if self.history_count < self._history_length:
            self.history[self.history_count] = result
            self.history_count += 1
        else:
            self.history[self.history_start] = result
            self.history_start = (self.history_start + 1) % self._history_length

    def get_history(self) -> Collection[TeamGameResult] | None:
        """
        Returns the `GameResult` history of the team.

        Returns:
            Collection[TeamGameResult]: The most recent `GameResult`s for this team
            or None if the team has not played any games.

        Complexity:
            Best Case Complexity: O(1), when history is empty.
            Worst Case Complexity: O(N), where N is history_length.
        """
        if self.history_count == 0:
            return None
        result = ArrayR(self.history_count)
        start = self.history_start
        for i in range(self.history_count):
            idx = (start + i) % self._history_length
            result[i] = self.history[idx]
        return result

    def make_post(self, post_date: str, post_content: str) -> None:
        """
        Publish a team blog `post` for a particular `post_date`.

        Args:
            `post_date` (`str`) - The date of the post
            `post_content` (`str`) - The content of the post

        Returns:
            None

        Complexity:
            Best Case Complexity: O(K), where K is the length of the date string.
            Worst Case Complexity: O(N * K), where N is the number of posts, K is the length of the date string.
        """
        self.posts[post_date] = post_content

    def __len__(self) -> int:
        """
        Returns the number of players in the team.

        Complexity:
            Best Case Complexity: O(1)
            Worst Case Complexity: O(1)
        """
        return self.player_count

    def __str__(self) -> str:
        """
        String representation for debugging.
        """
        return f"Team(name={self.name}, points={self.points}, players={self.player_count})"

    def __repr__(self) -> str:
        return str(self)