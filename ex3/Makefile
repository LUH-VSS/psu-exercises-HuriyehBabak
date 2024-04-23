.PHONY: test

test:
	python3 -m unittest -v
eps:
	python3 -m unittest test.test_parser_analysis.TestLL1Analysis.test_eps -v
first:
	python3 -m unittest test.test_parser_analysis.TestLL1Analysis.test_first -v 
follow:
	python3 -m unittest test.test_parser_analysis.TestLL1Analysis.test_follow -v
predict:
	python3 -m unittest test.test_parser_analysis.TestLL1Analysis.test_predict -v

# requires mypy (pip3 install -U mypy) [use pip on Windows]
typecheck:
	mypy parserll1/analysis.py

# requires ruff (pip3 install -U ruff) [use pip on Windows]
format:
	ruff format
