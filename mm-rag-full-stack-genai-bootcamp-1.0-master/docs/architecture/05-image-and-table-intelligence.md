# 05 — Image & Table Intelligence Strategy

Non-prose content is where naive RAG fails: tables get flattened into
unreadable token soup and images get indexed as an OCR fragment or not
at all. This document covers how tables and images are parsed, what text
is embedded for each, and how retrieval makes sure they are reachable.

Related: [04 hybrid retrieval](04-hybrid-retrieval-strategy.md) ·
[02 data model](02-multitenant-data-model.md)

Implementation: [parsing.py](file:///d:/mm-rag-full-stack-genai-bootcamp-1.0-master/mm-rag-full-stack-genai-bootcamp-1.0-master/src/parsing.py) ·
[ingestion.py](file:///d:/mm-rag-full-stack-genai-bootcamp-1.0-master/mm-rag-full-stack-genai-bootcamp-1.0-master/src/ingestion.py)

---

## 1. Content taxonomy

Every parsed artifact is tagged with a `content_type` in Qdrant
metadata, and that tag drives both chunking and retrieval behaviour.

| `content_type` | Produced by | Chunked? | Embedded text |
|---|---|---|---|
| `page_text_plus_ocr` | selectable PDF text + page OCR | ✅ recursively | page text + OCR |
| `text` | generic text input | ✅ recursively | raw text |
| `table` | `pdfplumber` `extract_tables()` | ❌ kept whole | headers + row-by-row `col = value` + Markdown |
| `image` | embedded images + page rasters | ❌ kept whole | **vision caption** + OCR + path |

`TEXT_CONTENT_TYPES = {page_text_plus_ocr, text}` are the only types
that go through `RecursiveCharacterTextSplitter` (2000 / 120). Tables and
images are deliberately **never split**, because a table row detached
from its header row is worse than useless, and a caption split in half
loses the subject.

---

## 2. Table intelligence

### 2.1 Extraction

`ComplexPDFParser.extract_tables()` (pdfplumber) per page:

1. Detect tables; normalize ragged rows to a rectangle.
2. Clean header artifacts (e.g. `"ansaction Date" → "Transaction Date"`,
   trailing `" Tr"` fragments) without changing column count.
3. Synthesize `column_N` names for unnamed columns.
4. Produce **three** representations of every table:
   - `markdown` — `DataFrame.to_markdown(index=False)`,
   - `csv` — for structured export,
   - `searchable_text` — an explicit, verbose form:
     ```
     TABLE FOUND ON PAGE 3
     TABLE INDEX: 0
     NUMBER OF COLUMNS: 4
     NUMBER OF DATA ROWS: 12

     TABLE COLUMNS:
     Transaction Date, Description, Debit, Credit

     ROW 1:
     Transaction Date = 2024-01-05 | Description = ... | Debit = ... | Credit = ...
     ROW 2:
     ...
     ```

### 2.2 Why the redundant `searchable_text`

A raw Markdown table embeds poorly: pipes and padding dominate the
token budget, and `col = value` adjacency — which is exactly what a
question like *"what was the debit on 2024-01-05?"* needs — is absent.
The verbose form gives the embedder and BM25 an explicit
`header = value` pairing per row, so both dense and lexical retrieval
can match a value to its column. Markdown is retained because it is
what the LLM reads best when the table is selected as evidence.

### 2.3 Indexing

The table becomes **one** Qdrant point containing:

```
TABLE FOUND ON PAGE n
TABLE INDEX: i

TABLE DIMENSIONS:
Rows: R
Columns: C

TABLE COLUMNS:
h1, h2, ...

SEARCHABLE TABLE CONTENT:
<searchable_text>

TABLE MARKDOWN:
<markdown>
```

with metadata `table_index`, `table_row_count`, `table_column_count`,
`table_headers`. High-quality tables are indexed as structure, not as
recovered text — this satisfies the "index tables as structured
Markdown" requirement.

### 2.4 Retrieval

- `content_types=["table"]` restricts the search to tables.
- `guaranteed_content_types=("table","image")` (the `generate` default)
  ensures at least one table reaches the context even when a text chunk
  outranks it — see
  [04 §3.5](04-hybrid-retrieval-strategy.md).

---

## 3. Image intelligence

The design goal is explicit: images must be reachable by **natural
language description**, not only by whatever text happens to be printed
inside them.

### 3.1 Two signals per image

| Signal | Source | Role |
|---|---|---|
| OCR text | `pytesseract` on the extracted image | literal text in the image |
| Vision caption | Ollama vision model (`moondream` by default) | semantic description (objects, diagrams, layout, people) |

OCR answers "what words are in it"; the caption answers "what is it".

### 3.2 Caption generation

`MultimodalDocumentIngestion._generate_image_caption()`:

- base64-encodes the image and POSTs to
  `{OLLAMA_BASE_URL}/api/generate` with
  `{"model": <vision_model>, "prompt": ..., "images": [b64], "stream": false}`,
- prompt is constrained to be factual and to **not invent** content:
  > Describe this image for document search. Be factual and concise.
  > Mention important objects, visible text, labels, diagrams, symbols,
  > layout, people … Do not invent information that is not visible.
- an empty caption is treated as a failure (`RuntimeError`), not
  silently accepted.

`_enrich_image_document()` then rewrites the image document's
`page_content` so the **caption becomes part of the embedded text**:

```
IMAGE CAPTION:
<caption>

IMAGE METADATA:
Page: n
Image Index: i
Image Path: ...

PARSER CONTENT:
<original OCR-based content>
```

Because the existing MiniLM pipeline embeds `page_content`, this makes
the image retrievable by semantic description **without** introducing a
second embedding space, a CLIP model or a multivector setup.

### 3.3 Caption is also stored as payload

`metadata.image_caption`, `image_caption_model`,
`image_caption_version = "v1"`, `image_searchable`, and `image_path`
are persisted, so the caption is inspectable and re-versionable
independently of the vector.

### 3.4 Graceful degradation (important)

Vision captioning is the least reliable step in the pipeline — the
model may be absent, slow or erroring. Failure must not lose the image:

| Failure | Handling |
|---|---|
| image path unresolvable | keep original content, `image_searchable=False`, `image_caption_error=…` |
| Ollama error / timeout / empty caption | keep original OCR content, record `image_caption_error` |

In both cases the point is still upserted, so the image remains
retrievable by its OCR text. The caption enhancement is additive.

### 3.5 Retrieval and generation

- `content_types=["image"]` targets images;
  `guaranteed_content_types` guarantees ≥1 image in the evidence set.
- At generation time, when an image point is selected, the **original
  image file** is attached to the multimodal message
  (`_build_messages` / `used_images`), so the model sees the actual
  pixels rather than only the caption — caption for *retrieval*, pixels
  for *reasoning*.

---

## 4. Page rasters

Alongside embedded images, the parser renders **page images**
(`page_image_path`) and OCRs them into the page's
`page_text_plus_ocr` chunk. This recovers text from scanned pages where
no selectable text layer exists, so a fully scanned PDF is still
searchable even before any image-level captioning.

---

## 5. Known limitations

- **Caption quality is model-bound.** `moondream` is small and CPU
  friendly; it will miss fine detail. The caption prompt, model and
  version are recorded per point so captions can be regenerated later
  when a better vision model is available (`image_caption_version`).
- **No native cross-modal vectors.** Images are represented through
  caption/OCR text only. A CLIP/SigLIP image vector or ColPali-style
  multivector retrieval would allow image-to-image and stronger
  image-to-text matching; it is the natural next step, not the current
  implementation.
- **Cost.** One vision call per image adds wall-clock time to ingestion;
  this is why ingestion is asynchronous (see
  [03](03-async-ingestion-workflow.md)) and bounded by `vision_timeout`.
- **Table extraction depends on ruling lines.** Borderless tables will
  be missed by pdfplumber's default strategy; a layout-model fallback
  (e.g. table-transformer) would be required to cover them.
