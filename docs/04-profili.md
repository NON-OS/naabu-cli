# Profili e flag vietati

🌐 **Italiano** · [English](en/04-profili.md) · [中文](zh/04-profili.md)

| Profilo | Cosa fa | Rumore | Root |
|---|---|---|---|
| `base` | Le 100 porte più comuni (default di naabu). | basso | no |
| `connect` | Scansione connect esplicita. | basso | no |
| `syn` | Scansione SYN. | medio | si |
| `top1000` | Le 1000 porte più comuni. | medio | no |
| `web` | Porte tipiche dei servizi web. | basso | no |
| `completo` | Tutte le 65535 porte. | alto | no |
| `prudente` | 1000 porte con limiti di frequenza e verifica. | medio | no |
| `lento` | Come prudente, ancora più piano. | basso | no |
| `jsonl` | 1000 porte in JSON. | medio | no |

`naabu-cli profili` stampa i flag esatti di ciascuno.

## Cosa fa ciascun profilo

**base** (`-silent`). Le 100 porte più comuni (default di naabu). Primo colpo d'occhio. Usa la scansione connect, non serve root.

**connect** (`-s c -silent`). Scansione connect esplicita. Senza privilegi. Completa l'handshake, quindi finisce nei log dei servizi.

**syn** (`-s s -silent`). Scansione SYN. Più veloce e meno visibile ai servizi. Richiede root.

**top1000** (`-top-ports 1000 -silent`). Le 1000 porte più comuni. Copertura buona senza passare per tutte le porte.

**web** (`-p 80,443,8080,8443,3000,5000,8000,8888 -silent`). Porte tipiche dei servizi web. Quando ti interessa solo cosa serve HTTP, prima di passare a httpx.

**completo** (`-p - -silent`). Tutte le 65535 porte. Su un host solo, quando serve non perdere porte alte e strane. Su molti host è pesante.

**prudente** (`-top-ports 1000 -s c -rate 300 -c 25 -timeout 1000 -retries 1 -verify -silent`). 1000 porte con limiti di frequenza e verifica. Il profilo da usare di default su reti di clienti: frequenza bassa, risultati verificati.

**lento** (`-top-ports 1000 -s c -rate 150 -c 10 -timeout 2000 -retries 2 -verify -silent`). Come prudente, ancora più piano. Per reti fragili o link lenti: meno pacchetti al secondo, timeout più larghi.

**jsonl** (`-top-ports 1000 -json -silent`). 1000 porte in JSON. Per elaborare il risultato con altri strumenti.

## Passare flag a mano

Tutto ciò che scrivi dopo `--` finisce a naabu, dopo i flag del profilo, a patto che non sia nell'elenco dei vietati. Il confronto non distingue maiuscole e minuscole e accetta sia `-flag valore` sia `-flag=valore`, con uno o due trattini.

```sh
naabu-cli lancia prudente 192.0.2.10 --scope scope.toml -- -timeout 5
```

## Elenco dei vietati

| Flag | Perché |
|---|---|
| `-host`, `-list`, `-l` | i target arrivano dal file validato contro lo scope |
| `-o`, `-output` | l'output lo gestisce naabu-cli |
| `-sa`, `-scan-all-ips` | scansiona tutti gli IP di un hostname: può uscire dallo scope |
| `-nmap-cli` | esegue un comando nmap arbitrario sui risultati |
| `-resume` | riprende un lancio che non è passato dal controllo dello scope |
| `-passive` | manda gli indirizzi dei target a Shodan, un terzo |
| `-nmap` | esegue nmap sui risultati senza altri controlli |
| `-up`, `-update` | l'aggiornamento del programma si fa a parte, non dentro un lancio autorizzato |

## Quello che il filtro non fa

Non è una sandbox. Se vuoi aggirarlo ci riesci, per esempio chiamando `naabu` direttamente. Serve a fermare gli errori e le abitudini sbagliate, non un malintenzionato che ha già accesso al tuo terminale. Se ti serve un flag vietato per un'attività concordata con il cliente, usa naabu direttamente e annota la scelta nell'ingaggio.
