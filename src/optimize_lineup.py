from dataclasses import dataclass
from typing import List

from injector import inject, Injector
from prettytable import PrettyTable

from src.models import Position, Player
from src.optimizer import Optimizer
from src.player_service import PlayerService


@inject
def main(player_service: PlayerService):
  squad = [x for x in player_service.get_players() if x.is_owned]
  optimizer = Optimizer(squad)
  optimizer.set_position_constraint(Position.GKP, minimum=1, maximum=1)
  optimizer.set_position_constraint(Position.DEF, minimum=3)
  optimizer.set_position_constraint(Position.FWD, minimum=1)
  optimizer.set_result_size_constraint(11)

  def __optimization_constraint_getter(player: Player) -> float:
    return player.next_fixture_quality * player.availability * player.quality

  starters = optimizer.solve(__optimization_constraint_getter)
  sorted_starters = sorted(starters, key=__optimization_constraint_getter, reverse=True)
  lineup = Lineup(
    starters=starters,
    bench=[x for x in squad if x not in starters],
    captain=sorted_starters[0],
    vice_captain=sorted_starters[1]
  )
  print(lineup)


@dataclass
class Lineup:
  starters: List[Player]
  bench: List[Player]
  captain: Player
  vice_captain: Player

  def __str__(self) -> str:
    def __table() -> PrettyTable:
      table = PrettyTable(['Pos.', 'Team', 'Player', 'Opp.', 'Fixture', 'Avail.', 'Quality'])
      table.align['Pos.'] = 'c'
      table.align['Team'] = 'l'
      table.align['Player'] = 'l'
      table.align['Opp'] = 'l'
      table.align['Fixture'] = 'r'
      table.align['Avail.'] = 'r'
      table.align['Quality'] = 'r'
      return table

    string = '\n'
    starters_table = __table()
    for position in [Position.GKP, Position.DEF, Position.MID, Position.FWD]:
      position_starters = [x for x in self.starters if x.position == position]
      for starter in sorted(position_starters, key=lambda x: x.quality, reverse=True):
        role = '(C)' if starter == self.captain else '(V)' if starter == self.vice_captain else ''
        starters_table.add_row([position.value, starter.team, f'{starter.name} {role}'.strip(),
                                starter.next_opponent, starter.next_fixture_quality, starter.availability,
                                starter.quality])

    def __count_position(pos: Position) -> int:
      return len([x for x in self.starters if x.position == pos])

    num_def = __count_position(Position.DEF)
    num_mid = __count_position(Position.MID)
    num_fwd = __count_position(Position.FWD)
    string += f'Lineup ({num_def}-{num_mid}-{num_fwd})\n{starters_table}\n\n'

    subs_table = __table()
    for sub in self.bench:
      subs_table.add_row([sub.position.value, sub.team, sub.name, sub.next_opponent, sub.next_fixture_quality,
                          sub.availability, sub.quality])
    subs_table.sortby = 'Quality'
    subs_table.reversesort = True
    string += f'Subs\n{subs_table}\n\n'
    return string


if __name__ == '__main__':
  Injector().call_with_injection(main)
