import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def word_count(text):
    """ Подсчет количества слов в тексте """
    return len(text.split())

def clean_text(html):
    """ Очистка HTML-кода и извлечение текста """
    soup = BeautifulSoup(html, 'html.parser')
    for script_or_style in soup(['script', 'style']):
        script_or_style.decompose()
    
    text = soup.get_text(separator='\n')
    text = re.sub(r'[^а-яёА-ЯЁ\s]', '', text)
    text = re.sub(r'\n+', '\n', text).strip()
    return text

def get_links(html, base_url):
    """ Извлечение всех корректных ссылок со страницы """
    soup = BeautifulSoup(html, 'html.parser')
    links = set()
    for link in soup.find_all('a', href=True):
        href = link.get('href')
        full_url = urljoin(base_url, href)
        if urlparse(full_url).netloc == urlparse(base_url).netloc:
            links.add(full_url)
    return links

def download_pages(start_urls, max_pages=100, min_words=1000, save_dir='pages'):
    """ Основная функция краулера """
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
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            text = clean_text(response.text)
            
            if word_count(text) >= min_words:
                page_count += 1
                file_name = f'doc_{page_count}.txt'
                file_path = os.path.join(save_dir, file_name)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                
                index.append(f'{page_count}: {url}')
                crawled_urls.add(url)
                to_crawl.update(get_links(response.text, url))
        
        except requests.RequestException:
            continue
    
    with open('index.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(index))

if __name__ == "__main__":
    start_urls = ['https://ru.wikipedia.org/wiki/TCP']
    download_pages(start_urls)
