from abc import ABC, abstractmethod
from typing import List

import requests
from injector import inject
from unidecode import unidecode

from src.env import AbstractEnvironment
from src.roto_wire.models import Projection, ProjectionType


class AbstractRotoWireRepository(ABC):
	@abstractmethod
	def get_projections(self, projection_type: ProjectionType) -> List[Projection]:
		pass


class RotoWireRepository(AbstractRotoWireRepository):
	@inject
	def __init__(self, env: AbstractEnvironment):
		session = requests.Session()
		session.post(self.__get_url('/users/login.php'), data={
			'username': env.get_rotowire_username(),
			'password': env.get_rotowire_password()
		})
		self.__cookie = '; '.join([f'{str(x)}={str(y)}' for x, y in session.cookies.items()])

	def get_projections(self, projection_type: ProjectionType) -> List[Projection]:
		return [
			Projection(type=projection_type, id=int(x['ID']), name=unidecode(x['player']), team=x['team'],
					   positions=x['position'].split('/'), minutes=float(x['minutes']), goals=float(x['goals']),
					   assists=float(x['assists']), clean_sheets=float(x['cleansheet']), saves=float(x['saves']),
					   goals_conceded=float(x['goalsconc']), yellow_cards=float(x['yellowcard']),
					   red_cards=float(x['redcard']), opponent=x.get('opp'))
			for x in requests.get(
				self.__get_url(
					f'/soccer/tables/projections.php?position=All&league=EPL&type={projection_type.value}&myLeagueID=0'
				), headers={'cookie': self.__cookie}
			).json()
		]

	@staticmethod
	def __get_url(path: str) -> str:
		return f'https://www.rotowire.com{path}'
