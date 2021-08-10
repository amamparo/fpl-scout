install:
	rm -rf Pipfile.lock
	pipenv install -d

test:
	pipenv run python -m unittest src -v

initial_squad:
	pipenv run python -m src.generate_initial_squad

optimal_lineup:
	pipenv run python -m src.optimize_lineup
