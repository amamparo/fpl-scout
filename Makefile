environment:
	rm -rf Pipfile.lock
	PIPENV_VENV_IN_PROJECT=1 pipenv install -d

test:
	pipenv run python -m unittest src -v

generate_initial_squad:
	pipenv run python -m src.generate_initial_squad

optimize_lineup:
	pipenv run python -m src.optimize_lineup
