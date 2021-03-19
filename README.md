# Player Banner

`pban` is a simple commandline utility to automatically reject all runs from a
speedrun.com user to a particular set of leaderboards. In order to reject a
players runs from a leaderboard, you will require the speedrun.com API key of a
moderator for said leaderboard.

You can get your API key here: https://www.speedrun.com/api/auth

## Installation

Installation is easy, just run

```sh
sudo make install
```

Thats it!

## Usage

Using the program is easy. Simply give the users name followed by the
abbreviations of the leaderboards to remove their runs from.

For example, to remove all runs by "AnInternetTroll" from
https://www.speedrun.com/mcbe and https://www.speedrun.com/celestep8 simply run
the following:

```sh
$ pban AnInternetTroll mcbe celestep8
$
```

If you see no output, that means the program terminated successfully. If
something went wrong, the response will be output to the terminal.
