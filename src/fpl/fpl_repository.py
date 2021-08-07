from abc import ABC, abstractmethod
from typing import List, Dict

import requests
from injector import inject
from unidecode import unidecode

from src.env import AbstractEnvironment
from src.fpl.models import FplPlayer
from src.models import Position


class AbstractFplRepository(ABC):
	@abstractmethod
	def get_players(self) -> List[FplPlayer]:
		pass


class FplRepository(AbstractFplRepository):
	@inject
	def __init__(self, env: AbstractEnvironment):
		session = requests.Session()
		session.post('https://users.premierleague.com/accounts/login/', data={
			'login': env.get_fpl_email(),
			'password': env.get_fpl_password(),
			'app': 'plfpl-web',
			'redirect_uri': 'https://fantasy.premierleague.com/'
		})
		self.__cookie = '; '.join([f'{str(x)}={str(y)}' for x, y in session.cookies.items()])

	def get_players(self) -> List[FplPlayer]:
		data = requests.get('https://fantasy.premierleague.com/api/bootstrap-static/').json()
		position_lookup: Dict[int, Position] = {
			x['id']: Position(x['singular_name_short']) for x in data['element_types']
		}
		team_lookup: Dict[int, str] = {x['id']: x['short_name'] for x in data['teams']}
		picks = self.__get_current_picks()
		players: List[FplPlayer] = []
		for element in data['elements']:
			pick = next((x for x in picks if x['element'] == element['id']), None)
			players.append(
				FplPlayer(id=element['id'], name=unidecode(element['web_name']), team=team_lookup[element['team']],
						  position=position_lookup[element['element_type']], bid=(pick or {}).get('selling_price'),
						  ask=element['now_cost'], is_in_squad=pick is not None)
			)
		return players

	def __get_current_picks(self) -> List[dict]:
		entry_id = requests.get(
			'https://fantasy.premierleague.com/api/me/',
			headers={'cookie': self.__cookie}
		).json()['player']['entry']
		return requests.get(
			f'https://fantasy.premierleague.com/api/my-team/{entry_id}/',
			headers={'cookie': self.__cookie}
		).json()['picks']
