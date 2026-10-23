

# Document 1

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 1,
  "content_type": "page_text_plus_ocr",
  "image_count": 0,
  "page_image_path": "C:\\Users\\prash\\AppData\\Local\\Temp\\mmrag_parsed_a4a_k005\\page_images\\page_001.png"
}
```

Content:
PAGE 1

SELECTABLE TEXT:
Complex RAG Parsing Sample - synthetic document
Page 1
Complex Document for RAG Parsing Tests
Synthetic 15-page PDF with paragraphs, simple and complex tables, diagrams, scanned-form style image, metadata
examples, and production RAG edge cases.
Story Line
Three client teams - Arka Finance, BlueLeaf Retail, and CityRide Mobility - are migrating contracts, policies, support records,
and operational reports into a single RAG platform. Each team has different document types, access rules, and parsing
challenges. The RAG system must answer questions with citations while ensuring that one client never sees another clients
data.
This PDF is intentionally designed to test document loaders, PDF parsers, OCR workflows, table extraction, chunking
strategies, metadata preservation, and source citation quality.
Key statement: RAG does not train the model. RAG gives the model the right context before answering.
Section
Parsing challenge
Why it matters for RAG
Contracts
Dense legal text, clause numbers, cross
references
Need section-aware chunks and citations
Tables
Merged headers, numeric columns,
footnotes
Need row/column preservation
Images
Architecture diagram, heatmap, scanned
form
Need OCR or multimodal extraction
Multi-tenant metadata
client_id, document_id,
contract_group_id
Need access-safe retrieval

OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 2

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 2,
  "content_type": "page_text_plus_ocr",
  "image_count": 1,
  "page_image_path": "C:\\Users\\prash\\AppData\\Local\\Temp\\mmrag_parsed_a4a_k005\\page_images\\page_002.png"
}
```

Content:
PAGE 2

SELECTABLE TEXT:
Complex RAG Parsing Sample - synthetic document
Page 2
1. Business Scenario
The platform team is building a document intelligence layer for contract operations. Legal users need answers such as: Which
contracts renew automatically? Which agreements have a 60-day termination notice? Which documents mention data
residency in India? These questions require retrieval across multiple document types and sometimes across multiple related
documents of a single client.
Support teams also want answers from SOPs, markdown runbooks, HTML exports, chat transcripts, and CSV logs. A single
parser is not enough because the corpus contains born-digital PDFs, scanned forms, HTML, markdown, and spreadsheet-like
tables.
Client
Main document family
Risk
Primary users
Typical question
Arka Finance
MSA, audit addendum, DPA
High
Legal and compliance
What audit rights exist in the DPA?
BlueLeaf Retail
MSA, pricing, support SLA
Medium
Procurement
Which clause controls renewal
pricing?
CityRide Mobility
Ops reports, incident logs,
SOPs
Medium
Operations
Which depot had repeated battery
incidents?
Caption: Ownership map showing how client admins, legal teams, audit teams, document storage, vector storage, and the RAG service interact.

OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 3

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 3,
  "content_type": "page_text_plus_ocr",
  "image_count": 0,
  "page_image_path": "C:\\Users\\prash\\AppData\\Local\\Temp\\mmrag_parsed_a4a_k005\\page_images\\page_003.png"
}
```

Content:
PAGE 3

SELECTABLE TEXT:
Complex RAG Parsing Sample - synthetic document
Page 3
2. Raw Data Inventory
The ingestion team receives files from multiple sources. Some files are clean and digital; others contain scanned pages,
rotated tables, missing metadata, embedded images, or formula-generated values. The inventory below intentionally includes
different formats and extraction expectations.
Asset ID
Client
Format
Pages/Rows
Expected extraction
Notes
ARK-MSA-001
Arka Finance
PDF
32 pages
Clauses, tables, signatures
Born-digital text with footer
references
ARK-DPA-002
Arka Finance
DOCX
18 pages
Headings, lists, tables
Track changes removed
before ingestion
BLR-PRICE-00
3
BlueLeaf Retail
XLSX
12 sheets
Rate cards, discounts
Merged cells and formulas
BLR-SLA-004
BlueLeaf Retail
PDF
9 pages
SLA table, escalation matrix
Table crosses page boundary
CRM-OPS-005
CityRide Mobility
CSV
48,200 rows
Incident records
Needs column type
normalization
CRM-FORM-00
6
CityRide Mobility
Scanned PDF
4 pages
OCR fields, checkbox
Low contrast and slight
rotation
KB-RUN-007
Shared
Markdown
14 files
Runbook sections
Good for heading-based
chunks
WEB-FAQ-008
Shared
HTML
23 pages
FAQ content, links
Needs boilerplate removal
Parsing difficulty increases when a document combines multiple layouts: paragraph text, tables, images, and notes. Good
parsers preserve structure; weak parsers flatten everything into a noisy text stream.

OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 4

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 4,
  "content_type": "page_text_plus_ocr",
  "image_count": 0,
  "page_image_path": "C:\\Users\\prash\\AppData\\Local\\Temp\\mmrag_parsed_a4a_k005\\page_images\\page_004.png"
}
```

Content:
PAGE 4

SELECTABLE TEXT:
Complex RAG Parsing Sample - synthetic document
Page 4
3. Contract Excerpt: Dense Legal Text
Clause 7.2 - Confidential Information. The Receiving Party shall protect Confidential Information using at least the same
degree of care that it uses to protect its own confidential materials, but in no event less than reasonable care. Confidential
Information includes technical documents, pricing schedules, user lists, API keys, operational procedures, security reports,
incident response notes, product roadmaps, and any derived analysis prepared by the Receiving Party.
Clause 7.3 - Exclusions. Confidential Information does not include information that is publicly available without breach,
independently developed without reference to the Disclosing Party material, received lawfully from a third party, or approved
for release in writing. The burden of proving an exclusion remains with the Receiving Party.
Clause 9.1 - Data Residency. If the Statement of Work identifies a specific processing region, the service provider shall
process production records only within that region unless the client approves a transfer in writing. Disaster recovery replicas
may be stored in a secondary region if encryption at rest and access logging are enabled.
Clause 11.4 - Termination Assistance. Upon termination, the provider shall make client data available for export for a period
of thirty days. After the export period, the provider may delete production data according to the deletion schedule unless a
legal hold applies.
Clause
Short name
Owner
Trigger
Required action
Citation hint
7.2
Confidentiality
Receiving Party
Receipt of confidential
material
Protect information with reasonable care
and equivalent internal controls
Page 4, clause
7.2
9.1
Data residency
Service Provider
SOW specifies region
Process production records only in
approved region
Page 4, clause
9.1
11.4
Termination
assistance
Service Provider
Agreement
termination
Provide export window for 30 days
Page 4, clause
11.4
Parser note: clause numbering is important. Chunking should not remove or split clause identifiers because users often
ask questions using clause numbers.

OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 5

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 5,
  "content_type": "page_text_plus_ocr",
  "image_count": 0,
  "page_image_path": "C:\\Users\\prash\\AppData\\Local\\Temp\\mmrag_parsed_a4a_k005\\page_images\\page_005.png"
}
```

Content:
PAGE 5

SELECTABLE TEXT:
Complex RAG Parsing Sample - synthetic document
Page 5
4. Simple Table: Policy Rules
The following table is intentionally simple. It should be correctly extracted by most PDF table parsers. It tests basic row and
column detection, short text values, and numeric values.
Policy Area
Rule
Owner
Review Cycle
Refunds
Refund requests must be raised within 7 days of
purchase.
Customer Support
Quarterly
Data Export
Client admins can request export in CSV or JSON
format.
Platform Ops
Monthly
Access Review
Privileged access must be reviewed every 30 days.
Security
Monthly
Incident Response
Critical incidents require acknowledgement within 30
minutes.
SRE
After each incident
Vendor Review
High-risk vendors require annual risk assessment.
Procurement
Annual
Narrative Around the Table
This table appears between paragraphs, which is common in enterprise documents. A good parser should preserve the
paragraph before the table, the table content, and the paragraph after the table in the correct reading order.
For RAG systems, simple tables are often converted into row-wise text chunks such as: Policy Area: Refunds; Rule: Refund
requests must be raised within 7 days; Owner: Customer Support.

OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 6

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 6,
  "content_type": "page_text_plus_ocr",
  "image_count": 0,
  "page_image_path": "C:\\Users\\prash\\AppData\\Local\\Temp\\mmrag_parsed_a4a_k005\\page_images\\page_006.png"
}
```

Content:
PAGE 6

SELECTABLE TEXT:
Complex RAG Parsing Sample - synthetic document
Page 6
5. Complex Table: SLA, Escalation, and Credits
This table uses long cells and operational footnotes. It is designed to test whether the parser can retain header hierarchy and
map values to the correct columns.
Service Category
Severity
Response Target
Resolution Target
Service Credit
Evidence Required
API Availability
P1 - complete
outage
15 minutes
4 hours
10 percent monthly
fee credit
Monitoring logs and incident
ticket
API Availability
P2 - degraded
performance
30 minutes
8 hours
5 percent monthly fee
credit
Latency dashboard and
affected endpoint list
Data Pipeline
P1 - ingestion
stopped
20 minutes
6 hours
8 percent pipeline fee
credit
Queue depth, failed job IDs,
replay report
Data Pipeline
P3 - delayed
batch
4 hours
Next business day
No automatic credit
Batch ID and SLA exception
note
Support
P2 - urgent
support
1 hour
1 business day
2 percent support fee
credit
Support ticket with timestamps
Footnote A: Service credits are not cumulative across the same service category for the same calendar month. Footnote B: Credits do not apply
when delay is caused by client-side network restrictions, missing credentials, or force majeure events.
Parser note: table footnotes should remain attached to the table. If the footnote is separated, an answer about credits may
become incomplete or misleading.

OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 7

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 7,
  "content_type": "page_text_plus_ocr",
  "image_count": 1,
  "page_image_path": "C:\\Users\\prash\\AppData\\Local\\Temp\\mmrag_parsed_a4a_k005\\page_images\\page_007.png"
}
```

Content:
PAGE 7

SELECTABLE TEXT:
Complex RAG Parsing Sample - synthetic document
Page 7
6. Image: RAG Architecture Diagram
The diagram below represents the ingestion and retrieval flow. Some PDF parsers ignore images completely, while others
extract image metadata but not the text inside the image. For production use, image content may require OCR or multimodal
extraction.
Caption: A simplified RAG pipeline showing raw files, parsing, chunking, embeddings, vector database, retriever, LLM, and grounded answer
generation.
Image element
Potential extraction method
Expected output
Box labels
OCR or vision model
Raw Files, Parser, Chunks, Vector DB
Arrows
Layout or vision understanding
Processing order
Caption
Normal PDF text extraction
Description of the diagram

OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 8

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 8,
  "content_type": "page_text_plus_ocr",
  "image_count": 0,
  "page_image_path": "C:\\Users\\prash\\AppData\\Local\\Temp\\mmrag_parsed_a4a_k005\\page_images\\page_008.png"
}
```

Content:
PAGE 8

SELECTABLE TEXT:
Complex RAG Parsing Sample - synthetic document
Page 8
7. Markdown Runbook Excerpt
Markdown files are often easier to parse because headings and code blocks are explicit. However, when markdown is
exported to PDF, the structure may become visual rather than semantic.
# Runbook: Contract Ingestion Failure
## Symptoms
- Upload status remains `processing` for more than 30 minutes.
- Worker logs show repeated timeout errors.
- Vector count does not increase for the affected document.
## Recovery Steps
1. Confirm the object exists in document storage.
2. Re-run parser with `safe_mode=True`.
3. Rebuild chunks with the previous chunking configuration.
4. Compare chunk count with the last successful ingestion.
5. Trigger re-embedding only for changed chunks.
A good parser should preserve code block boundaries and avoid mixing numbered steps with surrounding prose. In RAG,
runbooks are useful because users often ask operational questions that require exact steps.
Runbook field
Value
Parsing expectation
Title
Contract Ingestion Failure
Should become section title metadata
Symptoms
Five bullet items
Should remain as list or separate lines
Recovery Steps
Numbered sequence
Order must be preserved

OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 9

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 9,
  "content_type": "page_text_plus_ocr",
  "image_count": 1,
  "page_image_path": "C:\\Users\\prash\\AppData\\Local\\Temp\\mmrag_parsed_a4a_k005\\page_images\\page_009.png"
}
```

Content:
PAGE 9

SELECTABLE TEXT:
Complex RAG Parsing Sample - synthetic document
Page 9
8. Scanned Form and OCR Challenge
This page contains a scanned-form style image. Text inside the form is not normal selectable PDF text. A simple text parser
may miss it entirely. OCR-based systems should extract labels, values, and checkboxes from the image.
Caption: The form includes fields such as Client Name, Contract ID, Effective Date, Renewal Type, Data Region, Reviewer, and a checkbox
approval statement.
Field
Expected OCR value
Validation rule
Client Name
BlueLeaf Retail Pvt Ltd
Must match known client list
Contract ID
BLR-MSA-2026-019
Pattern: client-code + type + year +
sequence
Effective Date
01 Apr 2026
Date parser should normalize to ISO
format
Approval checkbox
Checked
Boolean extraction required

OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 10

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 10,
  "content_type": "page_text_plus_ocr",
  "image_count": 0,
  "page_image_path": "C:\\Users\\prash\\AppData\\Local\\Temp\\mmrag_parsed_a4a_k005\\page_images\\page_010.png"
}
```

Content:
PAGE 10

SELECTABLE TEXT:
Complex RAG Parsing Sample - synthetic document
Page 10
9. Multiple Documents for One Client
BlueLeaf Retail has five related contract documents. If these documents are indexed independently without relationship
metadata, the retriever may miss cross-document context. The platform uses a contract_group_id to connect related
documents.
document_id
document_type
contract_group_id
effective_date
relationship
BLR-MSA-001
Master Service
Agreement
BLR-ACME-2026
2026-04-01
Base commercial agreement
BLR-NDA-002
NDA
BLR-ACME-2026
2026-04-01
Confidentiality terms
BLR-SOW-003
Statement of Work
BLR-ACME-2026
2026-04-15
Project scope and deliverables
BLR-PRICE-004
Pricing Amendment
BLR-ACME-2026
2026-05-01
Updated pricing and discount tiers
BLR-SLA-005
Support SLA
BLR-ACME-2026
2026-05-10
Support response and credits
Example question: What does the BlueLeaf agreement say about termination assistance and pricing changes? A good
retriever may need chunks from the MSA and the Pricing Amendment together.
Relationship metadata allows retrieval across related documents without mixing unrelated client data.

OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 11

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 11,
  "content_type": "page_text_plus_ocr",
  "image_count": 0,
  "page_image_path": "C:\\Users\\prash\\AppData\\Local\\Temp\\mmrag_parsed_a4a_k005\\page_images\\page_011.png"
}
```

Content:
PAGE 11

SELECTABLE TEXT:
Complex RAG Parsing Sample - synthetic document
Page 11
10. Multi-tenant Retrieval and Access Control
In a multi-tenant RAG system, each document, chunk, embedding, and retrieval request should be associated with a tenant
identifier. Client isolation should happen before the LLM receives any context.
Layer
Control
Failure mode if missing
Authentication
Identify user and organization
Unknown user may access application
Authorization
Map user to client_id and role
User may retrieve another clients documents
Vector retrieval
Filter by client_id or namespace
Retriever may return unauthorized chunks
Prompt construction
Send only allowed context
LLM may see sensitive data
Audit logging
Record query, source chunks, user_id
No traceability during incident review
Correct flow: authenticate user, get client_id from backend, retrieve only matching chunks, build prompt with authorized
context, return answer with citations.
Wrong flow: retrieve from all clients and tell the model to ignore unauthorized content. This is unsafe because the LLM should
not be used as the access-control boundary.

OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 12

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 12,
  "content_type": "page_text_plus_ocr",
  "image_count": 1,
  "page_image_path": "C:\\Users\\prash\\AppData\\Local\\Temp\\mmrag_parsed_a4a_k005\\page_images\\page_012.png"
}
```

Content:
PAGE 12

SELECTABLE TEXT:
Complex RAG Parsing Sample - synthetic document
Page 12
11. Analytics Image: Retention Heatmap
The heatmap below simulates viewership retention by time slot. A parser that ignores chart images will miss useful business
context. OCR can extract axis labels and numbers, but chart understanding may require a vision model.
Observation
Supporting value
Scheduling implication
Prime Friday performs best
93 retention score
Place premium content in Friday late/prime slots
Early week late slots
underperform
10 to 21 score range
Avoid launching new series in weak slots
Evening improves midweek
77 on Wednesday evening
Use midweek evening for discovery content
For RAG, chart captions should be indexed. If chart values are critical, extract them into structured metadata or a
companion table.

OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 13

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 13,
  "content_type": "page_text_plus_ocr",
  "image_count": 0,
  "page_image_path": "C:\\Users\\prash\\AppData\\Local\\Temp\\mmrag_parsed_a4a_k005\\page_images\\page_013.png"
}
```

Content:
PAGE 13

SELECTABLE TEXT:
Complex RAG Parsing Sample - synthetic document
Page 13
12. Evaluation Dataset
A RAG system should be evaluated separately for retrieval quality and answer quality. This page includes a miniature
evaluation set with expected source references. It is useful for testing whether citations point to the correct section.
Test ID
Question
Expected source
Expected answer element
Failure signal
Q-001
What is the refund window?
Policy Rules table
7 days
Answer says 30 days
Q-002
Which clause covers data
residency?
Clause 9.1
Approved processing region
No clause citation
Q-003
What is P1 API response target?
SLA table
15 minutes
Wrong severity row
Q-004
Which documents belong to
BLR-ACME-2026?
Relationship table
Five related documents
Only one document
returned
Q-005
Who owns access review?
Policy Rules table
Security
Owner missing
Evaluation should include adversarial questions, unrelated questions, and questions that require multi-hop retrieval across
related documents.

OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 14

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 14,
  "content_type": "page_text_plus_ocr",
  "image_count": 0,
  "page_image_path": "C:\\Users\\prash\\AppData\\Local\\Temp\\mmrag_parsed_a4a_k005\\page_images\\page_014.png"
}
```

Content:
PAGE 14

SELECTABLE TEXT:
Complex RAG Parsing Sample - synthetic document
Page 14
13. Edge Cases for Parsers
The following cases often break real document ingestion pipelines. They are included here as guidance for testing parser
quality before moving to embeddings and vector storage.
Edge case
Example
Recommended handling
Repeated headers and
footers
Page number, confidentiality banner
Remove or store separately as metadata
Hyphenated line breaks
termi- nation assistance
Normalize during cleaning
Rotated tables
Landscape appendix in PDF
Use layout-aware parser or OCR
Merged cells
Pricing table with grouped plans
Preserve hierarchy in row text
Scanned signatures
Signature block as image
OCR if text is needed; store image reference
Boilerplate navigation
Website header and footer
Use boilerplate removal
Duplicate chunks
Same policy in FAQ and PDF
Deduplicate using source and hash
Bad parsing creates bad chunks. Bad chunks create bad retrieval. Bad retrieval creates bad answers.

OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 15

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 15,
  "content_type": "page_text_plus_ocr",
  "image_count": 0,
  "page_image_path": "C:\\Users\\prash\\AppData\\Local\\Temp\\mmrag_parsed_a4a_k005\\page_images\\page_015.png"
}
```

Content:
PAGE 15

SELECTABLE TEXT:
Complex RAG Parsing Sample - synthetic document
Page 15
15. Final Ingestion Checklist
Use this checklist before sending parsed content into chunking and embeddings. It helps identify whether the data is ready for
production RAG.
Checklist item
Status to verify
Why it matters
Text extraction
Paragraphs are readable and ordered
Prevents noisy chunks
Table extraction
Rows, columns, headers, and footnotes
preserved
Protects factual answers
Image handling
Captions indexed and OCR done if required
Avoids missing visual information
Metadata
source, page, client_id, document_id
captured
Enables citations and access control
Chunking
Chunks preserve meaning and section
boundaries
Improves retrieval relevance
Access control
Retrieval filters use authenticated client_id
Prevents data leakage
Evaluation
Golden questions tested with citations
Measures real answer quality
Summary: RAG is about knowledge access. Fine-tuning is about behavior adaptation. For document intelligence, parsing
quality is the foundation. If extraction is weak, no embedding model or LLM can fully fix the missing context.
End of synthetic 15-page parsing test document.

OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 16

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 16,
  "content_type": "page_text_plus_ocr",
  "image_count": 1,
  "page_image_path": "C:\\Users\\prash\\AppData\\Local\\Temp\\mmrag_parsed_a4a_k005\\page_images\\page_016.png"
}
```

Content:
PAGE 16

SELECTABLE TEXT:
Complex RAG Parsing Sample - appended complex tables
Appendix page 1
Appendix A: Complex Clause Responsibility Matrix
Grouped clauses with owner/backup split inside the same responsibility cell. This page is useful for testing row
grouping, merged-looking labels, split responsibility cells, and long evidence text.
Parsing challenge: preserve row boundaries, nested headers, split cells, grouped labels, numeric values, and footnotes/context around
the table.
Table 1: Added as complex parsing appendix for table extraction, OCR fallback, and layout-aware RAG testing.

OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 17

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 17,
  "content_type": "page_text_plus_ocr",
  "image_count": 1,
  "page_image_path": "C:\\Users\\prash\\AppData\\Local\\Temp\\mmrag_parsed_a4a_k005\\page_images\\page_017.png"
}
```

Content:
PAGE 17

SELECTABLE TEXT:
Complex RAG Parsing Sample - appended complex tables
Appendix page 2
Appendix B: Regional Pricing and Usage Add-on Matrix
Pricing table with multi-level headers, regional columns, add-on columns, billing rules, exception rows, and
mixed numeric/text values.
Parsing challenge: preserve row boundaries, nested headers, split cells, grouped labels, numeric values, and footnotes/context around
the table.
Table 2: Added as complex parsing appendix for table extraction, OCR fallback, and layout-aware RAG testing.

OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 18

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 18,
  "content_type": "page_text_plus_ocr",
  "image_count": 1,
  "page_image_path": "C:\\Users\\prash\\AppData\\Local\\Temp\\mmrag_parsed_a4a_k005\\page_images\\page_018.png"
}
```

Content:
PAGE 18

SELECTABLE TEXT:
Complex RAG Parsing Sample - appended complex tables
Appendix page 3
Appendix C: Invoice Line Items with Tax Split
Invoice-style line item table with item groups, quantity, rate, CGST/SGST split, totals, and summary row. Useful
for invoice parsing and tax extraction tests.
Parsing challenge: preserve row boundaries, nested headers, split cells, grouped labels, numeric values, and footnotes/context around
the table.
Table 3: Added as complex parsing appendix for table extraction, OCR fallback, and layout-aware RAG testing.

OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 19

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 19,
  "content_type": "page_text_plus_ocr",
  "image_count": 1,
  "page_image_path": "C:\\Users\\prash\\AppData\\Local\\Temp\\mmrag_parsed_a4a_k005\\page_images\\page_019.png"
}
```

Content:
PAGE 19

SELECTABLE TEXT:
Complex RAG Parsing Sample - appended visuals and scanned documents
Appendix page 1
Appendix D: Multimodal Document Processing Flow
Diagram-style image showing how PDFs, DOCX files, scanned invoices, Excel/CSV metadata, parser/OCR,
extracted text/tables/metadata, and RAG-ready chunks connect.
Parsing challenge: image text, arrows, labels, and captions may not appear in normal PDF text extraction. OCR or multimodal
parsing may be required.
Added at the end for complex image parsing, OCR fallback, layout-aware extraction, and multimodal RAG testing.

OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 20

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 20,
  "content_type": "page_text_plus_ocr",
  "image_count": 1,
  "page_image_path": "C:\\Users\\prash\\AppData\\Local\\Temp\\mmrag_parsed_a4a_k005\\page_images\\page_020.png"
}
```

Content:
PAGE 20

SELECTABLE TEXT:
Complex RAG Parsing Sample - appended visuals and scanned documents
Appendix page 2
Appendix E: Contract Risk Dashboard Image
Dashboard-style image containing a bar chart, legend, and small matrix. Useful for testing chart extraction,
numeric value capture, and caption-aware indexing.
Parsing challenge: extract chart title, bar values, legend labels, and table values from an embedded image.
Added at the end for complex image parsing, OCR fallback, layout-aware extraction, and multimodal RAG testing.

OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 21

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 21,
  "content_type": "page_text_plus_ocr",
  "image_count": 1,
  "page_image_path": "C:\\Users\\prash\\AppData\\Local\\Temp\\mmrag_parsed_a4a_k005\\page_images\\page_021.png"
}
```

Content:
PAGE 21

SELECTABLE TEXT:
Complex RAG Parsing Sample - appended visuals and scanned documents
Appendix page 3
Appendix F: Data Lineage and Access Boundary
Image
Lineage-map style image with nodes, arrows, access boundaries, and metadata badges. Useful for diagram
OCR and relationship extraction.
Parsing challenge: diagram text must be OCRed and mapped to relationships such as user auth, namespace, retrieval, and
LLM gateway.
Added at the end for complex image parsing, OCR fallback, layout-aware extraction, and multimodal RAG testing.

OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 22

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 22,
  "content_type": "page_text_plus_ocr",
  "image_count": 1,
  "page_image_path": "C:\\Users\\prash\\AppData\\Local\\Temp\\mmrag_parsed_a4a_k005\\page_images\\page_022.png"
}
```

Content:
PAGE 22

SELECTABLE TEXT:
Complex RAG Parsing Sample - appended visuals and scanned documents
Appendix page 4
Appendix G: Additional Scanned Invoice for OCR
Testing
Synthetic scanned tax invoice with vendor details, customer details, invoice number, GSTIN, line items, tax split,
total amount, payment terms, footer notes, approval stamp, and handwritten-style receipt text.
Parsing challenge: this page is intentionally embedded as an image-like scan. A normal text parser may miss invoice values
unless OCR is enabled.
Added at the end for complex image parsing, OCR fallback, layout-aware extraction, and multimodal RAG testing.

OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 23

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 23,
  "content_type": "page_text_plus_ocr",
  "image_count": 1,
  "page_image_path": "C:\\Users\\prash\\AppData\\Local\\Temp\\mmrag_parsed_a4a_k005\\page_images\\page_023.png"
}
```

Content:
PAGE 23

SELECTABLE TEXT:
Complex RAG Parsing Sample - appended visuals and scanned documents
Appendix page 5
Appendix H: Additional Scanned Utility Bill for OCR
Testing
Synthetic scanned utility bill with meter-style charges, usage rows, tax values, total payable amount, payment
terms, stamp, handwritten-style note, and noisy/rotated scan effects.
Parsing challenge: extract bill number, issuer, line items, usage quantity, tax split, total payable, and payment notes from a
scanned image.
Added at the end for complex image parsing, OCR fallback, layout-aware extraction, and multimodal RAG testing.

OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 24

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 24,
  "content_type": "page_text_plus_ocr",
  "image_count": 1,
  "page_image_path": "C:\\Users\\prash\\AppData\\Local\\Temp\\mmrag_parsed_a4a_k005\\page_images\\page_024.png"
}
```

Content:
PAGE 24

SELECTABLE TEXT:
Complex RAG Parsing Sample - appended instructor image
Appendix page 6
Appendix I: Profile Image for Multimodal Parsing
This page adds a portrait-style image to test how a parser or multimodal RAG system handles photographic
content, captions, image metadata, and surrounding text. Text-only loaders may extract the caption but cannot
understand the visual content unless OCR, vision, or multimodal parsing is used.
Caption: Portrait-style instructor image with a bright background. Useful for testing image extraction, captioning,
person detection, layout preservation, and multimodal document understanding.
Element
Parsing Challenge
Expected Handling
Portrait image
Pixels are not selectable PDF text.
Extract image object or create visual summary with a
multimodal model.
Caption text
Caption should stay attached to image
context.
Preserve caption near the image in reading order.
Image metadata
File name, page, and bounding box may be
needed.
Store metadata for citation and retrieval.
RAG usage
Text-only chunks may miss visual details.
Use OCR or vision captioning before chunking if
visual content matters.
Added at the end for complex image parsing, multimodal RAG testing, caption grounding, and visual-content extraction checks.

OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 25

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 1,
  "content_type": "table",
  "table_index": 1,
  "table_row_count": 4,
  "table_column_count": 3,
  "table_headers": [
    "Section",
    "Parsing challenge",
    "Why it matters for RAG"
  ]
}
```

Content:
TABLE FOUND ON PAGE 1
TABLE INDEX: 1

TABLE DIMENSIONS:
Rows: 4
Columns: 3

TABLE COLUMNS:
Section, Parsing challenge, Why it matters for RAG

SEARCHABLE TABLE CONTENT:
TABLE FOUND ON PAGE 1
TABLE INDEX: 1
NUMBER OF COLUMNS: 3
NUMBER OF DATA ROWS: 4

TABLE COLUMNS:
Section, Parsing challenge, Why it matters for RAG

ROW 1:
Section = Contracts | Parsing challenge = Dense legal text, clause numbers, cross references | Why it matters for RAG = Need section-aware chunks and citations

ROW 2:
Section = Tables | Parsing challenge = Merged headers, numeric columns, footnotes | Why it matters for RAG = Need row/column preservation

ROW 3:
Section = Images | Parsing challenge = Architecture diagram, heatmap, scanned form | Why it matters for RAG = Need OCR or multimodal extraction

ROW 4:
Section = Multi-tenant metadata | Parsing challenge = client_id, document_id, contract_group_id | Why it matters for RAG = Need access-safe retrieval

TABLE MARKDOWN:
| Section               | Parsing challenge                                  | Why it matters for RAG                  |
|:----------------------|:---------------------------------------------------|:----------------------------------------|
| Contracts             | Dense legal text, clause numbers, cross references | Need section-aware chunks and citations |
| Tables                | Merged headers, numeric columns, footnotes         | Need row/column preservation            |
| Images                | Architecture diagram, heatmap, scanned form        | Need OCR or multimodal extraction       |
| Multi-tenant metadata | client_id, document_id, contract_group_id          | Need access-safe retrieval              |

---


# Document 26

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 2,
  "content_type": "table",
  "table_index": 1,
  "table_row_count": 3,
  "table_column_count": 5,
  "table_headers": [
    "Client",
    "Main document family",
    "Risk",
    "Primary users",
    "Typical question"
  ]
}
```

Content:
TABLE FOUND ON PAGE 2
TABLE INDEX: 1

TABLE DIMENSIONS:
Rows: 3
Columns: 5

TABLE COLUMNS:
Client, Main document family, Risk, Primary users, Typical question

SEARCHABLE TABLE CONTENT:
TABLE FOUND ON PAGE 2
TABLE INDEX: 1
NUMBER OF COLUMNS: 5
NUMBER OF DATA ROWS: 3

TABLE COLUMNS:
Client, Main document family, Risk, Primary users, Typical question

ROW 1:
Client = Arka Finance | Main document family = MSA, audit addendum, DPA | Risk = High | Primary users = Legal and compliance | Typical question = What audit rights exist in the DPA?

ROW 2:
Client = BlueLeaf Retail | Main document family = MSA, pricing, support SLA | Risk = Medium | Primary users = Procurement | Typical question = Which clause controls renewal pricing?

ROW 3:
Client = CityRide Mobility | Main document family = Ops reports, incident logs, SOPs | Risk = Medium | Primary users = Operations | Typical question = Which depot had repeated battery incidents?

TABLE MARKDOWN:
| Client            | Main document family             | Risk   | Primary users        | Typical question                            |
|:------------------|:---------------------------------|:-------|:---------------------|:--------------------------------------------|
| Arka Finance      | MSA, audit addendum, DPA         | High   | Legal and compliance | What audit rights exist in the DPA?         |
| BlueLeaf Retail   | MSA, pricing, support SLA        | Medium | Procurement          | Which clause controls renewal pricing?      |
| CityRide Mobility | Ops reports, incident logs, SOPs | Medium | Operations           | Which depot had repeated battery incidents? |

---


# Document 27

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 3,
  "content_type": "table",
  "table_index": 1,
  "table_row_count": 8,
  "table_column_count": 6,
  "table_headers": [
    "Asset ID",
    "Client",
    "Format",
    "Pages/Rows",
    "Expected extraction",
    "Notes"
  ]
}
```

Content:
TABLE FOUND ON PAGE 3
TABLE INDEX: 1

TABLE DIMENSIONS:
Rows: 8
Columns: 6

TABLE COLUMNS:
Asset ID, Client, Format, Pages/Rows, Expected extraction, Notes

SEARCHABLE TABLE CONTENT:
TABLE FOUND ON PAGE 3
TABLE INDEX: 1
NUMBER OF COLUMNS: 6
NUMBER OF DATA ROWS: 8

TABLE COLUMNS:
Asset ID, Client, Format, Pages/Rows, Expected extraction, Notes

ROW 1:
Asset ID = ARK-MSA-001 | Client = Arka Finance | Format = PDF | Pages/Rows = 32 pages | Expected extraction = Clauses, tables, signatures | Notes = Born-digital text with footer references

ROW 2:
Asset ID = ARK-DPA-002 | Client = Arka Finance | Format = DOCX | Pages/Rows = 18 pages | Expected extraction = Headings, lists, tables | Notes = Track changes removed before ingestion

ROW 3:
Asset ID = BLR-PRICE-00 3 | Client = BlueLeaf Retail | Format = XLSX | Pages/Rows = 12 sheets | Expected extraction = Rate cards, discounts | Notes = Merged cells and formulas

ROW 4:
Asset ID = BLR-SLA-004 | Client = BlueLeaf Retail | Format = PDF | Pages/Rows = 9 pages | Expected extraction = SLA table, escalation matrix | Notes = Table crosses page boundary

ROW 5:
Asset ID = CRM-OPS-005 | Client = CityRide Mobility | Format = CSV | Pages/Rows = 48,200 rows | Expected extraction = Incident records | Notes = Needs column type normalization

ROW 6:
Asset ID = CRM-FORM-00 6 | Client = CityRide Mobility | Format = Scanned PDF | Pages/Rows = 4 pages | Expected extraction = OCR fields, checkbox | Notes = Low contrast and slight rotation

ROW 7:
Asset ID = KB-RUN-007 | Client = Shared | Format = Markdown | Pages/Rows = 14 files | Expected extraction = Runbook sections | Notes = Good for heading-based chunks

ROW 8:
Asset ID = WEB-FAQ-008 | Client = Shared | Format = HTML | Pages/Rows = 23 pages | Expected extraction = FAQ content, links | Notes = Needs boilerplate removal

TABLE MARKDOWN:
| Asset ID       | Client            | Format      | Pages/Rows   | Expected extraction          | Notes                                    |
|:---------------|:------------------|:------------|:-------------|:-----------------------------|:-----------------------------------------|
| ARK-MSA-001    | Arka Finance      | PDF         | 32 pages     | Clauses, tables, signatures  | Born-digital text with footer references |
| ARK-DPA-002    | Arka Finance      | DOCX        | 18 pages     | Headings, lists, tables      | Track changes removed before ingestion   |
| BLR-PRICE-00 3 | BlueLeaf Retail   | XLSX        | 12 sheets    | Rate cards, discounts        | Merged cells and formulas                |
| BLR-SLA-004    | BlueLeaf Retail   | PDF         | 9 pages      | SLA table, escalation matrix | Table crosses page boundary              |
| CRM-OPS-005    | CityRide Mobility | CSV         | 48,200 rows  | Incident records             | Needs column type normalization          |
| CRM-FORM-00 6  | CityRide Mobility | Scanned PDF | 4 pages      | OCR fields, checkbox         | Low contrast and slight rotation         |
| KB-RUN-007     | Shared            | Markdown    | 14 files     | Runbook sections             | Good for heading-based chunks            |
| WEB-FAQ-008    | Shared            | HTML        | 23 pages     | FAQ content, links           | Needs boilerplate removal                |

---


# Document 28

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 4,
  "content_type": "table",
  "table_index": 1,
  "table_row_count": 3,
  "table_column_count": 6,
  "table_headers": [
    "Clause",
    "Short name",
    "Owner",
    "Trigger",
    "Required action",
    "Citation hint"
  ]
}
```

Content:
TABLE FOUND ON PAGE 4
TABLE INDEX: 1

TABLE DIMENSIONS:
Rows: 3
Columns: 6

TABLE COLUMNS:
Clause, Short name, Owner, Trigger, Required action, Citation hint

SEARCHABLE TABLE CONTENT:
TABLE FOUND ON PAGE 4
TABLE INDEX: 1
NUMBER OF COLUMNS: 6
NUMBER OF DATA ROWS: 3

TABLE COLUMNS:
Clause, Short name, Owner, Trigger, Required action, Citation hint

ROW 1:
Clause = 7.2 | Short name = Confidentiality | Owner = Receiving Party | Trigger = Receipt of confidential material | Required action = Protect information with reasonable care and equivalent internal controls | Citation hint = Page 4, clause 7.2

ROW 2:
Clause = 9.1 | Short name = Data residency | Owner = Service Provider | Trigger = SOW specifies region | Required action = Process production records only in approved region | Citation hint = Page 4, clause 9.1

ROW 3:
Clause = 11.4 | Short name = Termination assistance | Owner = Service Provider | Trigger = Agreement termination | Required action = Provide export window for 30 days | Citation hint = Page 4, clause 11.4

TABLE MARKDOWN:
|   Clause | Short name             | Owner            | Trigger                          | Required action                                                           | Citation hint       |
|---------:|:-----------------------|:-----------------|:---------------------------------|:--------------------------------------------------------------------------|:--------------------|
|      7.2 | Confidentiality        | Receiving Party  | Receipt of confidential material | Protect information with reasonable care and equivalent internal controls | Page 4, clause 7.2  |
|      9.1 | Data residency         | Service Provider | SOW specifies region             | Process production records only in approved region                        | Page 4, clause 9.1  |
|     11.4 | Termination assistance | Service Provider | Agreement termination            | Provide export window for 30 days                                         | Page 4, clause 11.4 |

---


# Document 29

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 5,
  "content_type": "table",
  "table_index": 1,
  "table_row_count": 5,
  "table_column_count": 4,
  "table_headers": [
    "Policy Area",
    "Rule",
    "Owner",
    "Review Cycle"
  ]
}
```

Content:
TABLE FOUND ON PAGE 5
TABLE INDEX: 1

TABLE DIMENSIONS:
Rows: 5
Columns: 4

TABLE COLUMNS:
Policy Area, Rule, Owner, Review Cycle

SEARCHABLE TABLE CONTENT:
TABLE FOUND ON PAGE 5
TABLE INDEX: 1
NUMBER OF COLUMNS: 4
NUMBER OF DATA ROWS: 5

TABLE COLUMNS:
Policy Area, Rule, Owner, Review Cycle

ROW 1:
Policy Area = Refunds | Rule = Refund requests must be raised within 7 days of purchase. | Owner = Customer Support | Review Cycle = Quarterly

ROW 2:
Policy Area = Data Export | Rule = Client admins can request export in CSV or JSON format. | Owner = Platform Ops | Review Cycle = Monthly

ROW 3:
Policy Area = Access Review | Rule = Privileged access must be reviewed every 30 days. | Owner = Security | Review Cycle = Monthly

ROW 4:
Policy Area = Incident Response | Rule = Critical incidents require acknowledgement within 30 minutes. | Owner = SRE | Review Cycle = After each incident

ROW 5:
Policy Area = Vendor Review | Rule = High-risk vendors require annual risk assessment. | Owner = Procurement | Review Cycle = Annual

TABLE MARKDOWN:
| Policy Area       | Rule                                                          | Owner            | Review Cycle        |
|:------------------|:--------------------------------------------------------------|:-----------------|:--------------------|
| Refunds           | Refund requests must be raised within 7 days of purchase.     | Customer Support | Quarterly           |
| Data Export       | Client admins can request export in CSV or JSON format.       | Platform Ops     | Monthly             |
| Access Review     | Privileged access must be reviewed every 30 days.             | Security         | Monthly             |
| Incident Response | Critical incidents require acknowledgement within 30 minutes. | SRE              | After each incident |
| Vendor Review     | High-risk vendors require annual risk assessment.             | Procurement      | Annual              |

---


# Document 30

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 6,
  "content_type": "table",
  "table_index": 1,
  "table_row_count": 5,
  "table_column_count": 6,
  "table_headers": [
    "Service Category",
    "Severity",
    "Response Target",
    "Resolution Target",
    "Service Credit",
    "Evidence Required"
  ]
}
```

Content:
TABLE FOUND ON PAGE 6
TABLE INDEX: 1

TABLE DIMENSIONS:
Rows: 5
Columns: 6

TABLE COLUMNS:
Service Category, Severity, Response Target, Resolution Target, Service Credit, Evidence Required

SEARCHABLE TABLE CONTENT:
TABLE FOUND ON PAGE 6
TABLE INDEX: 1
NUMBER OF COLUMNS: 6
NUMBER OF DATA ROWS: 5

TABLE COLUMNS:
Service Category, Severity, Response Target, Resolution Target, Service Credit, Evidence Required

ROW 1:
Service Category = API Availability | Severity = P1 - complete outage | Response Target = 15 minutes | Resolution Target = 4 hours | Service Credit = 10 percent monthly fee credit | Evidence Required = Monitoring logs and incident ticket

ROW 2:
Service Category = API Availability | Severity = P2 - degraded performance | Response Target = 30 minutes | Resolution Target = 8 hours | Service Credit = 5 percent monthly fee credit | Evidence Required = Latency dashboard and affected endpoint list

ROW 3:
Service Category = Data Pipeline | Severity = P1 - ingestion stopped | Response Target = 20 minutes | Resolution Target = 6 hours | Service Credit = 8 percent pipeline fee credit | Evidence Required = Queue depth, failed job IDs, replay report

ROW 4:
Service Category = Data Pipeline | Severity = P3 - delayed batch | Response Target = 4 hours | Resolution Target = Next business day | Service Credit = No automatic credit | Evidence Required = Batch ID and SLA exception note

ROW 5:
Service Category = Support | Severity = P2 - urgent support | Response Target = 1 hour | Resolution Target = 1 business day | Service Credit = 2 percent support fee credit | Evidence Required = Support ticket with timestamps

TABLE MARKDOWN:
| Service Category   | Severity                  | Response Target   | Resolution Target   | Service Credit                | Evidence Required                            |
|:-------------------|:--------------------------|:------------------|:--------------------|:------------------------------|:---------------------------------------------|
| API Availability   | P1 - complete outage      | 15 minutes        | 4 hours             | 10 percent monthly fee credit | Monitoring logs and incident ticket          |
| API Availability   | P2 - degraded performance | 30 minutes        | 8 hours             | 5 percent monthly fee credit  | Latency dashboard and affected endpoint list |
| Data Pipeline      | P1 - ingestion stopped    | 20 minutes        | 6 hours             | 8 percent pipeline fee credit | Queue depth, failed job IDs, replay report   |
| Data Pipeline      | P3 - delayed batch        | 4 hours           | Next business day   | No automatic credit           | Batch ID and SLA exception note              |
| Support            | P2 - urgent support       | 1 hour            | 1 business day      | 2 percent support fee credit  | Support ticket with timestamps               |

---


# Document 31

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 7,
  "content_type": "table",
  "table_index": 1,
  "table_row_count": 3,
  "table_column_count": 3,
  "table_headers": [
    "Image element",
    "Potential extraction method",
    "Expected output"
  ]
}
```

Content:
TABLE FOUND ON PAGE 7
TABLE INDEX: 1

TABLE DIMENSIONS:
Rows: 3
Columns: 3

TABLE COLUMNS:
Image element, Potential extraction method, Expected output

SEARCHABLE TABLE CONTENT:
TABLE FOUND ON PAGE 7
TABLE INDEX: 1
NUMBER OF COLUMNS: 3
NUMBER OF DATA ROWS: 3

TABLE COLUMNS:
Image element, Potential extraction method, Expected output

ROW 1:
Image element = Box labels | Potential extraction method = OCR or vision model | Expected output = Raw Files, Parser, Chunks, Vector DB

ROW 2:
Image element = Arrows | Potential extraction method = Layout or vision understanding | Expected output = Processing order

ROW 3:
Image element = Caption | Potential extraction method = Normal PDF text extraction | Expected output = Description of the diagram

TABLE MARKDOWN:
| Image element   | Potential extraction method    | Expected output                      |
|:----------------|:-------------------------------|:-------------------------------------|
| Box labels      | OCR or vision model            | Raw Files, Parser, Chunks, Vector DB |
| Arrows          | Layout or vision understanding | Processing order                     |
| Caption         | Normal PDF text extraction     | Description of the diagram           |

---


# Document 32

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 8,
  "content_type": "table",
  "table_index": 1,
  "table_row_count": 3,
  "table_column_count": 3,
  "table_headers": [
    "Runbook field",
    "Value",
    "Parsing expectation"
  ]
}
```

Content:
TABLE FOUND ON PAGE 8
TABLE INDEX: 1

TABLE DIMENSIONS:
Rows: 3
Columns: 3

TABLE COLUMNS:
Runbook field, Value, Parsing expectation

SEARCHABLE TABLE CONTENT:
TABLE FOUND ON PAGE 8
TABLE INDEX: 1
NUMBER OF COLUMNS: 3
NUMBER OF DATA ROWS: 3

TABLE COLUMNS:
Runbook field, Value, Parsing expectation

ROW 1:
Runbook field = Title | Value = Contract Ingestion Failure | Parsing expectation = Should become section title metadata

ROW 2:
Runbook field = Symptoms | Value = Five bullet items | Parsing expectation = Should remain as list or separate lines

ROW 3:
Runbook field = Recovery Steps | Value = Numbered sequence | Parsing expectation = Order must be preserved

TABLE MARKDOWN:
| Runbook field   | Value                      | Parsing expectation                     |
|:----------------|:---------------------------|:----------------------------------------|
| Title           | Contract Ingestion Failure | Should become section title metadata    |
| Symptoms        | Five bullet items          | Should remain as list or separate lines |
| Recovery Steps  | Numbered sequence          | Order must be preserved                 |

---


# Document 33

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 9,
  "content_type": "table",
  "table_index": 1,
  "table_row_count": 4,
  "table_column_count": 3,
  "table_headers": [
    "Field",
    "Expected OCR value",
    "Validation rule"
  ]
}
```

Content:
TABLE FOUND ON PAGE 9
TABLE INDEX: 1

TABLE DIMENSIONS:
Rows: 4
Columns: 3

TABLE COLUMNS:
Field, Expected OCR value, Validation rule

SEARCHABLE TABLE CONTENT:
TABLE FOUND ON PAGE 9
TABLE INDEX: 1
NUMBER OF COLUMNS: 3
NUMBER OF DATA ROWS: 4

TABLE COLUMNS:
Field, Expected OCR value, Validation rule

ROW 1:
Field = Client Name | Expected OCR value = BlueLeaf Retail Pvt Ltd | Validation rule = Must match known client list

ROW 2:
Field = Contract ID | Expected OCR value = BLR-MSA-2026-019 | Validation rule = Pattern: client-code + type + year + sequence

ROW 3:
Field = Effective Date | Expected OCR value = 01 Apr 2026 | Validation rule = Date parser should normalize to ISO format

ROW 4:
Field = Approval checkbox | Expected OCR value = Checked | Validation rule = Boolean extraction required

TABLE MARKDOWN:
| Field             | Expected OCR value      | Validation rule                               |
|:------------------|:------------------------|:----------------------------------------------|
| Client Name       | BlueLeaf Retail Pvt Ltd | Must match known client list                  |
| Contract ID       | BLR-MSA-2026-019        | Pattern: client-code + type + year + sequence |
| Effective Date    | 01 Apr 2026             | Date parser should normalize to ISO format    |
| Approval checkbox | Checked                 | Boolean extraction required                   |

---


# Document 34

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 10,
  "content_type": "table",
  "table_index": 1,
  "table_row_count": 5,
  "table_column_count": 5,
  "table_headers": [
    "document_id",
    "document_type",
    "contract_group_id",
    "effective_date",
    "relationship"
  ]
}
```

Content:
TABLE FOUND ON PAGE 10
TABLE INDEX: 1

TABLE DIMENSIONS:
Rows: 5
Columns: 5

TABLE COLUMNS:
document_id, document_type, contract_group_id, effective_date, relationship

SEARCHABLE TABLE CONTENT:
TABLE FOUND ON PAGE 10
TABLE INDEX: 1
NUMBER OF COLUMNS: 5
NUMBER OF DATA ROWS: 5

TABLE COLUMNS:
document_id, document_type, contract_group_id, effective_date, relationship

ROW 1:
document_id = BLR-MSA-001 | document_type = Master Service Agreement | contract_group_id = BLR-ACME-2026 | effective_date = 2026-04-01 | relationship = Base commercial agreement

ROW 2:
document_id = BLR-NDA-002 | document_type = NDA | contract_group_id = BLR-ACME-2026 | effective_date = 2026-04-01 | relationship = Confidentiality terms

ROW 3:
document_id = BLR-SOW-003 | document_type = Statement of Work | contract_group_id = BLR-ACME-2026 | effective_date = 2026-04-15 | relationship = Project scope and deliverables

ROW 4:
document_id = BLR-PRICE-004 | document_type = Pricing Amendment | contract_group_id = BLR-ACME-2026 | effective_date = 2026-05-01 | relationship = Updated pricing and discount tiers

ROW 5:
document_id = BLR-SLA-005 | document_type = Support SLA | contract_group_id = BLR-ACME-2026 | effective_date = 2026-05-10 | relationship = Support response and credits

TABLE MARKDOWN:
| document_id   | document_type            | contract_group_id   | effective_date   | relationship                       |
|:--------------|:-------------------------|:--------------------|:-----------------|:-----------------------------------|
| BLR-MSA-001   | Master Service Agreement | BLR-ACME-2026       | 2026-04-01       | Base commercial agreement          |
| BLR-NDA-002   | NDA                      | BLR-ACME-2026       | 2026-04-01       | Confidentiality terms              |
| BLR-SOW-003   | Statement of Work        | BLR-ACME-2026       | 2026-04-15       | Project scope and deliverables     |
| BLR-PRICE-004 | Pricing Amendment        | BLR-ACME-2026       | 2026-05-01       | Updated pricing and discount tiers |
| BLR-SLA-005   | Support SLA              | BLR-ACME-2026       | 2026-05-10       | Support response and credits       |

---


# Document 35

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 11,
  "content_type": "table",
  "table_index": 1,
  "table_row_count": 5,
  "table_column_count": 3,
  "table_headers": [
    "Layer",
    "Control",
    "Failure mode if missing"
  ]
}
```

Content:
TABLE FOUND ON PAGE 11
TABLE INDEX: 1

TABLE DIMENSIONS:
Rows: 5
Columns: 3

TABLE COLUMNS:
Layer, Control, Failure mode if missing

SEARCHABLE TABLE CONTENT:
TABLE FOUND ON PAGE 11
TABLE INDEX: 1
NUMBER OF COLUMNS: 3
NUMBER OF DATA ROWS: 5

TABLE COLUMNS:
Layer, Control, Failure mode if missing

ROW 1:
Layer = Authentication | Control = Identify user and organization | Failure mode if missing = Unknown user may access application

ROW 2:
Layer = Authorization | Control = Map user to client_id and role | Failure mode if missing = User may retrieve another clients documents

ROW 3:
Layer = Vector retrieval | Control = Filter by client_id or namespace | Failure mode if missing = Retriever may return unauthorized chunks

ROW 4:
Layer = Prompt construction | Control = Send only allowed context | Failure mode if missing = LLM may see sensitive data

ROW 5:
Layer = Audit logging | Control = Record query, source chunks, user_id | Failure mode if missing = No traceability during incident review

TABLE MARKDOWN:
| Layer               | Control                              | Failure mode if missing                     |
|:--------------------|:-------------------------------------|:--------------------------------------------|
| Authentication      | Identify user and organization       | Unknown user may access application         |
| Authorization       | Map user to client_id and role       | User may retrieve another clients documents |
| Vector retrieval    | Filter by client_id or namespace     | Retriever may return unauthorized chunks    |
| Prompt construction | Send only allowed context            | LLM may see sensitive data                  |
| Audit logging       | Record query, source chunks, user_id | No traceability during incident review      |

---


# Document 36

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 12,
  "content_type": "table",
  "table_index": 1,
  "table_row_count": 3,
  "table_column_count": 3,
  "table_headers": [
    "Observation",
    "Supporting value",
    "Scheduling implication"
  ]
}
```

Content:
TABLE FOUND ON PAGE 12
TABLE INDEX: 1

TABLE DIMENSIONS:
Rows: 3
Columns: 3

TABLE COLUMNS:
Observation, Supporting value, Scheduling implication

SEARCHABLE TABLE CONTENT:
TABLE FOUND ON PAGE 12
TABLE INDEX: 1
NUMBER OF COLUMNS: 3
NUMBER OF DATA ROWS: 3

TABLE COLUMNS:
Observation, Supporting value, Scheduling implication

ROW 1:
Observation = Prime Friday performs best | Supporting value = 93 retention score | Scheduling implication = Place premium content in Friday late/prime slots

ROW 2:
Observation = Early week late slots underperform | Supporting value = 10 to 21 score range | Scheduling implication = Avoid launching new series in weak slots

ROW 3:
Observation = Evening improves midweek | Supporting value = 77 on Wednesday evening | Scheduling implication = Use midweek evening for discovery content

TABLE MARKDOWN:
| Observation                        | Supporting value        | Scheduling implication                           |
|:-----------------------------------|:------------------------|:-------------------------------------------------|
| Prime Friday performs best         | 93 retention score      | Place premium content in Friday late/prime slots |
| Early week late slots underperform | 10 to 21 score range    | Avoid launching new series in weak slots         |
| Evening improves midweek           | 77 on Wednesday evening | Use midweek evening for discovery content        |

---


# Document 37

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 13,
  "content_type": "table",
  "table_index": 1,
  "table_row_count": 5,
  "table_column_count": 5,
  "table_headers": [
    "Test ID",
    "Question",
    "Expected source",
    "Expected answer element",
    "Failure signal"
  ]
}
```

Content:
TABLE FOUND ON PAGE 13
TABLE INDEX: 1

TABLE DIMENSIONS:
Rows: 5
Columns: 5

TABLE COLUMNS:
Test ID, Question, Expected source, Expected answer element, Failure signal

SEARCHABLE TABLE CONTENT:
TABLE FOUND ON PAGE 13
TABLE INDEX: 1
NUMBER OF COLUMNS: 5
NUMBER OF DATA ROWS: 5

TABLE COLUMNS:
Test ID, Question, Expected source, Expected answer element, Failure signal

ROW 1:
Test ID = Q-001 | Question = What is the refund window? | Expected source = Policy Rules table | Expected answer element = 7 days | Failure signal = Answer says 30 days

ROW 2:
Test ID = Q-002 | Question = Which clause covers data residency? | Expected source = Clause 9.1 | Expected answer element = Approved processing region | Failure signal = No clause citation

ROW 3:
Test ID = Q-003 | Question = What is P1 API response target? | Expected source = SLA table | Expected answer element = 15 minutes | Failure signal = Wrong severity row

ROW 4:
Test ID = Q-004 | Question = Which documents belong to BLR-ACME-2026? | Expected source = Relationship table | Expected answer element = Five related documents | Failure signal = Only one document returned

ROW 5:
Test ID = Q-005 | Question = Who owns access review? | Expected source = Policy Rules table | Expected answer element = Security | Failure signal = Owner missing

TABLE MARKDOWN:
| Test ID   | Question                                 | Expected source    | Expected answer element    | Failure signal             |
|:----------|:-----------------------------------------|:-------------------|:---------------------------|:---------------------------|
| Q-001     | What is the refund window?               | Policy Rules table | 7 days                     | Answer says 30 days        |
| Q-002     | Which clause covers data residency?      | Clause 9.1         | Approved processing region | No clause citation         |
| Q-003     | What is P1 API response target?          | SLA table          | 15 minutes                 | Wrong severity row         |
| Q-004     | Which documents belong to BLR-ACME-2026? | Relationship table | Five related documents     | Only one document returned |
| Q-005     | Who owns access review?                  | Policy Rules table | Security                   | Owner missing              |

---


# Document 38

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 14,
  "content_type": "table",
  "table_index": 1,
  "table_row_count": 7,
  "table_column_count": 3,
  "table_headers": [
    "Edge case",
    "Example",
    "Recommended handling"
  ]
}
```

Content:
TABLE FOUND ON PAGE 14
TABLE INDEX: 1

TABLE DIMENSIONS:
Rows: 7
Columns: 3

TABLE COLUMNS:
Edge case, Example, Recommended handling

SEARCHABLE TABLE CONTENT:
TABLE FOUND ON PAGE 14
TABLE INDEX: 1
NUMBER OF COLUMNS: 3
NUMBER OF DATA ROWS: 7

TABLE COLUMNS:
Edge case, Example, Recommended handling

ROW 1:
Edge case = Repeated headers and footers | Example = Page number, confidentiality banner | Recommended handling = Remove or store separately as metadata

ROW 2:
Edge case = Hyphenated line breaks | Example = termi- nation assistance | Recommended handling = Normalize during cleaning

ROW 3:
Edge case = Rotated tables | Example = Landscape appendix in PDF | Recommended handling = Use layout-aware parser or OCR

ROW 4:
Edge case = Merged cells | Example = Pricing table with grouped plans | Recommended handling = Preserve hierarchy in row text

ROW 5:
Edge case = Scanned signatures | Example = Signature block as image | Recommended handling = OCR if text is needed; store image reference

ROW 6:
Edge case = Boilerplate navigation | Example = Website header and footer | Recommended handling = Use boilerplate removal

ROW 7:
Edge case = Duplicate chunks | Example = Same policy in FAQ and PDF | Recommended handling = Deduplicate using source and hash

TABLE MARKDOWN:
| Edge case                    | Example                             | Recommended handling                         |
|:-----------------------------|:------------------------------------|:---------------------------------------------|
| Repeated headers and footers | Page number, confidentiality banner | Remove or store separately as metadata       |
| Hyphenated line breaks       | termi- nation assistance            | Normalize during cleaning                    |
| Rotated tables               | Landscape appendix in PDF           | Use layout-aware parser or OCR               |
| Merged cells                 | Pricing table with grouped plans    | Preserve hierarchy in row text               |
| Scanned signatures           | Signature block as image            | OCR if text is needed; store image reference |
| Boilerplate navigation       | Website header and footer           | Use boilerplate removal                      |
| Duplicate chunks             | Same policy in FAQ and PDF          | Deduplicate using source and hash            |

---


# Document 39

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 15,
  "content_type": "table",
  "table_index": 1,
  "table_row_count": 7,
  "table_column_count": 3,
  "table_headers": [
    "Checklist item",
    "Status to verify",
    "Why it matters"
  ]
}
```

Content:
TABLE FOUND ON PAGE 15
TABLE INDEX: 1

TABLE DIMENSIONS:
Rows: 7
Columns: 3

TABLE COLUMNS:
Checklist item, Status to verify, Why it matters

SEARCHABLE TABLE CONTENT:
TABLE FOUND ON PAGE 15
TABLE INDEX: 1
NUMBER OF COLUMNS: 3
NUMBER OF DATA ROWS: 7

TABLE COLUMNS:
Checklist item, Status to verify, Why it matters

ROW 1:
Checklist item = Text extraction | Status to verify = Paragraphs are readable and ordered | Why it matters = Prevents noisy chunks

ROW 2:
Checklist item = Table extraction | Status to verify = Rows, columns, headers, and footnotes preserved | Why it matters = Protects factual answers

ROW 3:
Checklist item = Image handling | Status to verify = Captions indexed and OCR done if required | Why it matters = Avoids missing visual information

ROW 4:
Checklist item = Metadata | Status to verify = source, page, client_id, document_id captured | Why it matters = Enables citations and access control

ROW 5:
Checklist item = Chunking | Status to verify = Chunks preserve meaning and section boundaries | Why it matters = Improves retrieval relevance

ROW 6:
Checklist item = Access control | Status to verify = Retrieval filters use authenticated client_id | Why it matters = Prevents data leakage

ROW 7:
Checklist item = Evaluation | Status to verify = Golden questions tested with citations | Why it matters = Measures real answer quality

TABLE MARKDOWN:
| Checklist item   | Status to verify                                | Why it matters                       |
|:-----------------|:------------------------------------------------|:-------------------------------------|
| Text extraction  | Paragraphs are readable and ordered             | Prevents noisy chunks                |
| Table extraction | Rows, columns, headers, and footnotes preserved | Protects factual answers             |
| Image handling   | Captions indexed and OCR done if required       | Avoids missing visual information    |
| Metadata         | source, page, client_id, document_id captured   | Enables citations and access control |
| Chunking         | Chunks preserve meaning and section boundaries  | Improves retrieval relevance         |
| Access control   | Retrieval filters use authenticated client_id   | Prevents data leakage                |
| Evaluation       | Golden questions tested with citations          | Measures real answer quality         |

---


# Document 40

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 24,
  "content_type": "table",
  "table_index": 1,
  "table_row_count": 4,
  "table_column_count": 3,
  "table_headers": [
    "Element",
    "Parsing Challenge",
    "Expected Handling"
  ]
}
```

Content:
TABLE FOUND ON PAGE 24
TABLE INDEX: 1

TABLE DIMENSIONS:
Rows: 4
Columns: 3

TABLE COLUMNS:
Element, Parsing Challenge, Expected Handling

SEARCHABLE TABLE CONTENT:
TABLE FOUND ON PAGE 24
TABLE INDEX: 1
NUMBER OF COLUMNS: 3
NUMBER OF DATA ROWS: 4

TABLE COLUMNS:
Element, Parsing Challenge, Expected Handling

ROW 1:
Element = Portrait image | Parsing Challenge = Pixels are not selectable PDF text. | Expected Handling = Extract image object or create visual summary with a multimodal model.

ROW 2:
Element = Caption text | Parsing Challenge = Caption should stay attached to image context. | Expected Handling = Preserve caption near the image in reading order.

ROW 3:
Element = Image metadata | Parsing Challenge = File name, page, and bounding box may be needed. | Expected Handling = Store metadata for citation and retrieval.

ROW 4:
Element = RAG usage | Parsing Challenge = Text-only chunks may miss visual details. | Expected Handling = Use OCR or vision captioning before chunking if visual content matters.

TABLE MARKDOWN:
| Element        | Parsing Challenge                                | Expected Handling                                                       |
|:---------------|:-------------------------------------------------|:------------------------------------------------------------------------|
| Portrait image | Pixels are not selectable PDF text.              | Extract image object or create visual summary with a multimodal model.  |
| Caption text   | Caption should stay attached to image context.   | Preserve caption near the image in reading order.                       |
| Image metadata | File name, page, and bounding box may be needed. | Store metadata for citation and retrieval.                              |
| RAG usage      | Text-only chunks may miss visual details.        | Use OCR or vision captioning before chunking if visual content matters. |

---


# Document 41

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 2,
  "content_type": "image",
  "image_index": 1,
  "image_path": "C:\\Users\\prash\\AppData\\Local\\Temp\\mmrag_parsed_a4a_k005\\extracted_images\\page_002_image_1.png",
  "image_ext": "png"
}
```

Content:
IMAGE FOUND ON PAGE 2
IMAGE INDEX: 1
IMAGE PATH: C:\Users\prash\AppData\Local\Temp\mmrag_parsed_a4a_k005\extracted_images\page_002_image_1.png

IMAGE OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 42

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 7,
  "content_type": "image",
  "image_index": 1,
  "image_path": "C:\\Users\\prash\\AppData\\Local\\Temp\\mmrag_parsed_a4a_k005\\extracted_images\\page_007_image_1.png",
  "image_ext": "png"
}
```

Content:
IMAGE FOUND ON PAGE 7
IMAGE INDEX: 1
IMAGE PATH: C:\Users\prash\AppData\Local\Temp\mmrag_parsed_a4a_k005\extracted_images\page_007_image_1.png

IMAGE OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 43

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 9,
  "content_type": "image",
  "image_index": 1,
  "image_path": "C:\\Users\\prash\\AppData\\Local\\Temp\\mmrag_parsed_a4a_k005\\extracted_images\\page_009_image_1.png",
  "image_ext": "png"
}
```

Content:
IMAGE FOUND ON PAGE 9
IMAGE INDEX: 1
IMAGE PATH: C:\Users\prash\AppData\Local\Temp\mmrag_parsed_a4a_k005\extracted_images\page_009_image_1.png

IMAGE OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 44

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 12,
  "content_type": "image",
  "image_index": 1,
  "image_path": "C:\\Users\\prash\\AppData\\Local\\Temp\\mmrag_parsed_a4a_k005\\extracted_images\\page_012_image_1.png",
  "image_ext": "png"
}
```

Content:
IMAGE FOUND ON PAGE 12
IMAGE INDEX: 1
IMAGE PATH: C:\Users\prash\AppData\Local\Temp\mmrag_parsed_a4a_k005\extracted_images\page_012_image_1.png

IMAGE OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 45

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 16,
  "content_type": "image",
  "image_index": 1,
  "image_path": "C:\\Users\\prash\\AppData\\Local\\Temp\\mmrag_parsed_a4a_k005\\extracted_images\\page_016_image_1.png",
  "image_ext": "png"
}
```

Content:
IMAGE FOUND ON PAGE 16
IMAGE INDEX: 1
IMAGE PATH: C:\Users\prash\AppData\Local\Temp\mmrag_parsed_a4a_k005\extracted_images\page_016_image_1.png

IMAGE OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 46

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 17,
  "content_type": "image",
  "image_index": 1,
  "image_path": "C:\\Users\\prash\\AppData\\Local\\Temp\\mmrag_parsed_a4a_k005\\extracted_images\\page_017_image_1.png",
  "image_ext": "png"
}
```

Content:
IMAGE FOUND ON PAGE 17
IMAGE INDEX: 1
IMAGE PATH: C:\Users\prash\AppData\Local\Temp\mmrag_parsed_a4a_k005\extracted_images\page_017_image_1.png

IMAGE OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 47

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 18,
  "content_type": "image",
  "image_index": 1,
  "image_path": "C:\\Users\\prash\\AppData\\Local\\Temp\\mmrag_parsed_a4a_k005\\extracted_images\\page_018_image_1.png",
  "image_ext": "png"
}
```

Content:
IMAGE FOUND ON PAGE 18
IMAGE INDEX: 1
IMAGE PATH: C:\Users\prash\AppData\Local\Temp\mmrag_parsed_a4a_k005\extracted_images\page_018_image_1.png

IMAGE OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 48

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 19,
  "content_type": "image",
  "image_index": 1,
  "image_path": "C:\\Users\\prash\\AppData\\Local\\Temp\\mmrag_parsed_a4a_k005\\extracted_images\\page_019_image_1.png",
  "image_ext": "png"
}
```

Content:
IMAGE FOUND ON PAGE 19
IMAGE INDEX: 1
IMAGE PATH: C:\Users\prash\AppData\Local\Temp\mmrag_parsed_a4a_k005\extracted_images\page_019_image_1.png

IMAGE OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 49

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 20,
  "content_type": "image",
  "image_index": 1,
  "image_path": "C:\\Users\\prash\\AppData\\Local\\Temp\\mmrag_parsed_a4a_k005\\extracted_images\\page_020_image_1.png",
  "image_ext": "png"
}
```

Content:
IMAGE FOUND ON PAGE 20
IMAGE INDEX: 1
IMAGE PATH: C:\Users\prash\AppData\Local\Temp\mmrag_parsed_a4a_k005\extracted_images\page_020_image_1.png

IMAGE OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 50

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 21,
  "content_type": "image",
  "image_index": 1,
  "image_path": "C:\\Users\\prash\\AppData\\Local\\Temp\\mmrag_parsed_a4a_k005\\extracted_images\\page_021_image_1.png",
  "image_ext": "png"
}
```

Content:
IMAGE FOUND ON PAGE 21
IMAGE INDEX: 1
IMAGE PATH: C:\Users\prash\AppData\Local\Temp\mmrag_parsed_a4a_k005\extracted_images\page_021_image_1.png

IMAGE OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 51

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 22,
  "content_type": "image",
  "image_index": 1,
  "image_path": "C:\\Users\\prash\\AppData\\Local\\Temp\\mmrag_parsed_a4a_k005\\extracted_images\\page_022_image_1.png",
  "image_ext": "png"
}
```

Content:
IMAGE FOUND ON PAGE 22
IMAGE INDEX: 1
IMAGE PATH: C:\Users\prash\AppData\Local\Temp\mmrag_parsed_a4a_k005\extracted_images\page_022_image_1.png

IMAGE OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 52

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 23,
  "content_type": "image",
  "image_index": 1,
  "image_path": "C:\\Users\\prash\\AppData\\Local\\Temp\\mmrag_parsed_a4a_k005\\extracted_images\\page_023_image_1.png",
  "image_ext": "png"
}
```

Content:
IMAGE FOUND ON PAGE 23
IMAGE INDEX: 1
IMAGE PATH: C:\Users\prash\AppData\Local\Temp\mmrag_parsed_a4a_k005\extracted_images\page_023_image_1.png

IMAGE OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---


# Document 53

Metadata:
```json
{
  "source": "D:\\mm-rag-full-stack-genai-bootcamp-1.0-master\\mm-rag-full-stack-genai-bootcamp-1.0-master\\data\\uploads\\481350d0f2fd4d3990b086365bca36e4_Client_Contracts_Policies_and_Incident_Records.pdf",
  "page_number": 24,
  "content_type": "image",
  "image_index": 1,
  "image_path": "C:\\Users\\prash\\AppData\\Local\\Temp\\mmrag_parsed_a4a_k005\\extracted_images\\page_024_image_1.jpeg",
  "image_ext": "jpeg"
}
```

Content:
IMAGE FOUND ON PAGE 24
IMAGE INDEX: 1
IMAGE PATH: C:\Users\prash\AppData\Local\Temp\mmrag_parsed_a4a_k005\extracted_images\page_024_image_1.jpeg

IMAGE OCR TEXT:
[OCR_SKIPPED_OR_FAILED: tesseract is not installed or it's not in your PATH. See README file for more information.]

---
