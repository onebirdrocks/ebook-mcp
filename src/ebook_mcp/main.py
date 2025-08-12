import os
from typing import Any,List,Dict,Union,Tuple
from mcp.server.fastmcp import FastMCP
from ebooklib import epub
from pydantic import BaseModel
from bs4 import BeautifulSoup
from ebook_mcp.tools import epub_helper, pdf_helper
import logging
from datetime import datetime
from ebook_mcp.tools.logger_config import setup_logger  # Import logger config


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
def get_all_epub_files(path: str) -> List[str]:
    """Get all epub files in a given path.
    """
    return epub_helper.get_all_epub_files(path)

@mcp.tool()
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
    try:
        return epub_helper.get_meta(epub_path)
    except FileNotFoundError as e:
        raise FileNotFoundError(str(e))
    except Exception as e:
        raise Exception(str(e))


@mcp.tool()
def get_epub_toc(epub_path: str) -> List[Tuple[str, str]]:
    """Get toc of a given ebook.

    Args:
        epub_path: Full path to the ebook file.eg. "/Users/macbook/Downloads/test.epub"
    
    Returns:
        List[Tuple[str, str]]: Return a list，Each element is a Tuple，contain (Chapter tile, chapter link)

    Raises:
        FileNotFoundError: Raises when the epub file not found
        Exception: Raisers when running into parsing error of epub file
    """
    logger.debug(f"calling get_epub_toc: {epub_path}")
    try:
        return epub_helper.get_toc(epub_path)
    except FileNotFoundError as e:
        raise FileNotFoundError(str(e))
    except Exception as e:
        raise Exception(str(e))


@mcp.tool()
def get_epub_chapter_markdown(epub_path:str, chapter_id: str) -> str:
    """⚠️ DEPRECATED: This tool has a known issue when processing EPUB files with subchapters.
    When the TOC contains subchapters, it may prematurely truncate chapter content and only return the chapter title.

    It is recommended to use get_epub_chapter_markdown_fixed for more accurate chapter extraction results.

    Args:
        epub_path: Full path to the ebook file.eg. "/Users/macbook/Downloads/test.epub"
        chapter_id: Chapter id of the chapter to get content
    """
    logger.debug(f"calling get_epub_chapter_markdown: {epub_path}, chapter ID: {chapter_id}")
    try:
        book = epub_helper.read_epub(epub_path)
        return epub_helper.extract_chapter_markdown(book, chapter_id)
    except FileNotFoundError as e:
        raise FileNotFoundError(str(e))
    except Exception as e:
        raise Exception(str(e))

@mcp.tool()
def get_epub_chapter_markdown_fixed(epub_path:str, chapter_id: str) -> str:
    """Get content of a given chapter using the improved extraction method.
    
    ✅ RECOMMENDED: This tool fixes the truncation issue in the original version when processing subchapters.
    It can correctly handle EPUB files with subchapters and provide complete chapter content.
    
    This function uses extract_chapter_html_fixed which properly handles subchapters
    and provides accurate chapter boundaries, fixing the issue where subchapters
    in the TOC cause premature truncation of chapter content.

    Args:
        epub_path: Full path to the ebook file. eg. "/Users/macbook/Downloads/test.epub"
        chapter_id: Chapter id of the chapter to get content (e.g., "chapter1.xhtml#section1_3")
    
    Returns:
        str: Chapter content in markdown format
    """
    logger.debug(f"calling get_epub_chapter_markdown_fixed: {epub_path}, chapter ID: {chapter_id}")
    try:
        book = epub_helper.read_epub(epub_path)
        
        # Use the fixed version instead of the original
        return epub_helper.extract_chapter_markdown_fixed(book, chapter_id)
    except FileNotFoundError as e:
        raise FileNotFoundError(str(e))
    except Exception as e:
        raise Exception(str(e))

# PDF related tools
@mcp.tool()
def get_all_pdf_files(path: str) -> List[str]:
    """Get all PDF files in a given path.
    """
    return pdf_helper.get_all_pdf_files(path)

@mcp.tool()
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
    try:
        return pdf_helper.get_meta(pdf_path)
    except FileNotFoundError as e:
        raise FileNotFoundError(str(e))
    except Exception as e:
        raise Exception(str(e))

@mcp.tool()
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
    try:
        return pdf_helper.get_toc(pdf_path)
    except FileNotFoundError as e:
        raise FileNotFoundError(str(e))
    except Exception as e:
        raise Exception(str(e))

@mcp.tool()
def get_pdf_page_text(pdf_path: str, page_number: int) -> str:
    """Get text content of a specific page in PDF file.

    Args:
        pdf_path: Full path to the PDF file.eg. "/Users/macbook/Downloads/test.pdf"
        page_number: Page number to extract (1-based index)
    
    Returns:
        str: Extracted text content
    """
    logger.debug(f"calling get_pdf_page_text: {pdf_path}, page: {page_number}")
    try:
        return pdf_helper.extract_page_text(pdf_path, page_number)
    except Exception as e:
        raise Exception(str(e))

@mcp.tool()
def get_pdf_page_markdown(pdf_path: str, page_number: int) -> str:
    """Get markdown formatted content of a specific page in PDF file.

    Args:
        pdf_path: Full path to the PDF file.eg. "/Users/macbook/Downloads/test.pdf"
        page_number: Page number to extract (1-based index)
    
    Returns:
        str: Markdown formatted text
    """
    logger.debug(f"calling get_pdf_page_markdown: {pdf_path}, page: {page_number}")
    try:
        return pdf_helper.extract_page_markdown(pdf_path, page_number)
    except Exception as e:
        raise Exception(str(e))

@mcp.tool()
def get_pdf_chapter_content(pdf_path: str, chapter_title: str) -> Tuple[str, List[int]]:
    """Get content of a specific chapter in PDF file by its title.

    Args:
        pdf_path: Full path to the PDF file.eg. "/Users/macbook/Downloads/test.pdf"
        chapter_title: Title of the chapter to extract
    
    Returns:
        Tuple[str, List[int]]: Tuple containing (chapter_content, page_numbers)
    """
    logger.debug(f"calling get_pdf_chapter_content: {pdf_path}, chapter: {chapter_title}")
    try:
        return pdf_helper.extract_chapter_by_title(pdf_path, chapter_title)
    except Exception as e:
        raise Exception(str(e))

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
