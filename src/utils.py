"""
Utilities: read spreadsheet (Excel/CSV) and normalize column names to the
canonical keys used by the RPA Challenge.

Expected canonical headers:
  First Name, Last Name, Company Name, Role in Company, Address, Email, Phone Number
"""

from __future__ import annotations

import re
from typing import Dict, Iterable, List

import pandas as pd

_CANONICAL_BY_TOKEN: Dict[str, str] = {
    "firstname": "First Name",
    "lastname": "Last Name",
    "companyname": "Company Name",
    "roleincompany": "Role in Company",
    "address": "Address",
    "email": "Email",
    "phonenumber": "Phone Number",
}


def _tokenize(s: str) -> str:
    """Lowercase and strip non-letters/digits to match column aliases robustly."""
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def _rename_to_canonical(df: pd.DataFrame) -> pd.DataFrame:
    new_cols: Dict[str, str] = {}
    for col in df.columns:
        tok = _tokenize(str(col))
        new_cols[col] = _CANONICAL_BY_TOKEN.get(tok, str(col).strip())
    return df.rename(columns=new_cols)


def read_rows(path: str, limit: int | None = 10) -> Iterable[Dict[str, str]]:
    """Read spreadsheet rows as dicts with canonical keys. Supports .xlsx/.csv."""
    # Read as strings to preserve leading zeros (e.g., phone numbers)
    if path.lower().endswith((".xls", ".xlsx")):
        df = pd.read_excel(path, engine="openpyxl", dtype=str)
    else:
        df = pd.read_csv(path, dtype=str)

    df = _rename_to_canonical(df)
    df = df.fillna("")

    # Normalize every cell to string
    try:
        df = df.map(lambda v: str(v).strip())
    except AttributeError:
        df = df.applymap(lambda v: str(v).strip())

    rows: List[Dict[str, str]] = df.to_dict(orient="records")

    if limit is not None:
        return rows[:limit]
    return rows
