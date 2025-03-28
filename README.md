# Ebook-MCP

Ebook-MCP is a powerful Model Context Protocol (MCP) server for processing electronic books. Built on the [Model Context Protocol](https://github.com/modelcontextprotocol), it provides a set of standardized APIs for seamless integration between LLM applications and e-book processing capabilities. Currently supports EPUB and PDF formats.

## Features

### EPUB Support
- Extract metadata (title, author, publication date, etc.)
- Extract table of contents
- Extract chapter content (with Markdown output)
- Batch process EPUB files

### PDF Support
- Extract metadata (title, author, creation date, etc.)
- Extract table of contents
- Extract content by page number
- Extract content by chapter title
- Markdown output support
- Batch process PDF files

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ebook-mcp.git
cd ebook-mcp
```

2. Install dependencies using `uv`:
```bash
uv pip install -r requirements.txt
```

## Usage

### Starting the MCP Server

Run the server in development mode:
```bash
uv run mcp dev main.py
```

### EPUB Processing Examples

```python
# Get all EPUB files in a directory
epub_files = get_all_epub_files("/path/to/books")

# Get EPUB metadata
metadata = get_metadata("/path/to/book.epub")

# Get table of contents
toc = get_toc("/path/to/book.epub")

# Get specific chapter content (in Markdown format)
chapter_content = get_chapter_markdown("/path/to/book.epub", "chapter_id")
```

### PDF Processing Examples

```python
# Get all PDF files in a directory
pdf_files = get_all_pdf_files("/path/to/books")

# Get PDF metadata
metadata = get_pdf_metadata("/path/to/book.pdf")

# Get table of contents
toc = get_pdf_toc("/path/to/book.pdf")

# Get specific page content
page_text = get_pdf_page_text("/path/to/book.pdf", 1)
page_markdown = get_pdf_page_markdown("/path/to/book.pdf", 1)

# Get specific chapter content
chapter_content, page_numbers = get_pdf_chapter_content("/path/to/book.pdf", "Chapter 1")
```

## API Reference

### EPUB APIs

#### `get_all_epub_files(path: str) -> List[str]`
Get all EPUB files in the specified directory.

#### `get_metadata(epub_path: str) -> Dict[str, Union[str, List[str]]]`
Get metadata from an EPUB file.

#### `get_toc(epub_path: str) -> List[Tuple[str, str]]`
Get table of contents from an EPUB file.

#### `get_chapter_markdown(epub_path: str, chapter_id: str) -> str`
Get chapter content in Markdown format.

### PDF APIs

#### `get_all_pdf_files(path: str) -> List[str]`
Get all PDF files in the specified directory.

#### `get_pdf_metadata(pdf_path: str) -> Dict[str, Union[str, List[str]]]`
Get metadata from a PDF file.

#### `get_pdf_toc(pdf_path: str) -> List[Tuple[str, int]]`
Get table of contents from a PDF file.

#### `get_pdf_page_text(pdf_path: str, page_number: int) -> str`
Get plain text content from a specific page.

#### `get_pdf_page_markdown(pdf_path: str, page_number: int) -> str`
Get Markdown formatted content from a specific page.

#### `get_pdf_chapter_content(pdf_path: str, chapter_title: str) -> Tuple[str, List[int]]`
Get chapter content and corresponding page numbers by chapter title.

## Dependencies

Key dependencies include:
- ebooklib: EPUB file processing
- PyPDF2: Basic PDF processing
- PyMuPDF: Advanced PDF processing
- beautifulsoup4: HTML parsing
- html2text: HTML to Markdown conversion
- pydantic: Data validation
- fastmcp: MCP server framework

## Important Notes

1. PDF processing relies on the document's table of contents. Some features may not work if TOC is not available.
2. For large PDF files, it's recommended to process by page ranges to avoid loading the entire file at once.
3. EPUB chapter IDs must be obtained from the table of contents structure.

## Architecture

```
           ┌────────────────────────────┐
           │         Agent Layer        │
           │  - Translation Strategy    │
           │  - Style Consistency Check │
           │  - LLM Call & Interaction │
           └────────────▲─────────────┘
                        │ Tool Calls
           ┌────────────┴─────────────┐
           │        MCP Tool Layer     │
           │  - extract_chapter        │
           │  - write_translated_chapter│
           │  - generate_epub          │
           └────────────▲─────────────┘
                        │ System/IO Calls
           ┌────────────┴─────────────┐
           │     System Base Layer     │
           │  - File Reading          │
           │  - ebooklib Parsing      │
           │  - File Path Storage/Check│
           └────────────────────────────┘
```

## License

[MIT License](LICENSE)

## Contributing

We welcome Issues and Pull Requests!

## Author

[Your Name]

## Changelog

### v1.0.0
- Initial release
- EPUB and PDF format support
- Basic file processing APIs
```
           ┌────────────────────────────┐
           │         Agent Layer        │
           │  - Translation Strategy    │
           │  - Style Consistency Check │
           │  - LLM Call & Interaction │
           └────────────▲─────────────┘
                        │ Tool Calls
           ┌────────────┴─────────────┐
           │        MCP Tool Layer     │
           │  - extract_chapter        │
           │  - write_translated_chapter│
           │  - generate_epub          │
           └────────────▲─────────────┘
                        │ System/IO Calls
           ┌────────────┴─────────────┐
           │     System Base Layer     │
           │  - File Reading          │
           │  - ebooklib Parsing      │
           │  - File Path Storage/Check│
           └────────────────────────────┘
```