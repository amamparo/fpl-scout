import sys
from typing import List

import pulp

from src.models import Player, Position


class Optimizer:
	def __init__(self, players: List[Player]):
		self.__problem = pulp.LpProblem(sense=pulp.LpMaximize)
		self.__players = players
		self.__indexes = range(len(players))
		self.__player_variables = [pulp.LpVariable(f'player_{x.id}', cat='Binary') for x in players]

	def set_budget_constraint(self, budget: int) -> None:
		self.__problem += pulp.lpSum(
			self.__players[i].ask * self.__player_variables[i]
			for i in self.__indexes
		) <= budget

	def set_position_constraint(self, position: Position, minimum: int = 0, maximum: int = sys.maxsize) -> None:
		self.__problem += minimum <= pulp.lpSum(
			self.__player_variables[i] * (self.__players[i].position == position)
			for i in self.__indexes
		) <= maximum

	def set_team_constraints(self) -> None:
		for team in list(set(x.team for x in self.__players)):
			self.__problem += pulp.lpSum(
				self.__player_variables[i] * (self.__players[i].team == team)
				for i in self.__indexes
			) <= 3

	def set_result_size_constraint(self, size: int) -> None:
		self.__problem += pulp.lpSum(x for x in self.__player_variables) == size

	def solve(self) -> List[Player]:
		self.__problem += pulp.lpSum(self.__players[i].projection * self.__player_variables[i] for i in self.__indexes)
		self.__problem.solve(pulp.PULP_CBC_CMD(msg=False))
		players: List[Player] = []
		for i in self.__indexes:
			if self.__player_variables[i].value() == 1:
				players.append(self.__players[i])
		return players
