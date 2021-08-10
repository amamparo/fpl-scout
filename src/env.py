from dotenv import load_dotenv
from os import environ

from injector import singleton

load_dotenv()


@singleton
class Environment:
  @staticmethod
  def get_fpl_email() -> str:
    return environ.get('FPL_EMAIL')

  @staticmethod
  def get_fpl_password() -> str:
    return environ.get('FPL_PASSWORD')
