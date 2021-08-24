import time
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Union

import requests
from injector import inject, singleton

from src.env import Environment


@singleton
class FplRepository:
  @inject
  def __init__(self, env: Environment):
    session = requests.Session()
    session.post('https://users.premierleague.com/accounts/login/', data={
      'login': env.get_fpl_email(),
      'password': env.get_fpl_password(),
      'app': 'plfpl-web',
      'redirect_uri': 'https://fantasy.premierleague.com/'
    })
    self.__cookie = '; '.join([f'{str(x)}={str(y)}' for x, y in session.cookies.items()])
    self.__cache: Dict[str, Union[dict, list]] = {}

  @dataclass
  class Player:
    id: int
    name: str
    position_id: int
    team_id: int
    buy_price: float
    ict_index: float
    selected_by_percent: float
    news: str
    is_fully_available: bool

  def get_players(self) -> List[Player]:
    return [
      self.Player(id=x['id'], name=x['web_name'], position_id=x['element_type'], team_id=x['team'],
                  buy_price=x['now_cost'] / 10, ict_index=float(x['ict_index']),
                  selected_by_percent=float(x['selected_by_percent']), news=x['news'],
                  is_fully_available=x['status'] == 'a')
      for x in self.__fetch_static_data()['elements']
    ]

  @dataclass
  class Team:
    id: int
    name: str

  def get_teams(self) -> List[Team]:
    return [
      self.Team(id=x['id'], name=x['short_name'])
      for x in self.__fetch_static_data()['teams']
    ]

  @dataclass
  class Position:
    id: int
    name: str

  def get_positions(self) -> List[Position]:
    return [
      self.Position(id=x['id'], name=x['singular_name_short'])
      for x in self.__fetch_static_data()['element_types']
    ]

  @dataclass
  class Fixture:
    id: int
    kickoff_time: float
    is_started: bool
    team_difficulties: Dict[int, int]

  def get_fixtures(self) -> List[Fixture]:
    return sorted([
      self.Fixture(id=x['id'], is_started=x['started'],
                   kickoff_time=time.mktime(datetime.strptime(x['kickoff_time'], '%Y-%m-%dT%H:%M:%SZ').timetuple()),
                   team_difficulties={
                     x['team_h']: x['team_h_difficulty'],
                     x['team_a']: x['team_a_difficulty']
                   })
      for x in self.__fetch('/api/fixtures/')
    ], key=lambda x: x.kickoff_time)

  @dataclass
  class Pick:
    player_id: int
    sell_price: float

  def get_picks(self) -> List[Pick]:
    entry_id = self.__fetch('/api/me/')['player']['entry']
    return [
      self.Pick(player_id=x['element'], sell_price=x['selling_price'] / 10)
      for x in self.__fetch(f'/api/my-team/{entry_id}/')['picks']
    ]

  def __fetch_static_data(self) -> dict:
    return self.__fetch('/api/bootstrap-static/')

  def __fetch(self, path: str) -> Union[dict, list]:
    cached = self.__cache.get(path)
    if cached is not None:
      return cached
    self.__cache[path] = requests.get(
      f'https://fantasy.premierleague.com{path}',
      headers={'cookie': self.__cookie}
    ).json()
    return self.__cache[path]
