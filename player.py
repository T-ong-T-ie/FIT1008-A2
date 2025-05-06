from __future__ import annotations
from enums import PlayerPosition
import datetime


class Player:
    def __init__(self, name: str, position: PlayerPosition, age: int) -> None:
        """
        Constructor for the Player class

        Args:
            name (str): The name of the player
            position (PlayerPosition): The position of the player
            age (int): The age of the player

        Complexity:
            Best Case Complexity: O(1)
            Worst Case Complexity: O(1)
        """
        self.name = name
        # Calculate birth year based on current year and age
        current_year = datetime.datetime.now().year
        self.birth_year = current_year - age
        self.position = position
        self.goals = 0
        # Initialize statistics storage using HashTableSeparateChaining
        from data_structures.hash_table_separate_chaining import HashTableSeparateChaining
        self.stats = HashTableSeparateChaining()

    def reset_stats(self) -> None:
        """
        Reset the stats of the player.

        This doesn't delete the existing stats, but resets them to 0.
        I.e. all stats that were previously set should still be available, with a value of 0.

        Complexity:
            Best Case Complexity: O(1), when there are no stats
            Worst Case Complexity: O(N), where N is the number of statistics
        """
        stat_keys = self.stats.keys()
        for i in range(len(stat_keys)):
            self.stats[stat_keys[i]] = 0

    def __setitem__(self, statistic: str, value: int) -> None:
        """
        Set the given value for the given statistic for the player.

        Args:
            statistic (string): The key of the stat
            value (int): The value of the stat

        Complexity:
            Best Case Complexity: O(K), where K is the length of the statistic string
            Worst Case Complexity: O(N * K), where N is the number of items in the stats table, K is the length of the statistic string
        """
        self.stats[statistic] = value

    def __getitem__(self, statistic: str) -> int:
        """
        Get the value of the player's stat based on the passed key.

        Args:
            statistic (str): The key of the stat

        Returns:
            int: The value of the stat

        Complexity:
            Best Case Complexity: O(K), where K is the length of the statistic string
            Worst Case Complexity: O(N * K), where N is the number of items in the stats table, K is the length of the statistic string
        """
        try:
            return self.stats[statistic]
        except KeyError:
            raise KeyError(statistic)

    def get_age(self) -> int:
        """
        Get the age of the player

        Returns:
            int: The age of the player

        Complexity:
            Best Case Complexity: O(1)
            Worst Case Complexity: O(1)
        """
        current_year = datetime.datetime.now().year
        return current_year - self.birth_year

    def __str__(self) -> str:
        """
        String representation of the Player object for debugging.
        """
        return f"Player(name={self.name}, position={self.position}, age={self.get_age()}, goals={self.goals})"

    def __repr__(self) -> str:
        return str(self)