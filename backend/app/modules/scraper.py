import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import re
from typing import List, Dict, Optional
from loguru import logger
import asyncio
from dataclasses import dataclass

@dataclass
class ChapterData:
    title: str
    content: str
    chapter_number: int
    url: str
    word_count: int

@dataclass
class NovelData:
    title: str
    author: str
    description: str
    chapters: List[ChapterData]
    total_chapters: int
    url: str

class NovelHiScraper:
    """Scraper for novelhi.com website"""
    
    def __init__(self, use_selenium: bool = False):
        self.base_url = "https://novelhi.com"
        self.session = requests.Session()
        self.use_selenium = use_selenium
        self.driver = None
        
        # Set up headers to mimic a real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
    
    def _setup_selenium_driver(self) -> webdriver.Chrome:
        """Setup Selenium WebDriver with appropriate options"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in background
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            return driver
        except Exception as e:
            logger.error(f"Failed to setup Selenium driver: {e}")
            raise
    
    async def search_novel(self, novel_name: str) -> List[Dict]:
        """Search for novels by name on novelhi.com"""
        try:
            search_url = f"{self.base_url}/search"
            params = {'q': novel_name}
            
            response = self.session.get(search_url, params=params)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract search results (this would need to be adjusted based on actual HTML structure)
            novels = []
            search_results = soup.find_all('div', class_='search-result-item')  # Placeholder class
            
            for result in search_results:
                title_elem = result.find('h3') or result.find('a')
                url_elem = result.find('a')
                desc_elem = result.find('p', class_='description')
                
                if title_elem and url_elem:
                    novels.append({
                        'title': title_elem.get_text(strip=True),
                        'url': self._normalize_url(url_elem.get('href')),
                        'description': desc_elem.get_text(strip=True) if desc_elem else ""
                    })
            
            logger.info(f"Found {len(novels)} novels matching '{novel_name}'")
            return novels
            
        except Exception as e:
            logger.error(f"Error searching for novel '{novel_name}': {e}")
            return []
    
    async def get_novel_info(self, novel_url: str) -> Optional[Dict]:
        """Extract novel information from its main page"""
        try:
            response = self.session.get(novel_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract novel information (adjust selectors based on actual HTML)
            title = self._extract_text(soup, ['h1', '.novel-title', '.title'])
            author = self._extract_text(soup, ['.author', '.novel-author', '[data-author]'])
            description = self._extract_text(soup, ['.description', '.novel-description', '.summary'])
            
            # Get chapter list
            chapter_links = self._extract_chapter_links(soup, novel_url)
            
            return {
                'title': title,
                'author': author,
                'description': description,
                'url': novel_url,
                'total_chapters': len(chapter_links),
                'chapter_links': chapter_links
            }
            
        except Exception as e:
            logger.error(f"Error extracting novel info from {novel_url}: {e}")
            return None
    
    async def extract_chapter_content(self, chapter_url: str, chapter_number: int) -> Optional[ChapterData]:
        """Extract content from a single chapter"""
        try:
            if self.use_selenium:
                return await self._extract_chapter_selenium(chapter_url, chapter_number)
            else:
                return await self._extract_chapter_requests(chapter_url, chapter_number)
                
        except Exception as e:
            logger.error(f"Error extracting chapter {chapter_number} from {chapter_url}: {e}")
            return None
    
    async def _extract_chapter_requests(self, chapter_url: str, chapter_number: int) -> Optional[ChapterData]:
        """Extract chapter content using requests"""
        response = self.session.get(chapter_url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract chapter title and content (adjust selectors based on actual HTML)
        title = self._extract_text(soup, ['h1', '.chapter-title', '.title'])
        
        # Remove navigation elements, ads, etc.
        for unwanted in soup.find_all(['nav', 'footer', '.ads', '.navigation', 'script', 'style']):
            unwanted.decompose()
        
        # Extract main content
        content_elem = soup.find('div', class_='chapter-content') or \
                      soup.find('div', class_='content') or \
                      soup.find('article') or \
                      soup.find('main')
        
        if content_elem:
            content = self._clean_content(content_elem.get_text())
        else:
            # Fallback: try to find text in paragraphs
            paragraphs = soup.find_all('p')
            content = '\n'.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 20])
        
        return ChapterData(
            title=title or f"Chapter {chapter_number}",
            content=content,
            chapter_number=chapter_number,
            url=chapter_url,
            word_count=len(content.split())
        )
    
    async def _extract_chapter_selenium(self, chapter_url: str, chapter_number: int) -> Optional[ChapterData]:
        """Extract chapter content using Selenium for dynamic content"""
        if not self.driver:
            self.driver = self._setup_selenium_driver()
        
        self.driver.get(chapter_url)
        
        # Wait for content to load
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Additional wait for dynamic content
        time.sleep(2)
        
        # Extract content
        title_elem = self.driver.find_element(By.CSS_SELECTOR, "h1, .chapter-title, .title")
        title = title_elem.text if title_elem else f"Chapter {chapter_number}"
        
        # Try different content selectors
        content_selectors = ['.chapter-content', '.content', 'article', 'main']
        content = ""
        
        for selector in content_selectors:
            try:
                content_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                content = content_elem.text
                break
            except:
                continue
        
        if not content:
            # Fallback to paragraphs
            paragraphs = self.driver.find_elements(By.TAG_NAME, "p")
            content = '\n'.join([p.text for p in paragraphs if len(p.text.strip()) > 20])
        
        content = self._clean_content(content)
        
        return ChapterData(
            title=title,
            content=content,
            chapter_number=chapter_number,
            url=chapter_url,
            word_count=len(content.split())
        )
    
    def _extract_chapter_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract chapter links from novel page"""
        links = []
        
        # Try different selectors for chapter links
        link_selectors = [
            'a[href*="chapter"]',
            '.chapter-list a',
            '.chapters a',
            'a[href*="/c-"]'  # Common pattern for chapter URLs
        ]
        
        for selector in link_selectors:
            chapter_links = soup.select(selector)
            if chapter_links:
                for link in chapter_links:
                    href = link.get('href')
                    if href:
                        links.append(self._normalize_url(href, base_url))
                break
        
        # Remove duplicates and sort
        links = list(set(links))
        links.sort()
        
        return links
    
    def _extract_text(self, soup: BeautifulSoup, selectors: List[str]) -> str:
        """Extract text using multiple selectors as fallbacks"""
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text(strip=True)
        return ""
    
    def _clean_content(self, content: str) -> str:
        """Clean extracted content"""
        if not content:
            return ""
        
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content)
        
        # Remove common unwanted patterns
        unwanted_patterns = [
            r'Advertisement.*?Advertisement',
            r'Click here to.*?read more',
            r'Next Chapter.*?Previous Chapter',
            r'Chapter \d+ End.*?Chapter \d+ Start',
        ]
        
        for pattern in unwanted_patterns:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
        
        return content.strip()
    
    def _normalize_url(self, url: str, base_url: str = None) -> str:
        """Normalize URL to absolute URL"""
        if url.startswith('http'):
            return url
        elif url.startswith('/'):
            return f"{base_url or self.base_url}{url}"
        else:
            base = base_url or self.base_url
            return f"{base}/{url}"
    
    async def extract_novel_chapters(self, novel_url: str, max_chapters: int = None) -> Optional[NovelData]:
        """Extract all chapters from a novel"""
        try:
            # Get novel info
            novel_info = await self.get_novel_info(novel_url)
            if not novel_info:
                return None
            
            chapter_links = novel_info['chapter_links']
            if max_chapters:
                chapter_links = chapter_links[:max_chapters]
            
            # Extract chapters
            chapters = []
            for i, chapter_url in enumerate(chapter_links, 1):
                logger.info(f"Extracting chapter {i}/{len(chapter_links)}")
                chapter_data = await self.extract_chapter_content(chapter_url, i)
                
                if chapter_data:
                    chapters.append(chapter_data)
                
                # Add delay to avoid overwhelming the server
                await asyncio.sleep(1)
            
            return NovelData(
                title=novel_info['title'],
                author=novel_info['author'],
                description=novel_info['description'],
                chapters=chapters,
                total_chapters=len(chapters),
                url=novel_url
            )
            
        except Exception as e:
            logger.error(f"Error extracting novel chapters: {e}")
            return None
    
    def __del__(self):
        """Cleanup Selenium driver"""
        if self.driver:
            self.driver.quit() 