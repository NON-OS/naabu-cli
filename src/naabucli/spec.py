"""Descrizione di naabu: profili, flag vietati, formato dei risultati."""

from __future__ import annotations

from naabucli.profili import Profilo
from naabucli.risultati import Voce, righe_json

NOME = "naabu"
BINARIO = "naabu"
DESCRIZIONE = "Scansione veloce di porte con scope validato, dry-run di default e audit a catena di hash."
MODO = "host"
PASSA = ("file", "-list")
UNO_EXTRA: tuple[str, ...] = ()  # solo ffuf lavora "un comando per target"
USCITA = "-o"
VERSIONE = ("-version",)
RICONOSCI = "current version"  # testo che il binario vero stampa con {VERSIONE}: distingue da programmi omonimi
INSTALLAZIONE = "Kali/Debian: sudo apt install naabu (tira dentro libpcap). Ovunque con Go: go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest (serve libpcap, es. sudo apt install libpcap-dev)"
SEGRETI: frozenset[str] = frozenset()
GRUPPO = "Host"
NOTA_ATTIVITA = "scansione di porte: attiva, genera traffico verso i target e compare nei log dei firewall."

PROFILI = {
    p.nome: p
    for p in (
        Profilo("base", "Le 100 porte più comuni (default di naabu).", ("-silent",), "basso",
                "Primo colpo d'occhio. Usa la scansione connect, non serve root."),
        Profilo("connect", "Scansione connect esplicita.", ("-s", "c", "-silent"), "basso",
                "Senza privilegi. Completa l'handshake, quindi finisce nei log dei servizi."),
        Profilo("syn", "Scansione SYN.", ("-s", "s", "-silent"), "medio",
                "Più veloce e meno visibile ai servizi. Richiede root.", richiede_root=True),
        Profilo("top1000", "Le 1000 porte più comuni.", ("-top-ports", "1000", "-silent"), "medio",
                "Copertura buona senza passare per tutte le porte."),
        Profilo("web", "Porte tipiche dei servizi web.",
                ("-p", "80,443,8080,8443,3000,5000,8000,8888", "-silent"), "basso",
                "Quando ti interessa solo cosa serve HTTP, prima di passare a httpx."),
        Profilo("completo", "Tutte le 65535 porte.", ("-p", "-", "-silent"), "alto",
                "Su un host solo, quando serve non perdere porte alte e strane. Su molti host è pesante."),
        Profilo("prudente", "1000 porte con limiti di frequenza e verifica.",
                ("-top-ports", "1000", "-s", "c", "-rate", "300", "-c", "25", "-timeout", "1000",
                 "-retries", "1", "-verify", "-silent"), "medio",
                "Il profilo da usare di default su reti di clienti: frequenza bassa, risultati verificati."),
        Profilo("lento", "Come prudente, ancora più piano.",
                ("-top-ports", "1000", "-s", "c", "-rate", "150", "-c", "10", "-timeout", "2000",
                 "-retries", "2", "-verify", "-silent"), "basso",
                "Per reti fragili o link lenti: meno pacchetti al secondo, timeout più larghi."),
        Profilo("jsonl", "1000 porte in JSON.", ("-top-ports", "1000", "-json", "-silent"), "medio",
                "Per elaborare il risultato con altri strumenti.", uscita="jsonl"),
    )
}  # fmt: skip

VIETATI = {
    "host": "i target arrivano dal file validato contro lo scope",
    "list": "i target arrivano dal file validato contro lo scope",
    "l": "i target arrivano dal file validato contro lo scope",
    "o": "l'output lo gestisce naabu-cli",
    "output": "l'output lo gestisce naabu-cli",
    "sa": "scansiona tutti gli IP di un hostname: può uscire dallo scope",
    "scan-all-ips": "scansiona tutti gli IP di un hostname: può uscire dallo scope",
    "nmap-cli": "esegue un comando nmap arbitrario sui risultati",
    "resume": "riprende un lancio che non è passato dal controllo dello scope",
    "passive": "manda gli indirizzi dei target a Shodan, un terzo",
    "nmap": "esegue nmap sui risultati senza altri controlli",
    "up": "l'aggiornamento del programma si fa a parte, non dentro un lancio autorizzato",
    "update": "l'aggiornamento del programma si fa a parte, non dentro un lancio autorizzato",
}

ESEMPI_VIETATI = [
    ["-host", "x"],
    ["-list", "x"],
    ["-sa"],
    ["-nmap-cli", "nmap -sV"],
    ["-o", "x"],
    ["-passive"],
    ["-nmap"],
]
ESEMPI_AMMESSI = [["-rate", "100"], ["-exclude-ports", "53"]]


def voci(testo: str) -> list[Voce]:
    out = []
    for r in righe_json(testo):
        if isinstance(r, dict):
            host = str(r.get("host") or r.get("ip") or "")
            porta = r.get("port", "")
            if host:
                out.append(Voce(f"{host}:{porta}", f"{host}:{porta}", host))
        elif ":" in r:
            host = r.rsplit(":", 1)[0]
            out.append(Voce(r, r, host))
    return out


# -- lingua -------------------------------------------------------------------
# Testi tradotti, generati da l10n/. L'italiano resta quello definito sopra.
_TR_TESTI: dict[str, dict[str, str]] = {
    "en": {
        "descrizione": "Fast port scanning with a validated scope, dry-run by default and a hash-chained audit.",
        "nota_attivita": "port scanning: active, it generates traffic toward the targets and shows up in firewall logs.",
        "installazione": "Kali/Debian: sudo apt install naabu (pulls in libpcap). Anywhere with Go: go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest (needs libpcap, e.g. sudo apt install libpcap-dev)",
        "gruppo": "Host",
    },
    "zh": {
        "descrizione": "快速端口扫描，带作用域校验、默认 dry-run 以及哈希链审计。",
        "nota_attivita": "端口扫描：主动行为，会向目标产生流量，并出现在防火墙日志中。",
        "installazione": "Kali/Debian：sudo apt install naabu（会一并装上 libpcap）。任何装了 Go 的环境：go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest（需要 libpcap，例如 sudo apt install libpcap-dev）",
        "gruppo": "主机",
    },
}
_TR_PROFILI: dict[str, dict[str, list[str]]] = {
    "en": {
        "base": [
            "The 100 most common ports (naabu's default).",
            "First quick look. Uses a connect scan, no root needed.",
        ],
        "connect": [
            "Explicit connect scan.",
            "No privileges. Completes the handshake, so it lands in the services' logs.",
        ],
        "syn": ["SYN scan.", "Faster and less visible to services. Requires root."],
        "top1000": ["The 1000 most common ports.", "Good coverage without going through every port."],
        "web": [
            "Ports typical of web services.",
            "When you only care about what serves HTTP, before moving on to httpx.",
        ],
        "completo": [
            "All 65535 ports.",
            "On a single host, when you can't afford to miss high, odd ports. Heavy across many hosts.",
        ],
        "prudente": [
            "1000 ports with rate limits and verification.",
            "The default profile on client networks: low rate, verified results.",
        ],
        "lento": [
            "Like prudente, even slower.",
            "For fragile networks or slow links: fewer packets per second, wider timeouts.",
        ],
        "jsonl": ["1000 ports in JSON.", "To process the result with other tools."],
    },
    "zh": {
        "base": ["最常见的 100 个端口（naabu 默认）。", "快速初步查看。使用 connect 扫描，无需 root 权限。"],
        "connect": ["显式的 connect 扫描。", "无需特权。会完成握手，因此会留在服务的日志中。"],
        "syn": ["SYN 扫描。", "更快且对服务更隐蔽。需要 root 权限。"],
        "top1000": ["最常见的 1000 个端口。", "覆盖面不错，又无需扫描所有端口。"],
        "web": ["Web 服务常见的端口。", "当你只关心哪些端口提供 HTTP 服务时，在进入 httpx 之前使用。"],
        "completo": ["全部 65535 个端口。", "在单个主机上使用，当需要不遗漏高位和冷门端口时。在大量主机上开销很大。"],
        "prudente": ["1000 个端口，带频率限制和验证。", "在客户网络上默认使用的配置：低频率、结果经过验证。"],
        "lento": ["与 prudente 相同，但更慢。", "用于脆弱的网络或慢速链路：每秒发送更少的数据包，超时更宽松。"],
        "jsonl": ["1000 个端口，以 JSON 输出。", "用于使用其他工具处理结果。"],
    },
}
_TR_VIETATI: dict[str, dict[str, str]] = {
    "en": {
        "esegue nmap sui risultati senza altri controlli": "runs nmap on the results with no further checks",
        "esegue un comando nmap arbitrario sui risultati": "runs an arbitrary nmap command on the results",
        "i target arrivano dal file validato contro lo scope": "targets come from the file validated against the scope",
        "l'aggiornamento del programma si fa a parte, non dentro un lancio autorizzato": "updating the program is done separately, not inside an authorized run",
        "l'output lo gestisce naabu-cli": "output is handled by naabu-cli",
        "manda gli indirizzi dei target a Shodan, un terzo": "sends target addresses to Shodan, a third party",
        "riprende un lancio che non è passato dal controllo dello scope": "resumes a run that didn't go through the scope check",
        "scansiona tutti gli IP di un hostname: può uscire dallo scope": "scans every IP of a hostname: can go out of scope",
    },
    "zh": {
        "esegue nmap sui risultati senza altri controlli": "对结果执行 nmap，且不再做其他检查",
        "esegue un comando nmap arbitrario sui risultati": "对结果执行任意 nmap 命令",
        "i target arrivano dal file validato contro lo scope": "目标来自经过作用域校验的文件",
        "l'aggiornamento del programma si fa a parte, non dentro un lancio autorizzato": "程序更新应单独进行，而不是在一次授权任务中进行",
        "l'output lo gestisce naabu-cli": "输出由 naabu-cli 管理",
        "manda gli indirizzi dei target a Shodan, un terzo": "会把目标地址发送给第三方 Shodan",
        "riprende un lancio che non è passato dal controllo dello scope": "会恢复一次未经过作用域检查的任务",
        "scansiona tutti gli IP di un hostname: può uscire dallo scope": "扫描一个主机名的所有 IP：可能超出作用域",
    },
}
_ORIGINALI = (DESCRIZIONE, NOTA_ATTIVITA, INSTALLAZIONE, GRUPPO, PROFILI, VIETATI)


def applica_lingua(lingua: str) -> None:
    """Passa testi, profili e motivi dei flag vietati alla lingua scelta. Ripartendo
    sempre dagli originali italiani, chiamarla più volte non accumula niente."""
    global DESCRIZIONE, NOTA_ATTIVITA, INSTALLAZIONE, GRUPPO, PROFILI, VIETATI
    from dataclasses import replace

    DESCRIZIONE, NOTA_ATTIVITA, INSTALLAZIONE, GRUPPO, PROFILI, VIETATI = _ORIGINALI
    testi = _TR_TESTI.get(lingua)
    if not testi:
        return
    DESCRIZIONE = testi["descrizione"] or DESCRIZIONE
    NOTA_ATTIVITA = testi["nota_attivita"] or NOTA_ATTIVITA
    INSTALLAZIONE = testi["installazione"] or INSTALLAZIONE
    GRUPPO = testi["gruppo"] or GRUPPO
    prof = _TR_PROFILI.get(lingua, {})
    PROFILI = {
        n: replace(p, descrizione=prof[n][0] or p.descrizione, quando=prof[n][1] or p.quando) if n in prof else p
        for n, p in PROFILI.items()
    }
    viet = _TR_VIETATI.get(lingua, {})
    VIETATI = {k: viet.get(v, v) for k, v in VIETATI.items()}
