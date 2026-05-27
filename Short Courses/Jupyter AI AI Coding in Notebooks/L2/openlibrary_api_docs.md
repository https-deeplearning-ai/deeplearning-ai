# Open Library API Documentation

## Overview

Open Library provides a comprehensive set of APIs for accessing book data, author information, and bibliographic records. This document covers the main endpoints you'll use in this lesson.

## Base URLs

- **Search API:** `https://openlibrary.org/search.json`
- **Books API:** `https://openlibrary.org/books/{identifier}.json`
- **Authors API:** `https://openlibrary.org/authors/{author_id}.json`
- **Works API:** `https://openlibrary.org/works/{work_id}.json`
- **Covers API:** `https://covers.openlibrary.org/b/{size}/{value}-{size}.jpg`

---

## Search API

**Endpoint:** `GET https://openlibrary.org/search.json`

The Search API is the most convenient way to search for books, returning both work-level and edition-level information.

### Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `q` | string | General search query | `q=lord+of+the+rings` |
| `title` | string | Search by title | `title=pride+and+prejudice` |
| `author` | string | Search by author name | `author=tolkien` |
| `subject` | string | Search by subject | `subject=fantasy` |
| `isbn` | string | Search by ISBN | `isbn=9780140328721` |
| `fields` | string | Comma-separated fields to return | `fields=key,title,author_name,first_publish_year` |
| `limit` | integer | Number of results (default: 100, max: 100) | `limit=10` |
| `offset` | integer | Pagination offset | `offset=0` |
| `sort` | string | Sort order (new, old, random, etc.) | `sort=new` |
| `lang` | string | Filter by language code | `lang=eng` |

### Response Format

```json
{
  "start": 0,
  "num_found": 629,
  "numFound": 629,
  "docs": [
    {
      "key": "/works/OL27448W",
      "title": "The Lord of the Rings",
      "author_name": ["J. R. R. Tolkien"],
      "author_key": ["OL26320A"],
      "first_publish_year": 1954,
      "isbn": ["0618346252", "0618346260"],
      "cover_i": 8739161,
      "edition_count": 150,
      "language": ["eng"],
      "publisher": ["HarperCollins"],
      "publish_year": [1954, 1965, 1974]
    }
  ]
}
```

### Common Response Fields

- `key`: Work identifier (e.g., `/works/OL27448W`)
- `title`: Book title
- `author_name`: Array of author names
- `author_key`: Array of author identifiers
- `first_publish_year`: Year of first publication
- `isbn`: Array of ISBNs
- `cover_i`: Cover image ID
- `edition_count`: Number of editions
- `language`: Array of language codes
- `publisher`: Array of publishers
- `publish_year`: Array of publication years
- `number_of_pages_median`: Median page count
- `subject`: Array of subjects

### Example Queries

**Search by title:**
```
https://openlibrary.org/search.json?title=moby+dick
```

**Search by author:**
```
https://openlibrary.org/search.json?author=hemingway&sort=new
```

**Search with specific fields:**
```
https://openlibrary.org/search.json?q=python+programming&fields=key,title,author_name,first_publish_year,edition_count&limit=5
```

**Search by subject:**
```
https://openlibrary.org/search.json?subject=science+fiction&limit=20
```

---

## Books API

**Endpoint:** `GET https://openlibrary.org/books/{identifier}.json`

Retrieve detailed information about a specific book edition.

### Identifiers

You can use various identifiers:
- Open Library ID: `OL7353617M`
- ISBN-10: `ISBN:0451526538`
- ISBN-13: `ISBN:9780451526533`
- LCCN: `LCCN:93005405`
- OCLC: `OCLC:28457662`

### Example Request

```
https://openlibrary.org/books/OL7353617M.json
```

### Response Format

```json
{
  "publishers": ["Signet Classic"],
  "number_of_pages": 328,
  "isbn_10": ["0451526538"],
  "isbn_13": ["9780451526533"],
  "covers": [295577],
  "key": "/books/OL7353617M",
  "authors": [{"key": "/authors/OL28127A"}],
  "title": "1984",
  "publish_date": "1961",
  "works": [{"key": "/works/OL14933374W"}]
}
```

---

## Works API

**Endpoint:** `GET https://openlibrary.org/works/{work_id}.json`

Retrieve information about a work (which can have multiple editions).

### Example Request

```
https://openlibrary.org/works/OL14933374W.json
```

### Response Format

```json
{
  "title": "Nineteen Eighty-Four",
  "key": "/works/OL14933374W",
  "authors": [
    {
      "author": {"key": "/authors/OL28127A"},
      "type": {"key": "/type/author_role"}
    }
  ],
  "description": "A dystopian novel...",
  "subjects": ["Fiction", "Dystopian fiction", "Political fiction"],
  "covers": [295577, 295578]
}
```

---

## Authors API

**Endpoint:** `GET https://openlibrary.org/authors/{author_id}.json`

Retrieve information about an author.

### Example Request

```
https://openlibrary.org/authors/OL28127A.json
```

### Response Format

```json
{
  "key": "/authors/OL28127A",
  "name": "George Orwell",
  "birth_date": "25 June 1903",
  "death_date": "21 January 1950",
  "bio": "Eric Arthur Blair, better known by his pen name George Orwell...",
  "photos": [6253743, 6253744]
}
```

### Author's Works

**Endpoint:** `GET https://openlibrary.org/authors/{author_id}/works.json`

```
https://openlibrary.org/authors/OL28127A/works.json?limit=10
```

---

## Covers API

**Endpoint:** `GET https://covers.openlibrary.org/b/{type}/{value}-{size}.jpg`

Retrieve book cover images.

### Parameters

- **type**: `id`, `isbn`, `oclc`, `lccn`, `olid`
- **value**: The identifier value
- **size**: `S` (small), `M` (medium), `L` (large)

### Examples

**By Cover ID:**
```
https://covers.openlibrary.org/b/id/295577-L.jpg
```

**By ISBN:**
```
https://covers.openlibrary.org/b/isbn/9780451526533-M.jpg
```

**By OLID:**
```
https://covers.openlibrary.org/b/olid/OL7353617M-S.jpg
```

---

## Pagination

For Search API results with many items:

```python
# First page (0-10)
https://openlibrary.org/search.json?q=python&limit=10&offset=0

# Second page (10-20)
https://openlibrary.org/search.json?q=python&limit=10&offset=10

# Third page (20-30)
https://openlibrary.org/search.json?q=python&limit=10&offset=20
```

---

## Rate Limiting

- No API key required
- Be respectful with request rates
- Consider caching responses for repeated queries
- Recommended: Add delays between bulk requests

---

## Error Handling

**404 Not Found:**
- Book/Author/Work doesn't exist
- Check identifier format

**Empty Results:**
```json
{
  "start": 0,
  "num_found": 0,
  "docs": []
}
```

---

## Best Practices

1. **Use specific fields** to reduce response size:
   ```
   fields=key,title,author_name,first_publish_year
   ```

2. **Limit results** appropriately:
   ```
   limit=20
   ```

3. **Handle missing data** gracefully:
   ```python
   title = book.get('title', 'Unknown Title')
   authors = book.get('author_name', ['Unknown Author'])
   ```

4. **Cache cover images** rather than fetching repeatedly

5. **Use pagination** for large result sets

---

## Common Use Cases

### Search for books by author and get recent publications

```python
import requests

response = requests.get(
    'https://openlibrary.org/search.json',
    params={
        'author': 'Margaret Atwood',
        'sort': 'new',
        'limit': 10,
        'fields': 'key,title,first_publish_year,author_name'
    }
)
data = response.json()
```

### Get book details and cover image

```python
# Get book data
book_response = requests.get('https://openlibrary.org/books/OL7353617M.json')
book_data = book_response.json()

# Get cover image
cover_id = book_data['covers'][0]
cover_url = f'https://covers.openlibrary.org/b/id/{cover_id}-L.jpg'
```

### Search by subject and analyze publication trends

```python
response = requests.get(
    'https://openlibrary.org/search.json',
    params={
        'subject': 'artificial intelligence',
        'limit': 100,
        'fields': 'title,first_publish_year,author_name'
    }
)
```

---

## Additional Resources

- **Main API Documentation:** https://openlibrary.org/developers/api
- **Search API Details:** https://openlibrary.org/dev/docs/api/search
- **Books API Details:** https://openlibrary.org/dev/docs/api/books
- **Covers API Details:** https://openlibrary.org/dev/docs/api/covers
