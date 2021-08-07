from injector import inject

from src.dependency_injection import run
from src.models import Squad, Position
from src.optimizer import Optimizer
from src.player_service import AbstractPlayerService
from src.roto_wire.models import ProjectionType


@inject
def main(player_service: AbstractPlayerService):
	players = player_service.get_players(ProjectionType.SEASON)
	optimizer = Optimizer(players)
	optimizer.set_budget_constraint(1000)
	optimizer.set_position_constraint(Position.GKP, minimum=2, maximum=2)
	optimizer.set_position_constraint(Position.DEF, minimum=5, maximum=5)
	optimizer.set_position_constraint(Position.MID, minimum=5, maximum=5)
	optimizer.set_position_constraint(Position.FWD, minimum=3, maximum=3)
	optimizer.set_team_constraints()
	print(Squad(optimizer.solve()))


if __name__ == '__main__':
	run(main)
