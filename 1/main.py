import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, unquote

START_URLS = [
    'https://ru.wikipedia.org/wiki/TCP'
]
MAX_PAGES = 100
MIN_WORDS = 1000
SAVE_DIR = 'pages'

def word_count(text):
    return len(text.split())

def clean_text(html):
    """Очистка HTML-кода и извлечение только кириллического текста"""
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup(['script', 'style']):
        tag.decompose()
    text = soup.get_text(separator='\n')
    text = re.sub(r'[^а-яёА-ЯЁ\s]', '', text)
    text = re.sub(r'\n+', '\n', text).strip()
    return text

def is_valid_link(href, base_domain):
    if not href:
        return False
    href = href.strip()

    if href.startswith(('mailto:', 'tel:', 'javascript:', '#')):
        return False

    if re.search(r'\.(jpg|jpeg|png|gif|svg|pdf|zip|rar|exe|mp3|mp4|avi|docx?)$', href, re.IGNORECASE):
        return False

    parsed = urlparse(href)
    if parsed.netloc and parsed.netloc != base_domain:
        return False

    if parsed.query:
        if any(k in parsed.query for k in ['action=', 'veaction=', 'section=', 'diff=', 'oldid=']):
            return False

    return True


def get_links(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    base_domain = urlparse(base_url).netloc
    links = set()

    for tag in soup.find_all('a', href=True):
        href = tag.get('href').split('#')[0]
        full_url = urljoin(base_url, href)
        if is_valid_link(full_url, base_domain):
            links.add(full_url)

    return links

def download_pages(start_urls, max_pages, min_words, save_dir):
    os.makedirs(save_dir, exist_ok=True)
    crawled_urls = set()
    to_crawl = set(start_urls)
    index = []
    page_count = 0

    while to_crawl and page_count < max_pages:
        url = to_crawl.pop()
        if url in crawled_urls:
            continue

        try:
            response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()

            if 'text/html' not in response.headers.get('Content-Type', ''):
                continue

            text = clean_text(response.text)

            if word_count(text) >= min_words:
                page_count += 1
                file_name = f'doc_{page_count}.txt'
                file_path = os.path.join(save_dir, file_name)

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text)

                decoded_url = unquote(url)
                index.append(f'{page_count}: {decoded_url}')
                print(f"✓ Загружено ({page_count}): {decoded_url}")

                crawled_urls.add(url)
                new_links = get_links(response.text, url)
                to_crawl.update(new_links - crawled_urls)

        except requests.RequestException as e:
            print(f"✗ Не удалось загрузить {url}: {e}")
            continue

    with open('index.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(index))


if __name__ == "__main__":
    download_pages(
        start_urls=START_URLS,
        max_pages=MAX_PAGES,
        min_words=MIN_WORDS,
        save_dir=SAVE_DIR
    )
