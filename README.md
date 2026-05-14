# sheetpipe

> Python utility to sync Google Sheets data into PostgreSQL with schema inference

---

## Installation

```bash
pip install sheetpipe
```

---

## Usage

Configure your Google Sheets and PostgreSQL credentials, then run a sync:

```python
from sheetpipe import SheetPipe

pipe = SheetPipe(
    sheet_id="your_google_sheet_id",
    db_url="postgresql://user:password@localhost:5432/mydb"
)

pipe.sync(sheet_name="Sheet1", table_name="users")
```

Or use the CLI:

```bash
sheetpipe sync --sheet-id YOUR_SHEET_ID --table users --db-url postgresql://user:password@localhost/mydb
```

sheetpipe will automatically infer column types (text, integer, float, boolean, date) from your sheet data and create or update the target table accordingly.

---

## Features

- Automatic schema inference from sheet data
- Creates or updates PostgreSQL tables on the fly
- Supports incremental syncs to avoid full reloads
- Simple CLI and Python API

---

## Requirements

- Python 3.8+
- PostgreSQL 12+
- Google Sheets API credentials (`credentials.json`)

---

## License

MIT © [sheetpipe contributors](LICENSE)