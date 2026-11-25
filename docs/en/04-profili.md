# Profiles and forbidden flags

🌐 [Italiano](../04-profili.md) · **English** · [中文](../zh/04-profili.md)

| Profile | What it does | Noise | Root |
|---|---|---|---|
| `base` | The 100 most common ports (naabu's default). | low | no |
| `connect` | Explicit connect scan. | low | no |
| `syn` | SYN scan. | medium | yes |
| `top1000` | The 1000 most common ports. | medium | no |
| `web` | Ports typical of web services. | low | no |
| `completo` | All 65535 ports. | high | no |
| `prudente` | 1000 ports with rate limits and verification. | medium | no |
| `lento` | Like prudente, even slower. | low | no |
| `jsonl` | 1000 ports in JSON. | medium | no |

`naabu-cli profili` prints the exact flags of each one.

## What each profile does

**base** (`-silent`). The 100 most common ports (naabu's default). First quick look. Uses a connect scan, no root needed.

**connect** (`-s c -silent`). Explicit connect scan. No privileges. Completes the handshake, so it lands in the services' logs.

**syn** (`-s s -silent`). SYN scan. Faster and less visible to services. Requires root.

**top1000** (`-top-ports 1000 -silent`). The 1000 most common ports. Good coverage without going through every port.

**web** (`-p 80,443,8080,8443,3000,5000,8000,8888 -silent`). Ports typical of web services. When you only care about what serves HTTP, before moving on to httpx.

**completo** (`-p - -silent`). All 65535 ports. On a single host, when you can't afford to miss high, odd ports. Heavy across many hosts.

**prudente** (`-top-ports 1000 -s c -rate 300 -c 25 -timeout 1000 -retries 1 -verify -silent`). 1000 ports with rate limits and verification. The default profile on client networks: low rate, verified results.

**lento** (`-top-ports 1000 -s c -rate 150 -c 10 -timeout 2000 -retries 2 -verify -silent`). Like prudente, even slower. For fragile networks or slow links: fewer packets per second, wider timeouts.

**jsonl** (`-top-ports 1000 -json -silent`). 1000 ports in JSON. To process the result with other tools.

## Passing flags by hand

Everything you write after `--` goes to naabu, after the profile flags, provided it is not on the forbidden list. The check is case-insensitive and accepts both `-flag valore` and `-flag=valore`, with one or two dashes.

```sh
naabu-cli lancia prudente 192.0.2.10 --scope scope.toml -- -timeout 5
```

## Forbidden list

| Flag | Why |
|---|---|
| `-host`, `-list`, `-l` | targets come from the file validated against the scope |
| `-o`, `-output` | output is handled by naabu-cli |
| `-sa`, `-scan-all-ips` | scans every IP of a hostname: can go out of scope |
| `-nmap-cli` | runs an arbitrary nmap command on the results |
| `-resume` | resumes a run that didn't go through the scope check |
| `-passive` | sends target addresses to Shodan, a third party |
| `-nmap` | runs nmap on the results with no further checks |
| `-up`, `-update` | updating the program is done separately, not inside an authorized run |

## What the filter does not do

It is not a sandbox. If you want to get around it you can, for example by calling `naabu` directly. It is there to stop mistakes and bad habits, not an attacker who already has access to your terminal. If you need a forbidden flag for an activity agreed with the client, use naabu directly and record the decision in the engagement.
