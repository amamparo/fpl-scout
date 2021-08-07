# fpl-scout

## What is this?

This is a Fantasy Premier League squad optimizer which uses [RotoWire projections](https://www.rotowire.com/soccer/projections.php?type=season) and [linear programming](https://en.wikipedia.org/wiki/Linear_programming) to help me draft an optimal initial squad, set my weekly lineups, and (soon) discover beneficial transfer targets.


## Requirements
- [Python 3.8.6](https://www.python.org/downloads/release/python-386/)
- [pipenv](https://pypi.org/project/pipenv/)
- A registered [Fantasy Premier League](https://fantasy.premierleague.com) team
- A [RotoWire subscription](https://www.rotowire.com/subscribe/create-account.php) with access to their soccer fantasy projections package
- The following environment variables (ideally set in a `.env` file in this project's root directory):
  - `FPL_EMAIL`
  - `FPL_PASSWORD`
  - `ROTOWIRE_USERNAME`
  - `ROTOWIRE_PASSWORD`


## Setting up
Just install the dependencies by running `pipenv install`


## Running locally
All available actions are laid out in the [Makefile](/Makefile)

| Command | Action |
| --- | --- |
| `make initial_squad` | Generate an optimal initial squad |
| `make optimal_lineup` | Select the optimal starting lineup from an existing squad |

If you're using [PyCharm](https://www.jetbrains.com/pycharm/), these commands are also saved as executable run configurations inside of [/.run](/.run).


## TODO
- Create command to find beneficial transfers


## Resources / Works Cited
- [Linear programming](https://en.wikipedia.org/wiki/Linear_programming) (Wikipedia)
- [Using Python and Linear Programming to Optimize Fantasy Football Picks](https://medium.com/ml-everything/using-python-and-linear-programming-to-optimize-fantasy-football-picks-dc9d1229db81) (Medium)
