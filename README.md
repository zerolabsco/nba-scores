# NBA

NBA is a simple Python package that provides you with a quick and easy
command-line interface to current NBA scores and standings.

See the [Installation](#installation) & [Usage](#usage) sections below
for more information.

# Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)

# Installation

[Back to top](#table-of-contents)

## PyPi

```shell
pipx install nba-scores
```

## Manual

To run the script locally, run the following commands:

```shell
git clone https://git.cleberg.net/nba-scores.git
cd nba-scores
pipx install .
```

![Installation](./screenshots/installation.png)

# Usage

[Back to top](#table-of-contents)

All commands can be passed to the program with the following template:
`nba <ARGUMENT>`

| Argument      | Shortcut | Description                       |
|---------------|----------|-----------------------------------|
| `--scores`    | `-sc`    | Show today's scoreboard           |
| `--standings` | `-st`    | Show current conference standings |

Scores:
![Scores](./screenshots/scores.png)

Standings:
![Standings](./screenshots/standings.png)

# Contributing

[Back to top](#table-of-contents)

Any and all contributions are welcome. Feel free to fork the project,
add features, and submit a pull request.
