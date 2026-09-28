from pathlib import Path

import duckdb

BASE_DIR = Path(__file__).parent / "data"
RAW_DIR = BASE_DIR / "raw"
DB_PATH = BASE_DIR / "warehouse.duckdb"


def load_json_files():
    con = duckdb.connect(str(DB_PATH))

    con.execute("""
        CREATE TABLE IF NOT EXISTS raw_quotes (
            symbol VARCHAR,
            current_price DOUBLE,
            change DOUBLE,
            percent_change DOUBLE,
            high DOUBLE,
            low DOUBLE,
            open DOUBLE,
            previous_close DOUBLE,
            quote_timestamp BIGINT,
            fetched_at TIMESTAMP
        )
    """)

    con.execute("""
        CREATE TABLE IF NOT EXISTS loaded_files (
            filepath VARCHAR PRIMARY KEY,
            loaded_at TIMESTAMP DEFAULT current_timestamp
        )
    """)

    already_loaded = {
        row[0] for row in con.execute("SELECT filepath FROM loaded_files").fetchall()
    }

    files = sorted(RAW_DIR.glob("quotes_*.json"))
    # Keep the same "data/raw/<name>" key format as before,
    # so files you already loaded aren't loaded twice.
    new_files = [f for f in files if f"data/raw/{f.name}" not in already_loaded]
    print(f"Found {len(files)} file(s) total, {len(new_files)} new")

    for f in new_files:
        con.execute("""
            INSERT INTO raw_quotes
            SELECT
                symbol,
                c AS current_price,
                d AS change,
                dp AS percent_change,
                h AS high,
                l AS low,
                o AS open,
                pc AS previous_close,
                t AS quote_timestamp,
                fetched_at::TIMESTAMP
            FROM read_json_auto(?)
        """, [str(f)])
        con.execute(
            "INSERT INTO loaded_files (filepath) VALUES (?)",
            [f"data/raw/{f.name}"],
        )
        print(f"Loaded {f.name}")

    total = con.execute("SELECT COUNT(*) FROM raw_quotes").fetchone()[0]
    print(f"Total rows in raw_quotes: {total}")
    con.close()


if __name__ == "__main__":
    load_json_files()