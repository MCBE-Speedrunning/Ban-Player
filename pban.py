#!/usr/bin/env python3.9

import json
from itertools import count
from os import makedirs, path
from sys import argv, exit, stderr
from typing import Optional, Literal, NoReturn

import requests

PROG: Literal[str] = path.basename(__file__)
VERSION: Literal[str] = f"{PROG} 1.1.1"

API: Literal[str] = "https://www.speedrun.com/api/v1"
CONFIG: Literal[str] = f"{path.expanduser('~')}/.config/{PROG}/{PROG}rc"
REJECT: Literal[dict[str, dict[str, str]]] = {
	"status": {"status": "rejected", "reason": "Banned player"}
}

HELP: Literal[str] = f"""\
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


def usage() -> NoReturn:
	"""
	Print program usage to stderr and exit.
	"""
	print(
		f"Usage: {PROG} [USER] [GAMES]...\n"
		+ f"Try '{PROG} --help' for more information.",
		file=stderr,
	)
	exit(1)


def getopt(argc: int) -> None:
	"""
	Extremely rudamentary commandline option parser, because I don't need
	anything more complex.
	"""
	for i in range(1, argc):
		if argv[i] == "--help" or argv[i].startswith("-h"):
			print(HELP)
			exit(0)
		if argv[i] == "--version" or argv[i].startswith("-v"):
			print(VERSION)
			exit(0)


def get_apikey() -> str:
	"""
	Get the users speedrun.com API key from the configuration file. If it
	does not exist then prompt the user for a valid API key.
	"""
	try:
		with open(CONFIG, "r") as f:
			return f.read().strip()
	except FileNotFoundError:
		apikey = input("speedrun.com API key: ")
		makedirs(path.dirname(CONFIG))

		with open(CONFIG, "w+") as f:
			f.write(apikey)

		return apikey


def getuid(name: str) -> Optional[str]:
	"""
	Get a users user ID from their username. Returns None on error.

	>>> getuid("1")
	'zx7gd1yx'
	>>> getuid("AnInternetTroll")
	'7j477kvj'
	>>> getuid("Fake Name")
	"""
	r = requests.get(f"{API}/users", params={"lookup": name}).json()
	try:
		return r["data"][0]["id"]
	except IndexError:
		return None


def getgid(abbreviation: str) -> Optional[str]:
	"""
	Get a games game ID from its abbreviation. Returns None on error.

	>>> getgid("mkw")
	'l3dxogdy'
	>>> getgid("celestep8")
	'4d7e7z67'
	>>> getgid("Fake Game")
	"""
	r = requests.get(f"{API}/games", params={"abbreviation": abbreviation}).json()
	try:
		return r["data"][0]["id"]
	except IndexError:
		return None


def reject(apikey: str, uid: str, gid: str) -> None:
	"""
	Reject all runs by user with the id UID from the game with id GID using
	the API key specified by APIKEY. Print any errors to stderr.
	"""
	for offset in count(0, 200):
		r = requests.get(
			f"{API}/runs",
			params={
				"user": uid,
				"game": gid,
				"max": SRC_MAX,
				"offset": offset
			}
		).json()
		if not r["data"]:
			return

		for run in r["data"]:
			rid = run["weblink"].split("/")[-1]
			r = requests.put(
				f"{API}/runs/{rid}/status",
				headers={
					"X-API-Key": apikey,
					"Accept": "application/json",
					"User-Agent": "player-banner/1.0",
				},
				data=json.dumps(REJECT),
			)
			if not r.ok:
				print(json.dumps(json.loads(r.text), indent=4), file=stderr)


def main() -> int:
	argc = len(argv)
	getopt(argc)

	if argc < 3:
		usage()

	uid = getuid(argv[1])
	if not uid:
		print(f"{PROG}: user with name '{argv[1]}' not found", file=stderr)
		return 2

	apikey = get_apikey()

	for i in range(2, argc):
		gid = getgid(argv[i])
		if not gid:
			print(
				f"{PROG}: Game with abbreviation '{argv[i]}' not found.",
				file=stderr,
			)
			return 3

		reject(apikey, uid, gid)

	return 0


if __name__ == "__main__":
	exit(main())
