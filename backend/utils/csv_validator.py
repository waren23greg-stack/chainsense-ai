import pandas as pd
import io, re

MAX_ROWS = 500_000
MAX_COLS = 100

BINARY_SIGNATURES = [b"\x7fELF", b"MZ", b"\x89PNG", b"\xff\xd8\xff", b"PK\x03\x04", b"%PDF", b"\x1f\x8b"]
CSV_INJECTION_RE  = re.compile(r'(?:^|,)[\s"\']*[=+\-@\t\r|]', re.MULTILINE)

class ValidationError(Exception):
    pass

def validate_csv_upload(file_storage):
    raw = file_storage.read()
    if not raw:
        raise ValidationError("File is empty.")
    for sig in BINARY_SIGNATURES:
        if raw[:len(sig)] == sig:
            raise ValidationError("File is not a plain-text CSV. Binary files are not accepted.")
    if b"\x00" in raw:
        raise ValidationError("File contains null bytes.")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("latin-1")
    if CSV_INJECTION_RE.search(text):
        raise ValidationError("File contains formula injection characters (=, +, -, @). Clean the file and retry.")
    try:
        df = pd.read_csv(io.StringIO(text), low_memory=False, on_bad_lines="skip", nrows=MAX_ROWS + 1)
    except pd.errors.EmptyDataError:
        raise ValidationError("CSV has no data rows.")
    except Exception as e:
        raise ValidationError(f"Could not parse CSV: {e}")
    if len(df) == 0:
        raise ValidationError("CSV has no data rows.")
    if len(df) > MAX_ROWS:
        raise ValidationError(f"CSV exceeds {MAX_ROWS:,}-row limit.")
    if len(df.columns) > MAX_COLS:
        raise ValidationError(f"Too many columns ({len(df.columns)}). Max is {MAX_COLS}.")
    return df

def detect_column_roles(df):
    cols  = {c.lower().strip(): c for c in df.columns}
    roles = {}
    candidates = {
        "revenue":  ["revenue","total_amount","amount","sales","order_value"],
        "date":     ["order_date","date","created_at","shipped_date"],
        "status":   ["status","order_status","shipment_status"],
        "supplier": ["supplier_name","supplier","supplier_id","vendor"],
        "product":  ["product_name","product","product_id","sku"],
        "delay":    ["delay_days","delay","days_late","shipment_delay"],
        "stock":    ["stock_level","stock","inventory","quantity_on_hand"],
        "reorder":  ["reorder_point","reorder_level","min_stock"],
        "carrier":  ["carrier","carrier_name","shipper"],
        "quantity": ["quantity","qty","units"],
        "country":  ["country","region","origin_country"],
    }
    for role, names in candidates.items():
        for n in names:
            if n in cols:
                roles[role] = cols[n]
                break
    return roles
