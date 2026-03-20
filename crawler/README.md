# UCI Resource Crawler

This folder contains a schema-aware crawler for collecting UCI student resources.

## Output

By default the crawler writes generated data to:

- `crawler/output/uci_resources.json`

## Run locally

From the project root:

```bash
python3 -m pip install -r requirements.txt
python3 crawler/run.py
```

Useful options:

```bash
python3 crawler/run.py --max-pages 20
python3 crawler/run.py --output crawler/output/dev_resources.json
python3 crawler/run.py --seed-file crawler/seeds.txt
```

## Notes

- The crawler uses curated seed URLs and only follows allowed UCI domains.
- Every output record keeps the existing JSON shape:
  - `category`
  - `name`
  - `location`
  - `contact_info`
  - `description`
  - `target_audience`
  - `source_url`
- The required fields are `category`, `name`, `location`, `contact_info`, and `source_url`.
- `description` and `target_audience` are preserved for compatibility and may be empty strings.
