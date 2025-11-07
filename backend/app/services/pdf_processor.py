"""
PDF text extraction and chunking service.
"""
import PyPDF2
import tiktoken
from typing import List, Dict


def extract_text_from_pdf(file_path: str) -> List[Dict[str, any]]:
    """
    Extract text from PDF with page numbers.

    Args:
        file_path: Path to the PDF file

    Returns:
        List of dictionaries with page number and text
    """
    pages = []

    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)

            for page_num, page in enumerate(pdf_reader.pages, start=1):
                text = page.extract_text()
                if text.strip():  # Only include pages with text
                    pages.append({
                        'page': page_num,
                        'text': text
                    })
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        raise

    return pages


def chunk_text(text: str, page: int, max_tokens: int = 700) -> List[Dict[str, any]]:
    """
    Chunk text into segments of approximately max_tokens size.

    Args:
        text: Text to chunk
        page: Page number
        max_tokens: Maximum tokens per chunk

    Returns:
        List of text chunks with metadata
    """
    # Use tiktoken to count tokens (cl100k_base is used by many models)
    encoding = tiktoken.get_encoding("cl100k_base")

    # Split by sentences (simple approach)
    sentences = text.replace('\n', ' ').split('. ')

    chunks = []
    current_chunk = []
    current_tokens = 0

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        sentence_tokens = len(encoding.encode(sentence))

        if current_tokens + sentence_tokens > max_tokens and current_chunk:
            # Save current chunk
            chunks.append({
                'text': '. '.join(current_chunk) + '.',
                'page': page,
                'token_count': current_tokens
            })
            current_chunk = [sentence]
            current_tokens = sentence_tokens
        else:
            current_chunk.append(sentence)
            current_tokens += sentence_tokens

    # Add remaining chunk
    if current_chunk:
        chunks.append({
            'text': '. '.join(current_chunk) + '.',
            'page': page,
            'token_count': current_tokens
        })

    return chunks


def process_pdf(file_path: str, course_id: str, material_id: str, filename: str) -> List[Dict[str, any]]:
    """
    Process a PDF file into chunks with metadata.

    Args:
        file_path: Path to the PDF file
        course_id: Course ID
        material_id: Material ID
        filename: Original filename

    Returns:
        List of chunks with metadata
    """
    # Extract text from PDF
    pages = extract_text_from_pdf(file_path)

    # Chunk each page
    all_chunks = []
    chunk_index = 0

    for page_data in pages:
        page_chunks = chunk_text(page_data['text'], page_data['page'])

        for chunk in page_chunks:
            all_chunks.append({
                'text': chunk['text'],
                'metadata': {
                    'course_id': course_id,
                    'material_id': material_id,
                    'filename': filename,
                    'page': chunk['page'],
                    'chunk_index': chunk_index
                }
            })
            chunk_index += 1

    return all_chunks
