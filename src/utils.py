"""
Utilities: read spreadsheet (Excel/CSV) and normalize column names to the
canonical keys used by the RPA Challenge.
"""

from __future__ import annotations

from typing import Dict, Iterable, List

import pandas as pd

# Map many possible header spellings -> canonical names
_CANONICAL_BY_TOKEN: Dict[str, str] = {
    "firstname": "First Name",
    "first name": "First Name",
    "lastname": "Last Name",
    "last name": "Last Name",
    "companyname": "Company Name",
    "company name": "Company Name",
    "roleincompany": "Role in Company",
    "role in company": "Role in Company",
    "address": "Address",
    "email": "Email",
    "phonenumber": "Phone Number",
    "phone number": "Phone Number",
    "phone": "Phone Number",
}


def _tok(s: str) -> str:
    # normalize: lowercase, keep letters/digits/spaces, collapse spaces
    s = "".join(ch for ch in str(s).lower() if ch.isalnum() or ch.isspace())
    return " ".join(s.split())


def _rename_to_canonical(df: pd.DataFrame) -> pd.DataFrame:
    rename: Dict[str, str] = {}
    for col in df.columns:
        canon = _CANONICAL_BY_TOKEN.get(_tok(col))
        rename[col] = canon if canon else str(col).strip()
    return df.rename(columns=rename)


def read_rows(path: str, limit: int | None = 10) -> Iterable[Dict[str, str]]:
    """Read .xlsx/.csv as strings; fill NaNs; strip whitespace; normalize headers."""
    if path.lower().endswith((".xls", ".xlsx")):
        df = pd.read_excel(path, engine="openpyxl", dtype=str)
    else:
        df = pd.read_csv(path, dtype=str)

    df = _rename_to_canonical(df)
    df = df.fillna("")

    # Normalize every cell to string
    try:
        df = df.map(lambda v: v.strip() if isinstance(v, str) else str(v).strip())
    except AttributeError:
        df = df.applymap(lambda v: v.strip() if isinstance(v, str) else str(v).strip())

    rows: List[Dict[str, str]] = df.to_dict(orient="records")
    return rows if limit is None else rows[:limit]
