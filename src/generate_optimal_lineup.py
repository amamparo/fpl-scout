from injector import inject

from src.dependency_injection import run
from src.models import Lineup, Position
from src.optimizer import Optimizer
from src.player_service import AbstractPlayerService
from src.roto_wire.models import ProjectionType


@inject
def main(player_service: AbstractPlayerService):
	players = player_service.get_players(ProjectionType.WEEKLY)
	squad = [x for x in players if x.is_in_squad]
	optimizer = Optimizer(squad)
	optimizer.set_position_constraint(Position.GKP, minimum=1, maximum=1)
	optimizer.set_position_constraint(Position.DEF, minimum=3)
	optimizer.set_position_constraint(Position.FWD, minimum=1)
	optimizer.set_result_size_constraint(11)
	starters = optimizer.solve()
	sorted_starters = sorted(starters, key=lambda x: x.projection, reverse=True)
	lineup = Lineup(
		starters=starters,
		bench=[x for x in squad if x not in starters],
		captain=sorted_starters[0],
		vice_captain=sorted_starters[1]
	)
	print(lineup)


if __name__ == '__main__':
	run(main)
