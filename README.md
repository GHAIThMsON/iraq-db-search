# Iraq Database Search

CLI tool for searching Iraq database records by name, phone number, or any value.

## Features

- Search by any value (name, phone, or any text)
- Search by name specifically
- Search by phone number
- Fast SQLite-based search
- JSON output
- Works on Linux and Windows

## Installation

```bash
git clone https://github.com/GHAIThMsON/iraq-db-search.git
cd iraq-db-search
pip install -e .
```

## Usage

### Search for any value (name, phone, or text)
```bash
iraq-search search "احمد"
iraq-search search "0770"
iraq-search search "البصرة"
```

### Search by name
```bash
iraq-search name "احمد"
```

### Search by phone number
```bash
iraq-search phone "0770"
iraq-search phone "078"
```

### Get database statistics
```bash
iraq-search stats
```

### Limit results
```bash
iraq-search search "احمد" --limit 20
```

## Database Statistics

- Total Records: ~322,000
- Total Tables: 10

## Example Output

```json
[
  {
    "الاسم_الكامل": "احمد محمد علي",
    "المحافظة": " Baghdad",
    "الرقم_القياسي": "123456"
  },
  {
    "اسم_الخريج": "احمد عبد الله",
    "سنة_التخرج": "2020"
  }
]
```

## License

MIT
