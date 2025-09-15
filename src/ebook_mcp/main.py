import os
from typing import Any,List,Dict,Union,Tuple, Callable, TypeVar
from functools import wraps
from mcp.server.fastmcp import FastMCP
from ebooklib import epub
from pydantic import BaseModel
from bs4 import BeautifulSoup
from ebook_mcp.tools import epub_helper, pdf_helper
import logging
from datetime import datetime
from ebook_mcp.tools.logger_config import setup_logger  # Import logger config

# Type variable for generic function return type
T = TypeVar('T')

def handle_mcp_errors(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator to handle common MCP tool errors uniformly.
    
    This decorator catches FileNotFoundError and other exceptions,
    re-raises them with consistent error messages.
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            raise FileNotFoundError(str(e))
        except (epub_helper.EpubProcessingError, pdf_helper.PdfProcessingError) as e:
            # Re-raise custom exceptions as-is to preserve detailed error information
            raise e
        except Exception as e:
            raise Exception(str(e))
    return wrapper

def handle_pdf_errors(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator to handle PDF-specific errors.
    
    Some PDF functions don't need FileNotFoundError handling
    as they handle it internally.
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            raise Exception(str(e))
    return wrapper


log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, f"ebook-mcp_server_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)




# Initialize FastMCP server
mcp = FastMCP("ebook-MCP")

# EPUB related tools
@mcp.tool()
@handle_mcp_errors
def get_all_epub_files(path: str) -> List[str]:
    """Get all epub files in a given path.
    """
    return epub_helper.get_all_epub_files(path)

@mcp.tool()
@handle_mcp_errors
def get_epub_metadata(epub_path:str) -> Dict[str, Union[str, List[str]]]:
    """Get metadata of a given ebook.

    Args:
        epub_path: Full path to the ebook file.eg. "/Users/macbook/Downloads/test.epub"
    
    Returns:
        List[Tuple[str, str]]: Return a list，Each element is a Tuple，contains key and value of metadata

    Raises:
        FileNotFoundError: Raises when the epub file not found
        Exception: Raisers when running into parsing error of epub file
    """
    logger.debug(f"Getting ebook metadata: {epub_path}")
    return epub_helper.get_meta(epub_path)


@mcp.tool()
@handle_mcp_errors
def get_epub_toc(epub_path: str) -> List[Tuple[str, str]]:
    """Get table of contents of a given EPUB file.

    Args:
        epub_path: Full path to the ebook file.eg. "/Users/macbook/Downloads/test.epub"
    
    Returns:
        List[Tuple[str, str]]: List of TOC entries, each entry is a tuple of (title, href)

    Raises:
        FileNotFoundError: Raises when the EPUB file not found
        Exception: Raisers when running into parsing error of EPUB file
    """
    logger.debug(f"calling get_epub_toc: {epub_path}")
    return epub_helper.get_toc(epub_path)

@mcp.tool()
@handle_mcp_errors
def get_epub_chapter_markdown(epub_path:str, chapter_id: str, start_index: int = 0, page_size: int = 50000) -> str:
    """Get content of a given chapter using the improved extraction method.
    
    ✅ RECOMMENDED: This tool fixes the truncation issue in the original version when processing subchapters.
    It can correctly handle EPUB files with subchapters and provide complete chapter content.
    
    This function uses extract_chapter_html which properly handles subchapters
    and provides accurate chapter boundaries, fixing the issue where subchapters
    in the TOC cause premature truncation of chapter content.

    Args:
        epub_path: Full path to the ebook file. eg. "/Users/macbook/Downloads/test.epub"
        chapter_id: Chapter id of the chapter to get content (e.g., "chapter1.xhtml#section1_3")
        start_index: Starting character index for pagination (default: 0)
        page_size: Maximum number of characters to return (default: 50000)
    
    Returns:
        str: Chapter content in markdown format (paginated if needed)
    """
    logger.debug(f"calling get_epub_chapter_markdown: {epub_path}, chapter ID: {chapter_id}, start: {start_index}, size: {page_size}")
    book = epub_helper.read_epub(epub_path)
    
    # Use the improved version to get full content
    full_content = epub_helper.extract_chapter_markdown(book, chapter_id)
    
    # Apply pagination
    end_index = start_index + page_size
    paginated_content = full_content[start_index:end_index]
    
    # Add pagination info if content was truncated
    if end_index < len(full_content):
        paginated_content += f"\n\n[Content truncated. Total length: {len(full_content)} characters. Use start_index={end_index} to continue.]"
    
    return paginated_content

# PDF related tools
@mcp.tool()
@handle_mcp_errors
def get_all_pdf_files(path: str) -> List[str]:
    """Get all PDF files in a given path.
    """
    return pdf_helper.get_all_pdf_files(path)

@mcp.tool()
@handle_mcp_errors
def get_pdf_metadata(pdf_path: str) -> Dict[str, Union[str, List[str]]]:
    """Get metadata of a given PDF file.

    Args:
        pdf_path: Full path to the PDF file.eg. "/Users/macbook/Downloads/test.pdf"
    
    Returns:
        Dict[str, Union[str, List[str]]]: Dictionary containing metadata

    Raises:
        FileNotFoundError: Raises when the PDF file not found
        Exception: Raisers when running into parsing error of PDF file
    """
    logger.debug(f"calling get_pdf_metadata: {pdf_path}")
    return pdf_helper.get_meta(pdf_path)

@mcp.tool()
@handle_mcp_errors
def get_pdf_toc(pdf_path: str) -> List[Tuple[str, int]]:
    """Get table of contents of a given PDF file.

    Args:
        pdf_path: Full path to the PDF file.eg. "/Users/macbook/Downloads/test.pdf"
    
    Returns:
        List[Tuple[str, int]]: List of TOC entries, each entry is a tuple of (title, page_number)

    Raises:
        FileNotFoundError: Raises when the PDF file not found
        Exception: Raisers when running into parsing error of PDF file
    """
    logger.debug(f"calling get_pdf_toc: {pdf_path}")
    return pdf_helper.get_toc(pdf_path)

@mcp.tool()
@handle_pdf_errors
def get_pdf_page_text(pdf_path: str, page_number: int) -> str:
    """Get text content of a specific page in PDF file.

    Args:
        pdf_path: Full path to the PDF file.eg. "/Users/macbook/Downloads/test.pdf"
        page_number: Page number to extract (1-based index)
    
    Returns:
        str: Extracted text content
    """
    logger.debug(f"calling get_pdf_page_text: {pdf_path}, page: {page_number}")
    return pdf_helper.extract_page_text(pdf_path, page_number)

@mcp.tool()
@handle_pdf_errors
def get_pdf_page_markdown(pdf_path: str, page_number: int) -> str:
    """Get markdown formatted content of a specific page in PDF file.

    Args:
        pdf_path: Full path to the PDF file.eg. "/Users/macbook/Downloads/test.pdf"
        page_number: Page number to extract (1-based index)
    
    Returns:
        str: Markdown formatted text
    """
    logger.debug(f"calling get_pdf_page_markdown: {pdf_path}, page: {page_number}")
    return pdf_helper.extract_page_markdown(pdf_path, page_number)

@mcp.tool()
@handle_pdf_errors
def get_pdf_chapter_content(pdf_path: str, chapter_title: str) -> Tuple[str, List[int]]:
    """Get content of a specific chapter in PDF file by its title.

    Args:
        pdf_path: Full path to the PDF file.eg. "/Users/macbook/Downloads/test.pdf"
        chapter_title: Title of the chapter to extract
    
    Returns:
        Tuple[str, List[int]]: Tuple containing (chapter_content, page_numbers)
    """
    logger.debug(f"calling get_pdf_chapter_content: {pdf_path}, chapter: {chapter_title}")
    return pdf_helper.extract_chapter_by_title(pdf_path, chapter_title)

if __name__ == "__main__":
    # Initialize and run the server
    logger.info("Server is starting.....")
    mcp.run(transport='stdio')

# as the cli entry after the "pip install ebook-mcp"
def cli_entry():
    import logging
    logging.info("Starting ebook-mcp server")
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP("ebook-mcp")
    mcp.run(transport='stdio')
