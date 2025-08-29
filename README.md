# Digital Workforce – Python RPA Challenge

Automation solution for the **Input Forms** challenge at [rpachallenge.com](https://rpachallenge.com/).  
Implements reliable web automation in **Python 3.10+** with **Playwright**.  

The bot reads data from a spreadsheet (Excel or CSV) and fills 10 rounds of forms where the field order is randomized each round.

---

## Features
- Robust **selectors** (`ng-reflect-name`) → immune to shuffled form layout
- Supports **Excel (.xlsx)** and **CSV** input
- **Headed** mode for debugging; **headless** mode for CI/bonus
- **Performance mode** (`--perf`):  
  - Blocks heavy resources (images, fonts, media)  
  - Uses tighter element wait timeouts  
  - Outputs a run summary + JSON report
- Proof screenshot saved to `screenshots/result.png` and optional JSON `screenshots/run_summary.json`

---

## Quickstart

### 1) Clone & create environment
```bash
git clone https://github.com/jn-ww/rpa_challenge.git
cd rpa-challenge

# virtual environment
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate

pip install -r requirements.txt
python -m playwright install   # Linux: add --with-deps
```
### 2) Input data
Place your spreadsheet in data/ (e.g. data/challenge.xlsx).
Expected headers (case/spacing normalized automatically):
- First Name
- Last Name
- Company Name
- Role in Company
- Address
- Email
- Phone Number
CSV also works.

**Sample data**
A tiny sample dataset is included at data/sample.csv for quick tests and CI runs.
**Note:** The website’s “success rate” is computed against its official dataset. Our data/sample.csv is synthetic and used only for smoke testing/CI, so its banner % is arbitrary. Use data/challenge.xlsx to see 100% (70/70).

### 3) Run
**Headed sample data run:**
```bash
python -m src.main --file data/sample.csv
```
**Headed:**
```bash
python -m src.main --file data/challenge.xlsx
```
**Headless (CI-style):**
```bash
python -m src.main --file data/challenge.xlsx --headless
```
**Performance mode:**
```bash
python -m src.main --file data/challenge.xlsx --headless --perf
```

### 4) Docker (optional)
Run the challenge headless inside a container. Artifacts are saved to ./screenshots/
```bash
# Build the image
docker build -t rpa-challenge .

# Run with volumes (uses data/sample.csv by default)
docker run --rm \
  -v "$(pwd)/data:/app/data" \
  -v "$(pwd)/screenshots:/app/screenshots" \
  rpa-challenge
```
To run a specific file (e.g., your Excel), override the container command:
```bash
docker run --rm \
  -v "$(pwd)/data:/app/data" \
  -v "$(pwd)/screenshots:/app/screenshots" \
  rpa-challenge \
  python -m src.main --file data/challenge.xlsx --headless --perf
```
Windows PowerShell paths:
```powershell
docker run --rm `
  -v "${PWD}\data:/app/data" `
  -v "${PWD}\screenshots:/app/screenshots" `
  rpa-challenge
```
Artifacts: after the run, check screenshots/result.png and screenshots/run_summary.json on your host.

## Design decisions
- Stable selectors: Inputs are located by Angular’s ng-reflect-name (e.g., labelFirstName), which stay consistent even when the form fields shuffle each round.
- Data robustness: Spreadsheets are read with dtype=str, fillna(""), and light header normalization so common variants (e.g., “Phone” → “Phone Number”) still map correctly. This prevents the classic 60/70 miss.
- Round control:
  - Default mode: after each Submit, wait until the first-name field clears (next round ready).
  - Perf mode: use a tiny fixed breather between rounds (tens of ms) instead of a strict DOM condition to avoid flakiness and save time.
- Performance mode (--perf): Blocks heavy resources (images/media/fonts) but keeps stylesheets for layout stability; optional smaller viewport; minimal logging. Produces screenshots/result.png and screenshots/run_summary.json.
- Navigation resilience: Normal navigation waits for domcontentloaded; on a rare timeout, retries with a more permissive wait and ensures the Start button is ready.
- Developer experience: Plain, readable Python; single-line CLI summary; clear repo layout; sample data; optional Docker and CI so reviewers can run it quickly on any machine.

## Project structure
```
rpa-challenge/
├── data/
│   ├── challenge.xlsx         # exam input
│   └── sample.csv             # sample dataset included for quick runs & CI
├── screenshots/               # runtime artifacts (git-ignored)
│   └── .gitkeep
├── src/
│   ├── automation.py          # Playwright automation (selectors, flow, perf tweaks)
│   ├── main.py                # CLI entrypoint
│   └── utils.py               # data loading & header normalization
├── .github/
│   └── workflows/
│       └── python-ci.yml      # CI: lint + headless run on sample.csv (optional)
├── Dockerfile                 # Docker: containerized headless run (optional)
├── .dockerignore
├── requirements.txt
├── pyproject.toml             # ruff/black config
├── .gitignore
└── README.md
```

## Developer notes
Format & lint:
```bash
black .
ruff check . --fix
```
## Troubleshooting
**ModuleNotFoundError: No module named 'src'**
Run from repo root:
```bash
python -m src.main --file data/challenge.xlsx
```
**Playwright browser not installed**
```bash
python -m playwright install   # add --with-deps on Linux
```
**No output in --perf**
Summary is written to screenshots/run_summary.json and also logged at WARNING level.






