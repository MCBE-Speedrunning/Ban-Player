#!/usr/bin/env python3

import json
from sys import argv

import requests

API = "https://www.speedrun.com/api/v1"
REJECT = {"status": {"status": "rejected", "reason": "Banned player"}}
with open("apikey", "r") as f:
	KEY = f.read().strip()

r = requests.get(f"{API}/users?lookup={argv[1]}").json()
uid = r["data"][0]["id"]

r = requests.get(f"{API}/runs?user={uid}&max=200").json()
for run in r["data"]:
	if run["game"] in ("yd4ovvg1", "v1po7r76"):
		rid = run["weblink"].split("/")[-1]
		r = requests.put(
			f"https://www.speedrun.com/api/v1/runs/{rid}/status",
			headers={
				"X-API-Key": KEY,
				"Accept": "application/json",
				"User-Agent": "player-banner/1.0",
			},
			data=json.dumps(REJECT),
		)
		if r.status_code not in (200, 204):
			print(json.dumps(json.loads(r.text), indent=4))
