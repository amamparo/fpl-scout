import sys
from typing import List, Callable

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

  def set_team_constraints(self) -> None:
    for team in list(set(x.team for x in self.__players)):
      self.__problem += pulp.lpSum(
        self.__player_variables[i] * (self.__players[i].team == team) for i in self.__indexes
      ) <= 3

  def set_result_size_constraint(self, size: int) -> None:
    self.__problem += pulp.lpSum(x for x in self.__player_variables) == size

  def set_transfers_constraint(self, current_squad: List[Player], max_transfers: int) -> None:
    current_squad_player_ids = [x.id for x in current_squad]
    self.__problem += pulp.lpSum(
      self.__player_variables[i] * (self.__players[i].id not in current_squad_player_ids) for i in self.__indexes
    ) <= max_transfers

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
