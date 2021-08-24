from typing import List

from injector import inject, Injector
from prettytable import PrettyTable

from src.models import Position, Player
from src.optimizer import Optimizer
from src.player_service import PlayerService


@inject
def main(player_service: PlayerService) -> None:
  players = player_service.get_players()
  current_squad = [x for x in players if x.is_owned]
  optimizer = Optimizer(players)
  optimizer.set_budget_constraint(100)
  optimizer.set_position_constraint(Position.GKP, minimum=2, maximum=2)
  optimizer.set_position_constraint(Position.DEF, minimum=5, maximum=5)
  optimizer.set_position_constraint(Position.MID, minimum=5, maximum=5)
  optimizer.set_position_constraint(Position.FWD, minimum=3, maximum=3)
  optimizer.set_transfers_constraint(current_squad, 1)
  optimizer.set_team_constraints()

  def __optimization_constraint_getter(player: Player) -> float:
    return player.selected_by_percent

  new_squad = optimizer.solve(__optimization_constraint_getter)

  __print_squad(current_squad, new_squad)


def __print_squad(current_squad: List[Player], new_squad: List[Player]) -> None:
  for position in [Position.GKP, Position.DEF, Position.MID, Position.FWD]:
    table = PrettyTable(['Team', 'Player', 'Fixtures', 'Quality', 'Avail.', 'Sel. %', 'Cost'])
    table.align['Team'] = 'l'
    table.align['Player'] = 'l'
    table.align['Fixtures'] = 'r'
    table.align['Quality'] = 'r'
    table.align['Avail.'] = 'r'
    table.align['Sel. %'] = 'r'
    table.align['Cost'] = 'r'
    for player in [x for x in new_squad if x.position == position]:
      table.add_row([player.team, player.name, player.upcoming_fixtures_quality, player.quality, player.availability,
                     f'{player.selected_by_percent}%', player.buy_price])
    table.sortby = 'Cost'
    table.reversesort = True
    print(f'{position.value}\n{table}\n')

  out_list = ', '.join([
    f'{player.name} ({player.position} - {player.selected_by_percent})'
    for player in [x for x in current_squad if x not in new_squad]
  ])
  print(f'Out: {out_list}')


if __name__ == '__main__':
  Injector().call_with_injection(main)
