# Tor Browser Guide

## What Tor is
Tor routes your traffic through **3 encrypted hops** (volunteer relays worldwide) — websites see the exit node's IP, not yours. Plus `.onion` hidden services.

## Safety rules — READ THIS
- ⚠️ Tor hides your **location/network**, NOT your identity. Logging into Facebook/Gmail over Tor links that account to the session.
- ⚠️ Always keep **HTTPS** on (padlock) — Tor encrypts between hops, HTTPS encrypts end-to-end.
- ⚠️ Don't download files or enable scripts carelessly — same malware risks as normal browsing.
- ✅ Good uses: reading news freely, research, journalism, privacy-sensitive browsing, .onion sites.

## Basics
1. Launch **Tor Browser** (Start Menu) — it connects automatically (~10s)
2. Browse normally — every site goes through Tor
3. Check connection: toolbar shows "Tor circuit" info

## Censored networks?
If Tor is blocked, use **bridges**: hamburger menu → Connection Settings → "Add a bridge" → request one from torproject.org or use built-in obfs4 bridges.

## Tor vs VPN
| | Tor | VPN |
|---|---|---|
| Trust model | distributed volunteers | one company |
| Speed | slower (3 hops) | faster |
| Best for | anonymity | privacy + speed |

## Legal note
Using Tor is legal in most countries (journalists, researchers use it daily) — but a few countries restrict it. You're responsible for local laws.
