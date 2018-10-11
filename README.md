# tpn-generation

Modified version of a tpn-generator that [Brett Cannon](https://github.com/brettcannon/) wrote for [vscode-python](https://github.com/Microsoft/vscode-python).

## Usage
1. Install dependencies however you'd like. I use `pipenv`:
```
pipenv install
```
2. Call the tpn generator from cli
```
pipenv run python -m tpn
Usage: tpn [--npm=<package-lock.json>] [--pypi=<requirements.txt>] --config=<TPN.toml> <tpn_path>
```
