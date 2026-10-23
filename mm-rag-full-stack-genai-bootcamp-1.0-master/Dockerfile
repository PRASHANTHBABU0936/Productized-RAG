# Single image shared by the api / worker / ui services.
#
# Ollama and Qdrant stay outside Docker (Ollama on the Windows host,
# Qdrant Cloud), so nothing GPU- or vendor-specific is baked in here.
#
# Deliberately NOT used: a `python:3.11` image in which `python` resolves to
# something other than the pinned interpreter. The whole point of this image
# is that there is exactly ONE Python and ONE torch/VCRUNTIME stack.
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# System libraries the Python wheels need at runtime:
#   tesseract-ocr + tesseract-ocr-eng -> pytesseract OCR of scanned PDFs
#   libglib2.0-0                      -> OpenCV (via EasyOCR)
#   libgomp1                          -> OpenMP runtime used by PyTorch
#   curl                              -> container healthchecks
#   poppler-utils                     -> pdf2image / pdfplumber fallbacks
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        tesseract-ocr \
        tesseract-ocr-eng \
        libglib2.0-0 \
        libgomp1 \
        poppler-utils \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install PyTorch from the CPU-only index *first*. The extra index is what
# makes pip prefer the `+cpu` wheel over the multi-GB CUDA wheel that the
# default PyPI index serves. If the CPU index is unreachable the build still
# succeeds, it just falls back to the larger wheel.
COPY requirements.txt ./
RUN pip install --upgrade pip \
    && pip install \
        --extra-index-url https://download.pytorch.org/whl/cpu \
        "torch==2.14.1" \
        "torchvision==0.29.1" \
    && pip install -r requirements.txt

COPY . .

EXPOSE 8000 8502

# Default command is the API; compose overrides it for worker/ui.
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
