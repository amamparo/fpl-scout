from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from prettytable import PrettyTable


class Position(Enum):
	GKP = 'GKP'
	DEF = 'DEF'
	MID = 'MID'
	FWD = 'FWD'


@dataclass
class Player:
	id: int
	name: str
	team: str
	position: Position
	ask: int
	projection: float
	value: float
	is_in_squad: bool
	bid: Optional[int] = None
	opponent: Optional[str] = None

	def __hash__(self) -> int:
		return self.id

	def __eq__(self, o: 'Player') -> bool:
		return self.id == o.id


@dataclass
class Squad:
	players: List[Player]

	def __init__(self, players: List[Player]):
		self.players = players

	def __str__(self) -> str:
		string = '\n'
		for position in [Position.GKP, Position.DEF, Position.MID, Position.FWD]:
			table = PrettyTable(['Team', 'Player', 'Cost', 'Proj.', 'Value'], float_format='0.2')
			table.align['Team'] = 'l'
			table.align['Player'] = 'l'
			table.align['Cost'] = 'r'
			table.align['Proj.'] = 'r'
			table.align['Value'] = 'r'
			for player in [x for x in self.players if x.position == position]:
				table.add_row([player.team, player.name, player.ask, player.projection, player.value])
			table.sortby = 'Proj.'
			table.reversesort = True
			string += f'{position.value}\n{table}\n\n'
		return string


@dataclass
class Lineup:
	starters: List[Player]
	bench: List[Player]
	captain: Player
	vice_captain: Player

	def __str__(self) -> str:
		def __table() -> PrettyTable:
			table = PrettyTable(['Pos.', 'Team', 'Player', 'Proj.', 'Opp.'], float_format='0.2')
			table.align['Pos.'] = 'c'
			table.align['Team'] = 'l'
			table.align['Player'] = 'l'
			table.align['Proj.'] = 'r'
			table.align['Opp.'] = 'l'
			return table

		string = '\n'
		starters_table = __table()
		for position in [Position.GKP, Position.DEF, Position.MID, Position.FWD]:
			position_starters = [x for x in self.starters if x.position == position]
			for starter in sorted(position_starters, key=lambda x: x.projection, reverse=True):
				role = '(C)' if starter == self.captain else '(V)' if starter == self.vice_captain else ''
				starters_table.add_row([position.value, starter.team, f'{starter.name} {role}'.strip(),
										starter.projection, starter.opponent])

		def __count_position(pos: Position) -> int:
			return len([x for x in self.starters if x.position == pos])

		num_def = __count_position(Position.DEF)
		num_mid = __count_position(Position.MID)
		num_fwd = __count_position(Position.FWD)
		string += f'Lineup ({num_def}-{num_mid}-{num_fwd})\n{starters_table}\n\n'

		subs_table = __table()
		for sub in self.bench:
			subs_table.add_row([sub.position.value, sub.team, sub.name, sub.projection, sub.opponent])
		subs_table.sortby = 'Proj.'
		subs_table.reversesort = True
		string += f'Subs\n{subs_table}\n\n'
		return string
