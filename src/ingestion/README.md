# On the ETL ingestion process

There are currently two ingestion processes in place:
```sh
$ semantic erl run
```
ingests the documents specified in `src/ingestion/resources/`, namely:
- Código Civil
- Código Penal

These are large bodies of text with several articles and a deep hierarchical structure and don't need to be ingested every day. Only updated once a while.

On the other hand, the `src/ingestion/downloader.py` module provides tools to execute the Airflow pipeline which ingests more atomic data. Currently this is implemented:
- Jurisprudencia

These documents are downloaded, parsed and processed and stored on the datalake for ingestion into the Chroma DB.

## Structure of the datalake

- Bucket: `/legal/` for all storage related to this project
- 
- `datalake/`: all data produced by the ETL prior to ingestion into the database
  - `raw/`: all raw data as downloaded by the ETL process
    - `jurisprudencia/`: all raw data related to jurisprudencia
      - `paginations/YYYY/MM/DD/repsonse_#.html`: The different pages of results after web scraping
      - `/pdfs/YYYYMMDD/<ref-id>.pdf`: all pdfs downloaded by the ETL process
  - `refined/`: Data that has been processed and put in a `json` document
    - `jurisprudencia/`: all data related to jurisprudencia
      - `paginations/YYYY/MM/DD/records.json`: The records published on a given day
      - `/pdfs/YYYYMMDD/<ref-id>.json`: The content of the pdf in the `Node` structured format
      