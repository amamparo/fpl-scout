import sys
from typing import List, Callable, Dict

import pulp

from src.models import Position, Player


class Optimizer:
  def __init__(self, players: List[Player]):
    self.__problem = pulp.LpProblem(sense=pulp.LpMaximize)
    self.__players = players
    self.__indexes = range(len(players))
    self.__player_variables = [pulp.LpVariable(f'player_{x.id}', cat='Binary') for x in players]

  def set_budget_constraint(self, budget: int) -> None:
    self.__problem += pulp.lpSum(
      self.__players[i].buy_price * self.__player_variables[i]
      for i in self.__indexes
    ) <= budget

  def set_position_constraint(self, position: Position, minimum: int = 0, maximum: int = sys.maxsize) -> None:
    position_sum = pulp.lpSum(
      self.__player_variables[i] * (self.__players[i].position == position)
      for i in self.__indexes
    )
    self.__problem += position_sum <= maximum
    self.__problem += position_sum >= minimum

  def set_team_constraints(self, team_limits: Dict[str, int] = None) -> None:
    team_limits = team_limits or {}
    for team in list(set(x.team for x in self.__players)):
      self.__problem += pulp.lpSum(
        self.__player_variables[i] * (self.__players[i].team == team) for i in self.__indexes
      ) <= team_limits.get(team, 3)

  def set_restricted_players_constraint(self, restricted_players: List[Player]) -> None:
    self.__problem += pulp.lpSum(
      self.__player_variables[i] * (self.__players[i] in restricted_players) for i in self.__indexes
    ) == 0

  def set_result_size_constraint(self, size: int) -> None:
    self.__problem += pulp.lpSum(x for x in self.__player_variables) == size

  def solve(self, optimization_constraint_getter: Callable[[Player], float]) -> List[Player]:
    self.__problem += pulp.lpSum(
      optimization_constraint_getter(self.__players[i]) * self.__player_variables[i]
      for i in self.__indexes
    )
    self.__problem.solve(pulp.PULP_CBC_CMD(msg=False))
    players: List[Player] = []
    for i in self.__indexes:
      if self.__player_variables[i].value() == 1:
        players.append(self.__players[i])
    return players
