from abc import ABC, abstractmethod

from dotenv import load_dotenv
from os import environ

load_dotenv()


class AbstractEnvironment(ABC):
	@abstractmethod
	def get_rotowire_username(self) -> str:
		pass

	@abstractmethod
	def get_rotowire_password(self) -> str:
		pass

	@abstractmethod
	def get_fpl_email(self) -> str:
		pass

	@abstractmethod
	def get_fpl_password(self) -> str:
		pass


class Environment(AbstractEnvironment):
	def get_rotowire_username(self) -> str:
		return environ.get('ROTOWIRE_USERNAME')

	def get_rotowire_password(self) -> str:
		return environ.get('ROTOWIRE_PASSWORD')

	def get_fpl_email(self) -> str:
		return environ.get('FPL_EMAIL')

	def get_fpl_password(self) -> str:
		return environ.get('FPL_PASSWORD')
