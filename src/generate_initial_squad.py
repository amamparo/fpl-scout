from typing import List, Dict

from injector import inject, Injector
from prettytable import PrettyTable

from src.models import Position, Player
from src.optimizer import Optimizer
from src.player_service import PlayerService


@inject
def main(player_service: PlayerService) -> None:
  optimizer = Optimizer(player_service.get_players())
  optimizer.set_budget_constraint(100)
  optimizer.set_position_constraint(Position.GKP, minimum=2, maximum=2)
  optimizer.set_position_constraint(Position.DEF, minimum=5, maximum=5)
  optimizer.set_position_constraint(Position.MID, minimum=5, maximum=5)
  optimizer.set_position_constraint(Position.FWD, minimum=3, maximum=3)
  optimizer.set_team_constraints()

  def __optimization_constraint_getter(player: Player) -> float:
    return player.selected_by_percent

  __print_squad(optimizer.solve(__optimization_constraint_getter))


def __print_squad(players: List[Player]) -> None:
  for position in [Position.GKP, Position.DEF, Position.MID, Position.FWD]:
    table = PrettyTable(['Team', 'Player', 'Fixtures', 'Quality', 'Avail.', 'Sel. %', 'Cost'])
    table.align['Team'] = 'l'
    table.align['Player'] = 'l'
    table.align['Fixtures'] = 'r'
    table.align['Quality'] = 'r'
    table.align['Avail.'] = 'r'
    table.align['Sel. %'] = 'r'
    table.align['Cost'] = 'r'
    for player in [x for x in players if x.position == position]:
      table.add_row([player.team, player.name, player.upcoming_fixtures_quality, player.quality, player.availability,
                     f'{player.selected_by_percent}%', player.buy_price])
    table.sortby = 'Cost'
    table.reversesort = True
    print(f'{position.value}\n{table}\n')


if __name__ == '__main__':
  Injector().call_with_injection(main)
