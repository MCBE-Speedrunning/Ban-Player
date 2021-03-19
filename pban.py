#!/usr/bin/env python3.9

import json
from itertools import count
from os import makedirs, path
from os.path import basename, expanduser
from sys import argv, exit, stderr
from typing import Union

import requests

PROG: str = basename(__file__)

API: str = "https://www.speedrun.com/api/v1"
CONFIG: str = f"{expanduser('~')}/.config/{PROG}/{PROG}rc"
REJECT: dict[str, dict[str, str]] = {
	"status": {"status": "rejected", "reason": "Banned player"}
}

VERSION: str = f"{PROG} 1.1.0"
HELP: str = f"""\
Usage: {PROG} [OPTION]... [USER] [GAMES]...
Ban a USER from a list of GAMES by rejecting all of their existing runs.
Example: {PROG} AnInternetTroll mcbe mcbece celestep8

Miscellaneous:
  -h, --help                display this help text and exit
  -v, --version             display version information and exit

The usage of this program requires that you have a speedrun.com API key. When
first using the program, you will be prompted to enter your API key. After this
the key will be saved in the file located at '~/.config/{PROG}/{PROG}rc'. Future
calls to this program will read the API key from the {PROG}rc file.

Exit status:
 0  if OK,
 1  if incorrect program usage,
 2  if USER cannot be found,
 3  if GAME cannot be found.
"""


def usage() -> None:
	print(
		f"Usage: {PROG} [USER] [GAMES]...\n" + f"Try '{PROG} --help' for more information.",
		file=stderr,
	)
	exit(1)


def getopt(AC: int) -> None:
	"""
	Extremely rudamentary commandline option parser, because I don't need
	anything more complex.
	"""
	for i in range(1, AC):
		if argv[i] == "--help" or argv[i] == "-h":
			print(HELP)
			exit(0)
		if argv[i] == "--version" or argv[i] == "-v":
			print(VERSION)
			exit(0)


def apikey() -> str:
	try:
		with open(CONFIG, "r") as f:
			return f.read().strip()
	except FileNotFoundError:
		APIKEY: str = input("speedrun.com API key: ")
		makedirs(path.join(expanduser("~"), ".config", "{PROG}"))
		with open(CONFIG, "w+") as f:
			f.write(APIKEY)

		return APIKEY


def getuid(NAME: str) -> Union[str, None]:
	"""
	Get a users user ID from their username. Returns None on error.
	>>> getuid("1")
	'zx7gd1yx'
	>>> getuid("AnInternetTroll")
	'7j477kvj'
	>>> getuid("Fake Name")
	"""
	R: dict = requests.get(f"{API}/users?lookup={NAME}").json()
	try:
		return R["data"][0]["id"]
	except IndexError:
		return None


def getgid(ABRV: str) -> Union[str, None]:
	"""
	Get a games game ID from its abbreviation. Returns None on error.
	>>> getgid("mkw")
	'l3dxogdy'
	>>> getgid("celestep8")
	'4d7e7z67'
	>>> getgid("Fake Game")
	"""
	R: dict = requests.get(f"{API}/games?abbreviation={ABRV}").json()
	try:
		return R["data"][0]["id"]
	except IndexError:
		return None


def reject(APIKEY: str, UID: str, GID: str) -> None:
	for offset in count(0, 200):
		r: dict = requests.get(
			f"{API}/runs?user={UID}&game={GID}&max=200&offset={offset}"
		).json()
		for run in r["data"]:
			rid: str = run["weblink"].split("/")[-1]
			r = requests.put(
				f"{API}/runs/{rid}/status",
				headers={
					"X-API-Key": APIKEY,
					"Accept": "application/json",
					"User-Agent": "player-banner/1.0",
				},
				data=json.dumps(REJECT),
			)
			if r.status_code not in (200, 204):
				print(json.dumps(json.loads(r.text), indent=4), file=stderr)


def main() -> int:
	AC: int = len(argv)
	getopt(AC)

	if AC < 3:
		usage()

	UID: str = getuid(argv[1])
	if not UID:
		print(f"{PROG}: user with name '{argv[1]}' not found", file=stderr)
		return 2

	APIKEY: str = apikey()

	for i in range(2, AC):
		gid: str = getgid(argv[1])
		if not gid:
			print(
				f"{PROG}: game with abbreviation '{argv[i]}' not found",
				file=stderr,
			)
			return 3

		reject(APIKEY, UID, gid)

	return 0


if __name__ == "__main__":
	RET: int = main()
	exit(RET)
