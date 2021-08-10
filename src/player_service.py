from dataclasses import dataclass
from statistics import mean
from typing import List, Dict, Optional

from injector import inject, singleton

from src.fpl_repository import FplRepository
from src.models import Player, Position


@singleton
class PlayerService:
  @inject
  def __init__(self, fpl_repository: FplRepository):
    self.__fpl_repository = fpl_repository

  @dataclass
  class __Team:
    id: int
    name: str
    next_opponent_name: str
    upcoming_fixtures_quality: float
    next_fixture_quality: float

  def get_players(self) -> List[Player]:
    pick_lookup: Dict[int, FplRepository.Pick] = {x.player_id: x for x in self.__fpl_repository.get_picks()}
    players: List[PlayerService.Player] = []
    fpl_players = self.__fpl_repository.get_players()
    team_lookup = self.__get_team_lookup()
    for position in self.__fpl_repository.get_positions():
      position_players = [x for x in fpl_players if x.position_id == position.id]
      for player in position_players:
        availability = 1 if player.is_fully_available else \
          float(next(x for x in player.news.split() if x.endswith('%')).replace('%', '')) / 100 if '%' in player.news \
          else 0
        team = team_lookup[player.team_id]
        pick: Optional[FplRepository.Pick] = pick_lookup.get(player.id)
        players.append(Player(id=player.id, name=player.name, team=team.name, next_opponent=team.next_opponent_name,
                              position=Position(position.name), buy_price=player.buy_price,
                              sell_price=pick.sell_price if pick else None, is_owned=pick is not None,
                              next_fixture_quality=team.next_fixture_quality,
                              upcoming_fixtures_quality=team.upcoming_fixtures_quality,
                              selected_by_percent=player.selected_by_percent,
                              availability=availability, quality=player.ict_index))

    return players

  def __get_team_lookup(self) -> Dict[int, __Team]:
    fixtures = self.__fpl_repository.get_fixtures()
    team_lookup: Dict[int, FplRepository.Team] = {x.id: x for x in self.__fpl_repository.get_teams()}
    teams: [List[PlayerService.__Team]] = []
    for team in team_lookup.values():
      upcoming_fixtures = [x for x in fixtures if team.id in x.team_difficulties][:6]
      next_fixture = upcoming_fixtures[0]
      next_opponent_id = next(team_id for team_id in next_fixture.team_difficulties if team_id != team.id)
      upcoming_fixture_qualities = [1 - ((x.team_difficulties[team.id] - 1) / 4) for x in upcoming_fixtures]
      teams.append(self.__Team(id=team.id, name=team.name, next_opponent_name=team_lookup[next_opponent_id].name,
                               next_fixture_quality=upcoming_fixture_qualities[0],
                               upcoming_fixtures_quality=mean(upcoming_fixture_qualities)))
    return {x.id: x for x in teams}
