from typing import Callable

from injector import Binder, singleton, Injector

from src.env import AbstractEnvironment, Environment
from src.fpl.fpl_repository import AbstractFplRepository, FplRepository
from src.roto_wire.roto_wire_repository import AbstractRotoWireRepository, RotoWireRepository
from src.player_service import AbstractPlayerService, PlayerService


def __configure(binder: Binder) -> None:
	binder.bind(AbstractEnvironment, to=Environment, scope=singleton)
	binder.bind(AbstractRotoWireRepository, to=RotoWireRepository, scope=singleton)
	binder.bind(AbstractFplRepository, to=FplRepository, scope=singleton)
	binder.bind(AbstractPlayerService, to=PlayerService, scope=singleton)


def run(_callable: Callable[..., None]) -> None:
	Injector(__configure).call_with_injection(_callable)
