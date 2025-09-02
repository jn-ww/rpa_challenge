import pytest
import pandas as pd

from src.utils import read_rows

CANON = [
    "First Name","Last Name","Company Name","Role in Company",
    "Address","Email","Phone Number"
]

def test_header_normalization_csv(tmp_path):
    # deliberately messy headers + an extra column that should be ignored
    p = tmp_path / "mini.csv"
    p.write_text(
        " first name , LAST  NAME ,Company name,Role in company, address , Email , phone number , Extra\n"
        "Ada,Lovelace,Analytica,Engineer,Some St,ada@ex.com,00123,noise\n"
    )
    rows = list(read_rows(str(p)))
    assert len(rows) == 1
    r = rows[0]

    # canonical keys present
    missing = [k for k in CANON if k not in r]
    assert not missing, f"Missing canonical keys: {missing}"
    
    # dtype=str preserved (leading zeros)
    assert r["Phone Number"] == "00123"

    # allow extra columns; only guarantee canonical ones
    for k in CANON:
        assert isinstance(r[k], str)

def test_empty_cells_become_empty_strings(tmp_path):
    p = tmp_path / "empty.csv"
    p.write_text(
        "First Name,Last Name,Company Name,Role in Company,Address,Email,Phone Number\n"
        "John,,Acme,,Some St,,\n"
    )
    r = list(read_rows(str(p)))[0]
    # cells may be empty but must exist as keys with string values
    for k in CANON:
        assert k in r
        assert isinstance(r[k], str)

def test_xlsx_dtype_str(tmp_path):
    # Skip if openpyxl not installed (CI-safe)
    pytest.importorskip("openpyxl")
    df = pd.DataFrame([{
        "First Name":"John","Last Name":"Doe","Company Name":"Acme",
        "Role in Company":"Dev","Address":"A St","Email":"j@e.com",
        "Phone Number":"0007"
    }])
    x = tmp_path / "mini.xlsx"
    df.to_excel(x, index=False)
    rows = list(read_rows(str(x)))
    assert rows[0]["Phone Number"] == "0007"

