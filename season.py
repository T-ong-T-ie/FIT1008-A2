from __future__ import annotations
from data_structures.array_set import ArraySet
from data_structures.referential_array import ArrayR
from data_structures.array_list import ArrayList
from data_structures.hash_table_separate_chaining import HashTableSeparateChaining
from enums import TeamGameResult, PlayerPosition
from game_simulator import GameSimulator, GameSimulationOutcome
from dataclasses import dataclass
from team import Team


@dataclass
class Game:
    """
    Simple container for a game between two teams.
    Both teams must be team objects, there cannot be a game without two teams.
    """
    home_team: Team = None
    away_team: Team = None


class WeekOfGames:
    """
    Simple container for a week of games.
    A fixture must have at least one game.
    """

    def __init__(self, week: int, games: ArrayR[Game] | ArrayList[Game]) -> None:
        """
        Container for a week of games.
        """
        self.games = games
        self.week: int = week
        self._iter_index = 0  # For iteration

    def __iter__(self):
        """
        Returns an iterator for the games in this week.

        Complexity:
            Best Case Complexity: O(1)
            Worst Case Complexity: O(1)
        """
        self._iter_index = 0
        return self

    def __next__(self):
        """
        Returns the next game in the iteration.

        Complexity:
            Best Case Complexity: O(1)
            Worst Case Complexity: O(1)
        """
        if self._iter_index >= len(self.games):
            raise StopIteration
        game = self.games[self._iter_index]
        self._iter_index += 1
        return game


class Season:
    def __init__(self, teams: ArrayR[Team] | ArrayList[Team]) -> None:
        """
        Initializes the season with a schedule.

        Args:
            teams (ArrayR[Team]): The teams played in this season.

        Complexity:
            Best Case Complexity: O(N^2 + W * G), where N is the number of teams, W is the number of weeks, G is the number of games per week.
            Worst Case Complexity: O(N^2 + W * G), same as best case.
        """
        self.teams = teams
        self.leaderboard = ArrayList()
        # Initialize leaderboard with teams and all teams start with 0 points
        for i in range(len(teams)):
            self.leaderboard.append(teams[i])
        # Generate schedule using _generate_schedule
        raw_schedule = self._generate_schedule()  # ArrayList[ArrayList[Game]]
        self.schedule = ArrayList()
        for week_idx in range(len(raw_schedule)):
            week_games = raw_schedule[week_idx]
            self.schedule.append(WeekOfGames(week_idx + 1, week_games))

    def _generate_schedule(self) -> ArrayList[ArrayList[Game]]:
        """
        Generates a schedule by generating all possible games between the teams.
        """
        num_teams: int = len(self.teams)
        weekly_games: ArrayList[ArrayList[Game]] = ArrayList()
        flipped_weeks: ArrayList[ArrayList[Game]] = ArrayList()
        games: ArrayList[Game] = ArrayList()

        # Generate all possible matchups (team1 vs team2, team2 vs team1, etc.)
        for i in range(num_teams):
            for j in range(i + 1, num_teams):
                games.append(Game(self.teams[i], self.teams[j]))

        # Allocate games into each week ensuring no team plays more than once in a week
        week: int = 0
        while games:
            current_week: ArrayList[Game] = ArrayList()
            flipped_week: ArrayList[Game] = ArrayList()
            used_teams: ArraySet = ArraySet(len(self.teams))

            week_game_no: int = 0
            for game in games:
                if game.home_team.name not in used_teams and game.away_team.name not in used_teams:
                    current_week.append(game)
                    used_teams.add(game.home_team.name)
                    used_teams.add(game.away_team.name)

                    flipped_week.append(Game(game.away_team, game.home_team))
                    games.remove(game)
                    week_game_no += 1

            weekly_games.append(current_week)
            flipped_weeks.append(flipped_week)
            week += 1

        for flipped_week in flipped_weeks:
            weekly_games.append(flipped_week)
        return weekly_games

    def update_leaderboard(self) -> None:
        """
        Updates the leaderboard based on teams' points and names.

        Complexity:
            Best Case Complexity: O(N^2), where N is the number of teams.
            Worst Case Complexity: O(N^2), where N is the number of teams.
        """
        n = len(self.leaderboard)
        for i in range(n):
            for j in range(0, n - i - 1):
                team1 = self.leaderboard[j]
                team2 = self.leaderboard[j + 1]
                if (team1.points < team2.points) or \
                        (team1.points == team2.points and team1.name > team2.name):
                    self.leaderboard[j], self.leaderboard[j + 1] = team2, team1

    def get_leaderboard(self) -> ArrayList[Team]:
        """
        Returns the current leaderboard.

        Returns:
            ArrayList[Team]: The sorted array of teams.

        Complexity:
            Best Case Complexity: O(N^2), where N is the number of teams.
            Worst Case Complexity: O(N^2), where N is the number of teams.
        """
        self.update_leaderboard()
        return self.leaderboard

    def simulate_season(self) -> None:
        """
        Simulates the season.

        Complexity:
            G = total number of games = N(N-1), where N is the number of teams.
            P = average number of players per team.
            GS = average number of goals per game (small constant).
            GameSimulator.simulate() complexity: O(P).
            Best Case Complexity: O(G * (N^2 + P + GS * P)) = O(N^2 * (N^2 + P))
            Worst Case Complexity: O(G * (N^2 + P + GS * P)) = O(N^2 * (N^2 + P))
        """
        simulator = GameSimulator()
        for week in self.schedule:
            for game in week:
                outcome = simulator.simulate(game.home_team, game.away_team)

                # Update team results
                if outcome.home_goals > outcome.away_goals:
                    game.home_team.add_result(TeamGameResult.WIN)
                    game.away_team.add_result(TeamGameResult.LOSS)
                elif outcome.home_goals < outcome.away_goals:
                    game.home_team.add_result(TeamGameResult.LOSS)
                    game.away_team.add_result(TeamGameResult.WIN)
                else:
                    game.home_team.add_result(TeamGameResult.DRAW)
                    game.away_team.add_result(TeamGameResult.DRAW)

                # Get all players for both teams
                home_players = game.home_team.get_players()
                away_players = game.away_team.get_players()

                # Count outfield players (non-goalkeepers) for allocation
                home_outfield_count = 0
                away_outfield_count = 0
                for i in range(len(home_players)):
                    if home_players[i].position != PlayerPosition.GOALKEEPER:
                        home_outfield_count += 1
                for i in range(len(away_players)):
                    if away_players[i].position != PlayerPosition.GOALKEEPER:
                        away_outfield_count += 1

                # Allocate ArrayList for outfield players
                home_outfield = ArrayList()
                away_outfield = ArrayList()

                # Populate outfield players
                for i in range(len(home_players)):
                    if home_players[i].position != PlayerPosition.GOALKEEPER:
                        home_outfield.append(home_players[i])
                for i in range(len(away_players)):
                    if away_players[i].position != PlayerPosition.GOALKEEPER:
                        away_outfield.append(away_players[i])

                # Map player names to objects for efficient lookup using HashTableSeparateChaining
                player_map = HashTableSeparateChaining()
                for i in range(len(home_outfield)):
                    player_map[home_outfield[i].name] = home_outfield[i]
                for i in range(len(away_outfield)):
                    player_map[away_outfield[i].name] = away_outfield[i]

                # Update goals for scorers
                for i in range(len(outcome.goal_scorers)):
                    scorer_name = outcome.goal_scorers[i]
                    if scorer_name in player_map:
                        player_map[scorer_name].goals += 1

                # Update leaderboard after each game
                self.update_leaderboard()

    def delay_week_of_games(self, orig_week: int, new_week: int | None = None) -> None:
        """
        Delay a week of games from one week to another.

        Args:
            orig_week (int): The original week to move the games from.
            new_week (int or None): The new week to move the games to. If this is None, it moves the games to the end of the season.

        Complexity:
            Best Case Complexity: O(W), where W is the number of weeks.
            Worst Case Complexity: O(W), where W is the number of weeks.
        """
        orig_idx = orig_week - 1  # Convert to 0-based index
        if orig_idx < 0 or orig_idx >= len(self.schedule):
            raise ValueError("Invalid original week")

        # Extract the week to delay
        week_to_move = self.schedule[orig_idx]

        if new_week is None:
            # Delay to the end of the season
            for i in range(orig_idx, len(self.schedule) - 1):
                self.schedule[i] = self.schedule[i + 1]
            self.schedule[len(self.schedule) - 1] = week_to_move
        else:
            # Delay to an existing week
            new_idx = new_week - 1  # Convert to 0-based index
            if new_idx < 0 or new_idx >= len(self.schedule):
                raise ValueError("Invalid new week")

            if orig_idx < new_idx:
                for i in range(orig_idx, new_idx):
                    self.schedule[i] = self.schedule[i + 1]
                self.schedule[new_idx] = week_to_move
            else:
                for i in range(orig_idx, new_idx, -1):
                    self.schedule[i] = self.schedule[i - 1]
                self.schedule[new_idx] = week_to_move

    def __len__(self) -> int:
        """
        Returns the number of teams in the season.

        Complexity:
            Best Case Complexity: O(1)
            Worst Case Complexity: O(1)
        """
        return len(self.teams)

    def __str__(self) -> str:
        """
        Returns a string representation of the Season object.
        """
        return f"Season(teams={len(self.teams)}, leaderboard={len(self.leaderboard)}, schedule={len(self.schedule)})"

    def __repr__(self) -> str:
        """Returns a string representation of the Season object."""
        return str(self)