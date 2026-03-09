# Iraq Database Search

CLI tool for searching Iraq database records by name, phone number, or any value.

## Features

- Search across all tables or filter by specific table
- Fast SQLite-based search
- Export results as JSON
- Works on Linux and Windows

## Installation

### From Source

```bash
git clone https://github.com/GHAIThMsON/iraq-db-search.git
cd iraq-db-search
pip install -e .
```

### Using the Database

The repository includes a pre-built database with ~330K records. The database file is included in the repo.

## Usage

### Search for a name or phone number

```bash
iraq-search search "احمد"
iraq-search search "0770"
iraq-search search "البصرة"
```

### Search in specific table

```bash
iraq-search search "احمد" --table table_3
```

### Limit results

```bash
iraq-search search "احمد" --limit 20
```

### Output as JSON

```bash
iraq-search search "احمد" --json
```

### List all tables

```bash
iraq-search tables
```

### Show database statistics

```bash
iraq-search stats
```

### Show sample data from a table

```bash
iraq-search show table_3 --limit 5
```

## API Server

You can also run a web interface:

```bash
# Install dependencies
pip install flask flask-cors

# Run server
python -m iraq_db_search.server

# Open http://localhost:5000
```

## Database Structure

The database contains 10 tables with ~330K records:

| Table | Records | Description |
|-------|---------|-------------|
| table_0 | 274,765 | Defense database |
| table_1 | 2,004 | Year 2000 data |
| table_2 | 63 | Basra data |
| table_3 | 625 | Lawyers 2023 |
| table_4 | 1,765 | Martyrs & Prisoners |
| table_5 | 1,146 | Student names |
| table_6 | 23,573 | Traffic employees |
| table_7 | 11 | Ministry locations |
| table_8 | 17,907 | Civilian transfers |
| table_9 | 19 | NGOs |

## License

MIT
