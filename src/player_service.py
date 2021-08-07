import itertools
from abc import ABC, abstractmethod
from typing import List, Tuple

from fuzzywuzzy import process, fuzz
from injector import inject

from src.fpl.models import FplPlayer
from src.models import Player, Position
from src.roto_wire.models import Projection, ProjectionType
from src.fpl.fpl_repository import AbstractFplRepository
from src.roto_wire.roto_wire_repository import AbstractRotoWireRepository


class AbstractPlayerService(ABC):
	@abstractmethod
	def get_players(self, projection_type: ProjectionType) -> List[Player]:
		pass


class PlayerService(AbstractPlayerService):
	@inject
	def __init__(self, roto_wire_repository: AbstractRotoWireRepository, fpl_repository: AbstractFplRepository):
		self.__roto_wire_repository = roto_wire_repository
		self.__fpl_repository = fpl_repository

	def get_players(self, projection_type: ProjectionType) -> List[Player]:
		fpl_players = self.__fpl_repository.get_players()
		projections = self.__roto_wire_repository.get_projections(projection_type)
		players: List[Player] = []
		for fpl_team, roto_wire_team in self.__align_fpl_roto_wire_teams(fpl_players, projections):
			team_fpl_players = [x for x in fpl_players if x.team == fpl_team]
			team_projections = [x for x in projections if x.team == roto_wire_team]
			pairs: List[Tuple[FplPlayer, Projection]] = list(itertools.product(team_fpl_players, team_projections))
			fuzzy_pairs: List[Tuple[FplPlayer, Projection, int]] = [
				(x[0], x[1], fuzz.ratio(x[0].name, x[1].name)) for x in pairs
			]
			sorted_fuzzy_pairs = sorted(fuzzy_pairs, key=lambda x: x[2], reverse=True)
			while sorted_fuzzy_pairs:
				fpl_player, projection, score = sorted_fuzzy_pairs.pop(0)
				players.append(self.__create_player(fpl_player, projection))
				sorted_fuzzy_pairs = [x for x in sorted_fuzzy_pairs if x[0] != fpl_player and x[1] != projection]

		unprojected_fpl_players = [x for x in fpl_players if x.id not in [y.id for y in players]]
		for unprojected_fpl_player in unprojected_fpl_players:
			players.append(self.__create_player(unprojected_fpl_player, Projection(type=projection_type)))
		return players

	@staticmethod
	def __create_player(fpl_player: FplPlayer, projection: Projection) -> Player:
		goal_value: int = ({
			Position.GKP: 6, Position.DEF: 6, Position.MID: 5, Position.FWD: 4
		}).get(fpl_player.position, 0)
		clean_sheet_value: int = ({Position.GKP: 4, Position.DEF: 4, Position.MID: 1}).get(fpl_player.position, 0)
		goal_conceded_value: int = ({Position.GKP: -0.5, Position.DEF: -0.5}).get(fpl_player.position, 0)
		projection_value: float = (projection.goals * goal_value) + (projection.saves * (1 / 3)) + \
								  (projection.assists * 3) + (projection.clean_sheets * clean_sheet_value) + \
								  (projection.goals_conceded * goal_conceded_value) + (projection.yellow_cards * -1) + \
								  (projection.red_cards * -3) + (projection.minutes * ((4 / 3) / 90))
		return Player(id=fpl_player.id, name=fpl_player.name, team=fpl_player.team, position=fpl_player.position,
					  opponent=projection.opponent, bid=fpl_player.bid, ask=fpl_player.ask, projection=projection_value,
					  value=projection_value / fpl_player.ask, is_in_squad=fpl_player.is_in_squad)

	@staticmethod
	def __align_fpl_roto_wire_teams(fpl_players: List[FplPlayer], roto_wire_projections: List[Projection]) -> \
			List[Tuple[str, str]]:
		fpl_teams = list(set(x.team for x in fpl_players))
		roto_wire_teams = list(set(x.team for x in roto_wire_projections))
		matched_fpl_teams = [x for x in fpl_teams if x in roto_wire_teams]
		unmatched_fpl_teams = [x for x in fpl_teams if x not in roto_wire_teams]
		unmatched_roto_wire_teams = [x for x in roto_wire_teams if x not in fpl_teams]
		aligned_teams: List[Tuple[str, str]] = [(x, x) for x in matched_fpl_teams]
		for unmatched_fpl_team in unmatched_fpl_teams:
			roto_wire_team = process.extractOne(unmatched_fpl_team, unmatched_roto_wire_teams)[0]
			aligned_teams.append((unmatched_fpl_team, roto_wire_team))
		return aligned_teams
