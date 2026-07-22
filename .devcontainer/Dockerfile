# Pinned Python. Matches requirements.txt / pyproject.toml.
FROM python:3.11-slim

# System libs matplotlib needs for headless (Agg) rendering + a font.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libfreetype6 \
        libpng16-16 \
        fonts-dejavu-core \
        git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Install dependencies first (better layer caching), then the package itself.
# The devcontainer installs the project's declared deps from pyproject.toml.
COPY pyproject.toml requirements.txt README.md ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source and install the package in editable mode so `import digraph_enum`
# and `digraph-enum` both work from anywhere in the container.
COPY . .
RUN pip install --no-cache-dir -e .
