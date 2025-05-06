# 📑 Contract Extractor

---

## 🚀 Start

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set your OpenAI API key in .env**


3. **Run the extractor**
```bash
# Run against every PDF in ./data, write JSONs to ./output
python -m main --directory data --output-dir output --concurrency 2
```

## ✨ Key Features

- ### **Turn PDF into text**
  Using PyPDF2 to extract all the text, page by page.

- ### **Split text into tokens**
  If a contract is too long, we split it into smaller chunks that fit within the model’s limit. If the tokenizer isn’t there, we just assume every 4 characters is roughly one token.

- ### **Pick the right schemas**
   Schemas (templates) picked by LLM model in a way that which template fits (like “NDA” or “Service Agreement”) to pdf and fills in only valid JSON.

- ### **Fix and combine JSON**
  Sometimes the LLM’s output isn’t perfectly formatted JSON, so we run simple “find and fix” rules to clean it up. Then we merge all the chunks back into one JSON and remove any repeated parties or clauses.

- ### **One JSON file per PDF**
  For Every PDF we will its own `.json` output.

- ### **Pipeline fails**
  If extraction fails or the JSON is unfixable, the pipeline don’t crash: we save a minimal “unknown” template and log an error. We also log how long each chunk took and where we saved the file.


## 🗂 Folder Structure
```
contract_extractor/
├── main.py
│   └─ CLI entry point: orchestrates PDF discovery, LLM client, and concurrency
│
├── models/
│   └── llm_client.py
│       └─ Async wrapper around OpenAI’s chat API
│
├── parsers/
│   └── pdf_loader.py
│       └─ Extract plain text from PDF pages
│
├── utils/
│   ├── token_utils.py      ─ token counting & chunking (real or approximate)
│   ├── json_fix.py         ─ repair near‑JSON blobs into valid JSON
│   └── merge_utils.py      ─ merge chunk outputs + deduplicate parties/clauses
│
├── prompts/
│   └── meta_extraction_prompt.py
│       └─ System prompt template with dynamic schema
│
├── schemas/
│   ├── generic.py          ─ fallback Pydantic model
│   ├── nda.py              ─ NDA‑specific schema
│   ├── employment.py       ─ Employment contract schema
│   └── service_agreement.py─ Service agreement schema
│
├── extractors/
│   └── metadata_extractor.py
│         └─ Core orchestration: load → chunk → call LLM → merge → save
│
├── data/
│    └── Add all the pdf files
│
└── Notebook
   └── contract_extractor.ipynb
         └─ Jupyter notebook to run the whole code in notebook
```

## ➕ Add a new contract type
#### Create schemas/lease.py:
```
from .generic import GenericContractSchema

class LeaseSchema(GenericContractSchema):
    contract_type = "lease"
    rent_amount: str | None = None
    security_deposit: str | None = None
```

## 📖 Approach & Assumptions
- ### **LLM based**
   Rely on ChatGPT for extraction within the schema constraints.

- ### **Chunking**
   Handles very large contracts by splitting on token limits.

- ### **Deduplication**
   Ensures no repeated parties or clauses in merged output.

- ### **Fallback**
   Falls back on missing dependencies or parsing errors.

- ### **Extensible**
   Schema‑based design makes it easy to add new contract types.

## Future Improvements
- ### **Evaluation**
   Integrate a labeled dataset (e.g. CUAD) to compute precision/recall.

- ### **Interactive review**
   Build a simple UI for manual correction & approval.

- ### **Hybrid extraction**
   Combine rule‑based parsers with LLM for higher accuracy.

- ### **Adaptive chunking**
   Dynamically adjust chunk size based on headings or sections.
