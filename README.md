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
git clone https://github.com/<your-username>/rpa-challenge.git
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

### 3) Run
**Headed (debug):**
```bash
python -m src.main --file data/challenge.xlsx
```
**Headless:**
```bash
python -m src.main --file data/challenge.xlsx --headless
```
**Performance mode:**
```bash
python -m src.main --file data/challenge.xlsx --headless --perf
```
**Debug logging:**
```bash
python -m src.main --file data/challenge.xlsx --log-level DEBUG
```
## 4) Design decisions
- Selectors: used Angular attribute ng-reflect-name (labelFirstName, etc.) for stability across shuffled layouts.
- Data handling: spreadsheets read with dtype=str to preserve phone numbers/leading zeros; headers normalized to canonical names.
- Resilience: waits for form readiness each round; after Submit waits until fields clear.
- Performance mode: blocks images/fonts/media, shortens element waits, always writes a run summary JSON + screenshot.

## 5) Project structure
```
rpa-challenge/
├── data/                # input files (.xlsx/.csv)
├── screenshots/         # proof artifacts
├── src/                 # source code
│   ├── main.py          # CLI entry
│   ├── automation.py    # Playwright logic
│   └── utils.py         # data loading
├── requirements.txt
├── pyproject.toml       # black/ruff config
├── .gitignore
└── README.md
```

## 6) Developer notes
Format & lint:
```bash
black .
ruff check . --fix
```
## 7) Troubleshooting
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






