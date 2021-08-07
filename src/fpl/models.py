from dataclasses import dataclass
from typing import Optional

from src.models import Position


@dataclass
class FplPlayer:
	id: int
	name: str
	team: str
	position: Position
	ask: int
	is_in_squad: bool
	bid: Optional[int] = None

	def __hash__(self) -> int:
		return self.id

	def __eq__(self, o: 'FplPlayer') -> bool:
		return self.id == o.id
