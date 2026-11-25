#!/usr/bin/env bash
# naabu_workflow_v2.sh
# Riferimento operativo completo. Solo target autorizzati.

INPUT_LIST="<FILE_CON_HOST>"
TARGET="<HOST_O_IP>"
OUT="<PREFISSO_OUTPUT>"

# ---------------------------------------------------------------
# Prerequisiti
# Default scan-type = CONNECT ("c"). NON serve root.
# SYN ("s") richiede root e NET_RAW. Se non hai privilegi,
# CONNECT è il default e funziona comunque .
# ---------------------------------------------------------------
naabu -version

# ---------------------------------------------------------------
# Scansione base
# Default: top 100 porte, CONNECT, rate 1000 pps, timeout 700ms.
# ---------------------------------------------------------------

# Host singolo.
naabu -host "$TARGET" -silent

# Lista di host.
naabu -list "$INPUT_LIST" -silent -o "$OUT.base.txt"

# ---------------------------------------------------------------
# Scan type: CONNECT (default) vs SYN
# -s c (CONNECT): default. Nessun privilegio. Completa l'handshake.
# -s s (SYN): richiede root. Più veloce, half-open.
# La documentazione ufficiale elenca default "c" .
# ---------------------------------------------------------------

# CONNECT esplicito (default, no root).
naabu -list "$INPUT_LIST" -s c -silent -o "$OUT.connect.txt"

# SYN (solo con root).
sudo naabu -list "$INPUT_LIST" -s s -silent -o "$OUT.syn.txt"

# ---------------------------------------------------------------
# Port selection
# Default: top 100. -top-ports 1000 per più copertura.
# -p - per full 1-65535 (lento, solo su host interessanti) .
# ---------------------------------------------------------------

naabu -list "$INPUT_LIST" -top-ports 1000 -silent -o "$OUT.top1000.txt"
naabu -host "$TARGET" -p - -silent -o "$OUT.full.txt"
naabu -list "$INPUT_LIST" -p 80,443,8080,8443,3000,5000,8000,8888 -silent -o "$OUT.web.txt"

# Escludi porte specifiche.
naabu -list "$INPUT_LIST" -top-ports 1000 -exclude-ports 9100,53 -silent -o "$OUT.excluded.txt"

# ---------------------------------------------------------------
# CDN exclusion (-exclude-cdn / -ec)
# Su host dietro CDN/WAF, NON salta lo scan: scansiona SOLO
# 80 e 443. Il resto viene ignorato .
# -display-cdn (-cdn) mostra il CDN in uso.
# ---------------------------------------------------------------
naabu -list "$INPUT_LIST" -top-ports 1000 -exclude-cdn -silent -o "$OUT.no_cdn.txt"
naabu -list "$INPUT_LIST" -display-cdn -silent -o "$OUT.cdn_info.txt"

# ---------------------------------------------------------------
# Rate limiting e performance
# -rate: pacchetti/sec (default 1000). Abbassa su produzione.
# -c: worker threads (default 25) .
# -timeout: MILLISECONDI. Default 700ms. Non mettere 10 .
# -retries: tentativi (default 1) .
# ---------------------------------------------------------------

# Conservativo per produzione.
naabu -list "$INPUT_LIST" -top-ports 1000 \
  -s c -rate 300 -c 25 -timeout 1000 -retries 1 -verify \
  -silent -o "$OUT.safe.txt"

# Se perdi porte, abbassa rate e alza timeout.
naabu -list "$INPUT_LIST" -top-ports 1000 \
  -s c -rate 150 -c 10 -timeout 2000 -retries 2 -verify \
  -silent -o "$OUT.slow.txt"

# ---------------------------------------------------------------
# Verify (-verify)
# Ri-conferma le porte scoperte prima di riportarle.
# Riduce i falsi positivi. Consigliato prima di httpx .
# ---------------------------------------------------------------
naabu -list "$INPUT_LIST" -top-ports 1000 -verify -silent -o "$OUT.verified.txt"

# ---------------------------------------------------------------
# Output
# -json: JSONL per pipeline. -oX: XML compatibile Nmap.
# -oG: greppable compatibile Nmap. -oA: tutti i formati .
# ---------------------------------------------------------------

naabu -list "$INPUT_LIST" -top-ports 1000 -json -silent -o "$OUT.jsonl"
naabu -list "$INPUT_LIST" -top-ports 1000 -oX "$OUT.xml"
naabu -list "$INPUT_LIST" -top-ports 1000 -oA "$OUT.all"

# ---------------------------------------------------------------
# Integrazione con Nmap (-nmap-cli)
# Passa i risultati direttamente a Nmap per service detection.
# Questo è il punto di integrazione reale, non solo la
# compatibilità XML .
# ---------------------------------------------------------------
# naabu -list "$INPUT_LIST" -top-ports 1000 -nmap-cli 'nmap -sV -oX nmap-out.xml'

# ---------------------------------------------------------------
# Pipeline: subfinder → dnsx → naabu → httpx → nuclei
# ---------------------------------------------------------------

subfinder -d "$DOMAIN" -all -silent -o /tmp/subs.txt
dnsx -l /tmp/subs.txt -a -re -silent -o /tmp/resolved.txt

if command -v naabu &>/dev/null; then
    naabu -list /tmp/resolved.txt -top-ports 1000 \
      -s c -rate 300 -timeout 1000 -retries 1 -verify \
      -silent -o /tmp/naabu_ports.txt
else
    echo "naabu non installato. Pipeline fermata."
    exit 1
fi

if command -v httpx &>/dev/null; then
    cat /tmp/naabu_ports.txt | httpx -silent -sc -title -td -mc 200,401,403 -o /tmp/live_hosts.txt
else
    echo "httpx non installato. Pipeline fermata."
    exit 1
fi

if command -v nuclei &>/dev/null; then
    nuclei -l /tmp/live_hosts.txt -severity critical,high -exclude-tags intrusive,dos -jsonl -o /tmp/nuclei_findings.jsonl
else
    echo "nuclei non installato. Pipeline fermata a live_hosts.txt."
fi

# ---------------------------------------------------------------
# Comando di produzione completo
# Top 1000, CONNECT (no root), rate limitato, verify,
# CDN exclusion, output JSONL.
# ---------------------------------------------------------------
naabu -list "$INPUT_LIST" \
  -top-ports 1000 \
  -s c \
  -exclude-cdn \
  -rate 300 -c 25 -timeout 1000 -retries 1 \
  -verify \
  -silent -json -o "$OUT.jsonl"
