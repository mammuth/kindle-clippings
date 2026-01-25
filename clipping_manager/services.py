import logging
import hashlib
from clipping_manager.models import Book, Clipping

logger = logging.getLogger(__name__)

def generate_content_hash(content: str) -> str:
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def import_clippings_for_user(user, clips_data):
    """
    clips_data can be:
    - { 'Book Title': ['Highlight 1', ...], ... } (Kindle format)
    - [ { 'title': '...', 'text': '...', 'authors': '...' }, ... ] (JSON format)
    """
    num_books = 0
    num_clippings = 0
    errors = 0
    
    if isinstance(clips_data, dict):
        # Convert Kindle format to consistent format
        normalized_data = []
        for title, texts in clips_data.items():
            for text in texts:
                normalized_data.append({
                    'title': title,
                    'text': text,
                })
        clips_data = normalized_data

    # Book cache to avoid repeated lookups
    book_cache = {}

    for item in clips_data:
        title = item.get('title')
        text = item.get('text')
        author = item.get('authors') or item.get('author', '')
        
        if not title or not text:
            continue
            
        try:
            if title not in book_cache:
                book, created = Book.objects.get_or_create(
                    user=user,
                    title=title,
                    defaults={'author_name': author}
                )
                if created:
                    num_books += 1
                book_cache[title] = book
            else:
                book = book_cache[title]

            content_hash = generate_content_hash(text)
            # Use get_or_create with content_hash to avoid issues with long text in some DBs
            __, created = Clipping.objects.get_or_create(
                user=user,
                book=book,
                content_hash=content_hash,
                defaults={'content': text}
            )
            if created:
                num_clippings += 1
        except Exception as e:
            errors += 1
            logger.error(f'Error importing a clipping for book {title}.', exc_info=True)
                
    return num_books, num_clippings, errors
