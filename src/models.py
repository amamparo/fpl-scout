from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Position(Enum):
  GKP = 'GKP'
  DEF = 'DEF'
  MID = 'MID'
  FWD = 'FWD'


@dataclass
class Player:
  id: int
  name: str
  team: str
  next_opponent: str
  position: Position
  buy_price: float
  sell_price: Optional[float]
  next_fixture_quality: float
  upcoming_fixtures_quality: float
  availability: float
  selected_by_percent: float
  quality: Optional[float]
  is_owned: bool = False
