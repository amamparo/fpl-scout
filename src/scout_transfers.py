import itertools
from typing import List, Tuple

from injector import inject, Injector
from prettytable import PrettyTable
from tqdm import tqdm

from src.fpl_repository import FplRepository
from src.models import Position, Player
from src.optimizer import Optimizer
from src.player_service import PlayerService

n_transfers: int = 2


@inject
def main(player_service: PlayerService, fpl_repository: FplRepository) -> None:
  players = player_service.get_players()
  current_squad = [x for x in players if x.is_owned]
  combos = []
  bank = fpl_repository.get_bank()
  for i in range(n_transfers):
    combos.extend(list(itertools.combinations(current_squad, i + 1)))
  results: List[Tuple[List[Player], List[Player], float]] = []
  for combo in tqdm(combos):
    outgoing_players = list(combo)
    optimizer = Optimizer(players)
    optimizer.set_restricted_players_constraint(current_squad)
    freed_salary = sum(x.sell_price for x in outgoing_players)
    optimizer.set_budget_constraint(bank + freed_salary)
    team_limits = {}
    for other_squad_player in [x for x in current_squad if x not in outgoing_players]:
      team = other_squad_player.team
      team_limits[team] = team_limits.get(team, 3) - 1
    optimizer.set_team_constraints(team_limits)
    for position in Position:
      n_position_players = len([x for x in outgoing_players if x.position == position])
      optimizer.set_position_constraint(position, minimum=n_position_players, maximum=n_position_players)

    def __optimization_constraint_getter(player: Player) -> float:
      return player.selected_by_percent

    incoming_players = optimizer.solve(__optimization_constraint_getter)
    results.append((
      outgoing_players, incoming_players,
      sum(__optimization_constraint_getter(x) for x in incoming_players) -
      sum(__optimization_constraint_getter(x) for x in outgoing_players)
    ))
  result = sorted(results, key=lambda x: x[-1], reverse=True)[0]
  print(f'Out: {", ".join(x.name + " (" + x.position.value + ", " + str(x.selected_by_percent) + ")" for x in result[0])}')
  print(f'In: {", ".join(x.name + " (" + x.position.value + ", " + str(x.selected_by_percent) + ")" for x in result[1])}')


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
