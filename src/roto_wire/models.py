from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class ProjectionType(Enum):
	SEASON = 'season'
	WEEKLY = 'weekly'


@dataclass
class Projection:
	type: ProjectionType
	id: int = 0
	name: str = ''
	team: str = ''
	positions: List[str] = field(default_factory=lambda: [])
	minutes: float = 0
	goals: float = 0
	assists: float = 0
	clean_sheets: float = 0
	saves: float = 0
	goals_conceded: float = 0
	yellow_cards: float = 0
	red_cards: float = 0
	opponent: Optional[str] = None

	def __hash__(self) -> int:
		return self.id

	def __eq__(self, o: 'Projection') -> bool:
		return self.id == o.id
