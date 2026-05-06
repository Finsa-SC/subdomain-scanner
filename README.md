# subdomain-validator

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python&logoColor=white)
![uv](https://img.shields.io/badge/env-uv-purple?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Security](https://img.shields.io/badge/Use-Ethical%20Only-red?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)

**A lightweight yet powerful CLI tool for subdomain enumeration, HTTP/HTTPS validation, and honeypot detection.**

</div>

---

> [!WARNING]
> **Recon Type: Hybrid (Passive + Active)**
> Subdomain *discovery* is done passively via external APIs — no direct contact with the target.
> The *validation* phase sends real HTTP/HTTPS requests to each discovered subdomain, meaning your traffic **will be logged** by the target and may trigger IDS/WAF alerts.
> **Only use this tool on domains you own or have explicit written permission to test.**

---

## ✨ Features

- **Multi-source subdomain discovery** — HackerTarget, crt.sh, RapidDNS, AlienVault OTX
- **Source selection** — pick a specific source (`-s`) or run all at once (`-all`)
- **Flexible input** — domain (`-d`), file (`-dL`), or **stdin/pipe** support
- **Dual protocol validation** — HTTP and HTTPS simultaneously, with IP resolution, Server header detection, and latency measurement
- **Wildcard DNS detection** — skip false positives (`-w`)
- **Response size filtering** — filter by min/max response size (`--min-size`, `--max-size`)
- **Custom DNS resolver** — use Cloudflare, Google, Quad9, OpenDNS, or a custom IP (`--dns`)
- **🍯 Honeypot Analyzer** — smart fingerprinting to detect traps and fake services (`--honeypot`)
  - Checks server signatures, body hashes, header anomalies, and behavioral patterns
  - Confidence scoring with tiered signal weighting (Critical / Strong / Weak)
  - Visual score bar with labels: Confirmed / Likely / Probable / Possible / Unlikely
- **Aggressive mode** — enable all informative flags in one shot (`-a`)
- **Filter live hosts only** (`-A`)
- **Verbose mode** with redirect info (`-v`, `-r`)
- **Quiet mode** for clean output (`-q`) — optionally show IPs instead of subdomains (`--ip`)
- **Page title extraction** per subdomain (`-t`)
- **Technology detection** from response headers (`-x`)
- **Configurable request delay** between threads (`--delay`)
- **Automatic Cloudflare IP filtering** on saved results
- **Save results** as plain IP list (`-o`) or detailed JSON (`-oJ`)
  - JSON output groups findings into: unique active, honeypots, wildcards, others
- **Scan summary** at the end — OK, Forbidden, SSL Error, Server Error, No Response
- **Concurrent validation** via ThreadPoolExecutor (configurable via `--thread`)
- **Full CLI support** via `argparse` — no interactive prompts
- **Default configuration** via `.env`

---

## 📋 Requirements

- Python 3.10+
- [uv](https://github.com/astral-sh/uv)

---

## 🚀 Getting Started

```bash
# Clone
git clone --depth 1 https://github.com/Finsa-SC/subdomain-validator.git
cd subdomain-validator

# Create virtual environment
uv venv --python 3.10
source .venv/bin/activate        # Linux / macOS
.venv\Scripts\activate           # Windows

# Install dependencies
uv sync

# (Optional) Configure defaults
cp .env.example .env
```

---

## 📖 Usage

```bash
python app/main.py [-h] [-V] (-d DOMAIN | -dL FILE) [options]
```

Or using pipe/stdin:
```bash
cat hosts.txt | python app/main.py
```

---

## 🚩 Flags

### Input Arguments

| Flag | Long | Description |
|------|------|-------------|
| `-d` | `--domain` | Target domain to enumerate |
| `-dL` | `--domain-list` | Path to file containing subdomains to validate |
| `-s` | `--source` | Select a specific discovery source (`hackertarget`, `crtsh`, `rapiddns`, `alienvault`) |
| `-all` | | Use all available discovery sources |

### Configuration

| Flag | Long | Description |
|------|------|-------------|
| | `--timeout` | Request timeout in seconds *(default: from `.env` or `3.0`)* |
| | `--thread` | Number of concurrent threads *(default: from `.env` or `5`)* |
| | `--delay` | Delay between requests in seconds *(default: `0.0`)* |
| | `--dns` | Custom DNS resolver: `cloudflare`, `google`, `quad9`, `opendns`, or a raw IP |

### Profiling & Analysis

| Flag | Long | Description |
|------|------|-------------|
| `-v` | `--verbose` | Show detailed protocol and header information |
| `-t` | `--title` | Print page title below each subdomain |
| `-x` | `--header-tech` | Show technology stack detected from response headers |
| `-r` | `--redirect` | Show redirect targets *(requires `-v`)* |
| `--honeypot` | | Enable smart honeypot fingerprinting |
| `-a` | `--aggressive` | Enable all informative flags (`-v`, `-t`, `-x`, `-r`, `--honeypot`) |

### Output Filtering

| Flag | Long | Description |
|------|------|-------------|
| `-A` | `--available` | Only show hosts with status `200 OK` |
| `-w` | `--no-wildcard` | Skip subdomains detected as wildcard DNS |
| `-q` | `--quiet` | Clean output — only show subdomains with 200 status |
| `--ip` | | Show IPs instead of subdomains *(requires `-q`)* |
| `--color` | | Colorize output text |
| | `--min-size` | Filter out responses smaller than N bytes |
| | `--max-size` | Filter out responses larger than N bytes |

### Export Options

| Flag | Long | Description |
|------|------|-------------|
| `-o` | `--output` | Save results as plain IP list |
| `-oJ` | `--output-json` | Save results as structured JSON with full details |

> `-d` and `-dL` are mutually exclusive. `-r` requires `-v`. `--ip` requires `-q`.

---

## 💡 Examples

```bash
# Basic scan
python app/main.py -d example.com

# Use all discovery sources
python app/main.py -d example.com -all

# Use a specific source
python app/main.py -d example.com -s crtsh

# Only show live hosts (HTTP 200)
python app/main.py -d example.com -A

# Verbose with redirect info
python app/main.py -d example.com -v -r

# Clean output with page titles and tech detection
python app/main.py -d example.com -q -t -x

# Enable honeypot detection
python app/main.py -d example.com --honeypot

# Full aggressive mode (all analysis flags at once)
python app/main.py -d example.com -a

# Use custom DNS resolver
python app/main.py -d example.com --dns cloudflare
python app/main.py -d example.com --dns 1.1.1.1

# Filter by response size (min 500 bytes, max 1MB)
python app/main.py -d example.com --min-size 500 --max-size 1000000

# Scan from file, custom timeout and threads
python app/main.py -dL hosts.txt --timeout 5.0 --thread 20

# Pipe input from another tool
cat hosts.txt | python app/main.py

# Skip wildcard DNS + save as JSON
python app/main.py -d example.com -w -oJ

# Slow scan with delay between requests
python app/main.py -d example.com --delay 0.5 --thread 5

# Full combo
python app/main.py -dL hosts.txt -A -w -a -o -oJ --thread 20 --timeout 5
```

---

## 🖥️ Example Output

```
[*] sub.example.com      | 93.184.216.34   | Apache          | HTTP: 200 (250ms)  | HTTPS: 200 (310ms)  [ (OK) ]
        |_title: [Example Domain]
        |_Tech      : Apache/2.4.41
[!] admin.example.com    | 93.184.216.35   | nginx           | HTTP: 403 (80ms)   | HTTPS: 403 (90ms)   [ [!Forbidden] ]
        |_Honeypot: ████░░░░░░ 42.5% [Probable]
        |_[ Findings: High-value bait subdomain: 'admin', HTTP 200 but no page title ]
[-] old.example.com      | 93.184.216.36   | Unknown         | HTTP: 404 (120ms)  | HTTPS: -   (N/A)


Summary:
Host Up      : 1
Forbidden    : 1
SSL Error    : 0
Server Error : 0
No Response  : 0
```

### Output Prefixes

| Prefix | Meaning |
|--------|---------|
| `[*]` | Host is alive and accessible (200 OK) |
| `[!]` | Host exists but access is denied (403 Forbidden) |
| `[?]` | Possible wildcard DNS match |
| `[-]` | Host found with another status code |

---

## 🍯 Honeypot Analyzer

The `--honeypot` flag enables a multi-signal fingerprinting engine designed to detect deception infrastructure (honeypots, canary traps, fake services).

### How It Works

Signals are grouped into tiers and combined using a **Noisy-OR** probability model:

| Tier | Signals |
|------|---------|
| **Critical** | Known honeypot server signature, honeypot body hash match, literal honeypot headers (`x-honeypot`, `x-canary`, etc.), Cloudflare IP leak |
| **Strong** | Obsolete server version, suspicious header ordering, identical body on HTTP & HTTPS, default server page titles |
| **Weak** | High-value bait subdomain name (`admin`, `vpn`, `db`, etc.), missing page title on 200 response |

### Confidence Labels

| Score | Label |
|-------|-------|
| ≥ 90% | Confirmed |
| ≥ 75% | Likely |
| ≥ 50% | Probable |
| ≥ 25% | Possible |
| < 25% | Unlikely |

---

## 🔍 Discovery Sources

| Source | Flag | Notes |
|--------|------|-------|
| HackerTarget | `hackertarget` | Default source. Free, no API key required. |
| crt.sh | `crtsh` | Certificate transparency logs. No API key required. |
| RapidDNS | `rapiddns` | Scrapes subdomain data from rapiddns.io. |
| AlienVault OTX | `alienvault` | Passive DNS data. Requires an API key. |

Use `-s <source>` to pick one, or `-all` to run all sources and merge results.

---

## 📄 File Input Format (`-dL`)

The format is flexible — the tool reads the **first value per line** (split by `,`). HackerTarget-style output works out of the box, but so does a plain subdomain list:

```
# HackerTarget format (works)
sub.example.com,93.184.216.34

# Plain list (also works)
sub.example.com
admin.example.com
```

---

## ⚙️ Environment Variables

Configurable via `.env` (copy from `.env.example`). CLI flags will **override** these at runtime.

| Variable | Default | Description |
|----------|---------|-------------|
| `TIMEOUT` | `3.0` | HTTP request timeout in seconds |
| `THREAD` | `5` | Number of concurrent threads |
| `DELAY` | `0.0` | Delay between requests in seconds |
| `DEBUG` | `False` | When `True`, skips CLI and runs directly against `hosts.txt` |

---

## 💾 Output Files

Results are saved in the `results/` directory. Cloudflare IPs are automatically filtered from all saved output.

| File | Contents |
|------|----------|
| `results/<domain>_healthy_ip.txt` | IPs that returned 200 OK |
| `results/<domain>_problem_ip.txt` | IPs with non-200 responses |
| `results/<domain>.json` | Structured JSON with metadata, summary, and grouped findings |

### JSON Structure

```json
{
  "metadata": { "timestamp": "...", "domain": "...", "thread_used": 5 },
  "summary": { "total_found": 42, "unique_active": 10, "honeypots": 2, ... },
  "findings": {
    "unique_active": { "<fingerprint_hash>": { "total": 3, "sample": { ... } } },
    "honeypots": [ { ... } ],
    "wildcard_sample": [ { ... } ],
    "others": { ... }
  }
}
```

---

## 🏗️ Project Structure

```
subdomain-validator/
├── app/
│   ├── main.py             # Entry point — argparse CLI & stdin/pipe support
│   ├── analysis/
│   │   └── honeypot.py     # HoneypotAnalyzer — multi-signal fingerprinting engine
│   ├── core/
│   │   ├── request.py      # HTTP/HTTPS request helpers with latency measurement
│   │   ├── scanner.py      # Orchestration: fetch, threading, wildcard check
│   │   ├── stealth.py      # StealthMode — randomized UA & browser impersonation
│   │   └── validate.py     # Per-subdomain validation logic & stats tracking
│   ├── models/
│   │   ├── scan_config.py  # ScanConfig dataclass & global config accessor
│   │   └── signatures.py   # Honeypot signatures, weights, DNS providers, UA fallbacks
│   ├── sources/
│   │   ├── handler.py      # Source dispatcher — routes to the right fetcher
│   │   ├── hackertarget.py # HackerTarget API source
│   │   ├── crtsh.py        # crt.sh certificate transparency source
│   │   ├── rapiddns.py     # RapidDNS scraper source
│   │   └── alienvault.py   # AlienVault OTX passive DNS source
│   └── utils/
│       ├── output.py       # Output formatting, colorization, sign classification
│       ├── summary.py      # ReconStats — scan result tracker and summary printer
│       └── writer.py       # File saving logic with Cloudflare IP filtering
├── assets/
│   └── banner.txt          # ASCII banner
├── .env.example            # Configuration template
├── Dockerfile              # Docker support (Alpine-based, non-root user)
└── pyproject.toml          # Project metadata and dependencies
```

---

## 🐳 Docker

```bash
# Build
docker build -t subvr .

# Run
docker run --rm subv -d example.com -all
```

---

> [!WARNING]
> **Gunakan dengan bijak. / Use responsibly.**
>
> This tool performs **active reconnaissance** — during the validation phase, HTTP/HTTPS requests are sent directly to each discovered subdomain. Your activity **will be logged** by the target and may trigger IDS/WAF alerts.
>
> This tool is intended **only** for domains you **own** or have **explicit written permission** to test.
> Unauthorized use against third-party domains may violate applicable laws and regulations:
> - 🇮🇩 **UU ITE** (Indonesia)
> - 🇺🇸 **CFAA** (United States)
> - And equivalent laws in your jurisdiction
>
> The author is not responsible for any misuse or damage caused by this tool.

---

## 📜 License

Distributed under the [MIT License](LICENSE).

---

<div align="center">

**subdomain-validator** — Built with ❤️ using Python & multiple OSINT sources

🇮🇩 *Proudly made in Indonesia by [Finsa Kusuma Putra](https://github.com/Finsa-SC)*

#### *"Dari Indonesia, untuk dunia."*
*From Indonesia, for the world*<br>
*let's prove them wrong*
</div>
