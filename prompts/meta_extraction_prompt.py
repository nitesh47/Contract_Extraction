from textwrap import dedent

PROMPT = dedent("""You are an expert contract analyst.

**Goal**  
Return a single **valid JSON object** that follows the selected schema and
contains the best structured metadata you can extract.

### 1. Decide `contract_type`
Give the document a short label (one or two words).

### 2. Pick schema
Select the schema from the menu whose name is closest to that label.
If nothing fits, pick `generic`.

### 3. Extract
Fill every key. Use null where data is absent.  
Unknown but important extra fields → `custom_fields` (key/value).  
Detect common clauses (indemnification, confidentiality, non‑compete, etc.)
and list them in `clauses`.

### Output rules
- **Return only JSON** (no markdown, no explanations).  
- Must parse with `json.loads` on first try.

### Schema menu
{schema_menu}

### Contract
{contract_text}
### End
""")