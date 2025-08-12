from typing import List, Tuple, Dict, Union
import os
import logging

# Try to import optional dependencies
try:
    from ebooklib import epub
    EBOOKLIB_AVAILABLE = True
except ImportError:
    epub = None
    EBOOKLIB_AVAILABLE = False

try:
    from bs4 import BeautifulSoup, Comment
    BEAUTIFULSOUP_AVAILABLE = True
except ImportError:
    BeautifulSoup = None
    Comment = None
    BEAUTIFULSOUP_AVAILABLE = False

try:
    import html2text
    HTML2TEXT_AVAILABLE = True
except ImportError:
    html2text = None
    HTML2TEXT_AVAILABLE = False

# Initialize logger
logger = logging.getLogger(__name__)


def get_all_epub_files(path: str) -> List[str]:
    """
    Get all EPUB files in the specified path
    """
    return [f for f in os.listdir(path) if f.endswith('.epub')]

def get_toc(epub_path: str) -> List[Tuple[str, str]]:
    """
    Get the Table of Contents (TOC) from an EPUB file
    
    Args:
        epub_path (str): Absolute path to the EPUB file
        
    Returns:
        List[Tuple[str, str]]: List of TOC entries, each entry is a tuple of (title, link)
        
    Raises:
        FileNotFoundError: If the file does not exist
        Exception: If the file is not a valid EPUB or parsing fails
    """
    try:
        if not os.path.exists(epub_path):
            logger.error(f"File not found: {epub_path}")
            raise FileNotFoundError(f"EPUB file not found: {epub_path}")
            
        # Read EPUB file
        logger.debug(f"Starting to read EPUB file: {epub_path}")
        book = epub.read_epub(epub_path)
        toc = []
        
        # Iterate through TOC items
        for item in book.toc:
            # Handle nested TOC structure
            if isinstance(item, tuple):
                # item format: (chapter element, list of subchapters)
                chapter = item[0]
                toc.append((chapter.title, chapter.href))
                # Add subchapters
                for sub_item in item[1]:
                    if isinstance(sub_item, tuple):
                        toc.append((sub_item[0].title, sub_item[0].href))
                    else:
                        toc.append((sub_item.title, sub_item.href))
            else:
                # Single level TOC item
                toc.append((item.title, item.href))
        
        logger.debug(f"Successfully retrieved TOC with {len(toc)} entries")
        return toc
    except FileNotFoundError:
        raise FileNotFoundError(f"EPUB file not found: {epub_path}")
    except Exception as e:
        logger.error(f"Failed to parse EPUB file: {str(e)}")
        raise Exception("Failed to parse EPUB file")

def get_meta(epub_path: str) -> Dict[str, Union[str, List[str]]]:
    """
    Get metadata from an EPUB file
    
    Args:
        epub_path (str): Absolute path to the EPUB file
        
    Returns:
        Dict[str, Union[str, List[str]]]: Dictionary containing metadata
            
    Raises:
        FileNotFoundError: If the file does not exist
        Exception: If the file is not a valid EPUB or parsing fails
    """
    try:
        if not os.path.exists(epub_path):
            logger.error(f"File not found: {epub_path}")
            raise FileNotFoundError(f"EPUB file not found: {epub_path}")
            
        # Read EPUB file
        logger.debug(f"Starting to read EPUB file: {epub_path}")
        book = epub.read_epub(epub_path)
        meta = {}

        # Standard metadata fields
        standard_fields = {
            'title': 'title',
            'language': 'language',
            'identifier': 'identifier',
            'date': 'date',
            'publisher': 'publisher',
            'description': 'description'
        }

        # Fields that may have multiple values
        multi_fields = ['creator', 'contributor', 'subject']

        # Extract standard fields
        for field, dc_field in standard_fields.items():
            items = book.get_metadata('DC', dc_field)
            if items and len(items) > 0 and len(items[0]) > 0:
                meta[field] = items[0][0]

        # Handle multi-value fields
        for field in multi_fields:
            items = book.get_metadata('DC', field)
            if items:
                meta[field] = [item[0] for item in items]

        logger.debug(f"Successfully retrieved metadata with fields: {list(meta.keys())}")
        return meta

    except FileNotFoundError:
        raise FileNotFoundError(f"EPUB file not found: {epub_path}")
    except Exception as e:
        logger.error(f"Failed to parse EPUB file: {str(e)}")
        raise Exception("Failed to parse EPUB file")
    


def extract_chapter_from_epub(epub_path, anchor_href):
    """
    Extract complete HTML content of a chapter starting from the specified anchor point until the next TOC entry.
    
    Args:
        epub_path: Complete path to the EPUB file
        anchor_href: Chapter location information like 'xhtml/ch01.xhtml#ch01'
    
    Returns:
        HTML string (complete chapter content starting from the anchor point)
    """
    logger.debug(f"Extracting chapter from EPUB: path= {epub_path} anchor_href= {anchor_href}")
    # Read EPUB file
    book = epub.read_epub(epub_path)
    # Parse input href and anchor id
    if '#' in anchor_href:
        href, anchor_id = anchor_href.split('#')
    else:
        href, anchor_id = anchor_href, None
    
    if anchor_id:
        logger.debug(f"Anchor: {anchor_id}")

    # Get current chapter XHTML content
    item = book.get_item_with_href(href)
    if item is None:
        raise ValueError(f"File not found: {href}")
    
    soup = BeautifulSoup(item.get_content().decode('utf-8'), 'html.parser')

    # If no anchor, return entire page
    if not anchor_id:
        return str(soup)

    # Find anchor starting position
    anchor_elem = soup.find(id=anchor_id)
    if not anchor_elem:
        raise ValueError(f"Anchor #{anchor_id} not found in file {href}")

    # Extract all content after this anchor (including itself)
    extracted = [str(anchor_elem)]
    for elem in anchor_elem.find_all_next():
        extracted.append(str(elem))

    return '\n'.join(extracted)


def read_epub(epub_path):
    return epub.read_epub(epub_path)

def flatten_toc(book):
    toc_list = []
    def _flatten(toc):
        for item in toc:
            if isinstance(item, tuple):
                link, children = item
                toc_list.append(link.href)
                if children:
                    _flatten(children)
            else:
                # Handle single Link object
                toc_list.append(item.href)
    _flatten(book.toc)
    return toc_list

def extract_chapter_html(book, anchor_href):
    toc = flatten_toc(book)
    if anchor_href not in toc:
        raise ValueError(f"{anchor_href} not found in TOC.")

    idx = toc.index(anchor_href)
    href, anchor = anchor_href.split('#') if '#' in anchor_href else (anchor_href, None)
    next_href = toc[idx + 1] if idx + 1 < len(toc) else None

    item = book.get_item_with_href(href)
    soup = BeautifulSoup(item.get_content().decode('utf-8'), 'html.parser')

    if anchor:
        start_elem = soup.find(id=anchor)
        if not start_elem:
            raise ValueError(f"Anchor {anchor} not found in {href}")
        elems = [str(start_elem)] + [str(e) for e in start_elem.find_all_next()]
    else:
        elems = [str(soup)]

    # If next anchor is in current file, truncate
    if next_href and next_href.startswith(href) and '#' in next_href:
        next_anchor = next_href.split('#')[1]
        stop_elem = soup.find(id=next_anchor)
        if stop_elem:
            stop_html = str(stop_elem)
            full_html = '\n'.join(elems)
            return full_html.split(stop_html)[0]  # Truncate the front part
    html = '\n'.join(elems)
    return clean_html(html)  # Clean the HTML before returning

def extract_chapter_plain_text(book, anchor_href):
    html = extract_chapter_html(book, anchor_href)
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text()


def extract_multiple_chapters(book, anchor_list, output='html'):
    results = []
    for href in anchor_list:
        if output == 'html':
            content = extract_chapter_html(book, href)
        elif output == 'text':
            content = extract_chapter_plain_text(book, href)
        elif output == 'markdown':
            content = convert_html_to_markdown(extract_chapter_html(book, href))
        else:
            raise ValueError("Invalid output format.")
        results.append((href, content))
    return results

def convert_html_to_markdown(html_str):
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = False
    return h.handle(html_str)

def clean_html(html_str):
    """
    Clean HTML content:
    - Remove unnecessary tags like <img>, <script>, <style>, <svg>, <video>, <iframe>, <nav>
    - Remove comments
    - Remove empty tags (like empty <p>)
    
    Returns:
    - Cleaned HTML string
    """
    soup = BeautifulSoup(html_str, 'html.parser')

    # Remove unnecessary tags
    for tag in soup(['script', 'style', 'img', 'svg', 'iframe', 'video', 'nav']):
        tag.decompose()

    # Remove HTML comments
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    # Remove empty tags (no text and no useful attributes)
    for tag in soup.find_all():
        if not tag.get_text(strip=True) and not tag.find('img') and not tag.name == 'br':
            tag.decompose()

    return str(soup)



def extract_chapter_html_fixed(book, anchor_href):
    """
    Extract chapter HTML content with improved logic to handle subchapters correctly.
    This function fixes the issue where subchapters in the TOC cause premature truncation
    of chapter content by properly understanding the chapter hierarchy.
    Args:
        book: EPUB book object
        anchor_href: Chapter location information like 'chapter1.xhtml#section1_3'
    Returns:
        HTML string (complete chapter content with proper boundaries)
    """
    logger.debug(f"Extracting chapter with fixed logic: {anchor_href}")
    href, anchor = anchor_href.split('#') if '#' in anchor_href else (anchor_href, None)
    toc_entries = []
    for item in book.toc:
        if isinstance(item, tuple):
            chapter = item[0]
            toc_entries.append((chapter.title, chapter.href, 1))
            for sub_item in item[1]:
                if isinstance(sub_item, tuple):
                    toc_entries.append((sub_item[0].title, sub_item[0].href, 2))
                else:
                    toc_entries.append((sub_item.title, sub_item.href, 2))
        else:
            toc_entries.append((item.title, item.href, 1))
    current_idx = None
    current_level = None
    for i, (title, toc_href, level) in enumerate(toc_entries):
        if toc_href == anchor_href or (anchor_href in toc_href and '#' in anchor_href):
            current_idx = i
            current_level = level
            break
    if current_idx is None:
        raise ValueError(f"{anchor_href} not found in TOC.")
    next_chapter_href = None
    for i in range(current_idx + 1, len(toc_entries)):
        title, toc_href, level = toc_entries[i]
        if level <= current_level:
            next_chapter_href = toc_href
            break
    item = book.get_item_with_href(href)
    if item is None:
        raise ValueError(f"File not found: {href}")
    soup = BeautifulSoup(item.get_content().decode('utf-8'), 'html.parser')
    elems = []
    def heading_level(tag_name):
        if tag_name and tag_name.startswith('h') and tag_name[1:].isdigit():
            return int(tag_name[1:])
        return 7  # treat as lowest priority
    if anchor:
        start_elem = soup.find(id=anchor)
        if not start_elem:
            raise ValueError(f"Anchor {anchor} not found in {href}")
        start_level = heading_level(start_elem.name)
        for elem in start_elem.next_elements:
            if elem is start_elem:
                elems.append(str(elem))
                continue
            if hasattr(elem, 'name') and elem.name and elem.name.startswith('h') and elem.name[1:].isdigit():
                if heading_level(elem.name) <= start_level:
                    break
            elems.append(str(elem))
    else:
        chapter_elem = soup.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        if chapter_elem:
            start_level = heading_level(chapter_elem.name)
            for elem in chapter_elem.next_elements:
                if elem is chapter_elem:
                    elems.append(str(elem))
                    continue
                if hasattr(elem, 'name') and elem.name and elem.name.startswith('h') and elem.name[1:].isdigit():
                    if heading_level(elem.name) <= start_level:
                        break
                elems.append(str(elem))
        else:
            body_elem = soup.find('body')
            elems = [str(body_elem)] if body_elem else [str(soup)]
    html = '\n'.join(elems)
    return clean_html(html)


def extract_chapter_plain_text_fixed(book, anchor_href):
    """Fixed version of extract_chapter_plain_text using extract_chapter_html_fixed"""
    html = extract_chapter_html_fixed(book, anchor_href)
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text()


def extract_chapter_markdown(book, anchor_href):
    """Fixed version of extract_chapter_markdown using extract_chapter_html_fixed"""
    html = extract_chapter_html_fixed(book, anchor_href)
    return convert_html_to_markdown(html)


def extract_multiple_chapters_fixed(book, anchor_list, output='html'):
    """Fixed version of extract_multiple_chapters using extract_chapter_html_fixed"""
    results = []
    for href in anchor_list:
        if output == 'html':
            content = extract_chapter_html_fixed(book, href)
        elif output == 'text':
            content = extract_chapter_plain_text_fixed(book, href)
        elif output == 'markdown':
            content = extract_chapter_markdown_fixed(book, href)
        else:
            raise ValueError("Invalid output format.")
        results.append((href, content))
    return results


if __name__ == "__main__":
    # Test the functionality
    book = read_epub('/path/to/book.epub')
    # Single chapter to Markdown
    md = convert_html_to_markdown(extract_chapter_html(book, 'xhtml/ch02.xhtml#ch02'))
    # Multiple chapters to plain text
    chapters = ['xhtml/ch01.xhtml#ch01', 'xhtml/ch02.xhtml#ch02', 'xhtml/ch03.xhtml#ch03']
    results = extract_multiple_chapters(book, chapters, output='text')
    # Save results
    for href, content in results:
        fname = href.replace('/', '_').replace('#', '_') + '.txt'
        with open(fname, 'w', encoding='utf-8') as f:
            f.write(content)
