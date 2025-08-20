#!/usr/bin/env python3
"""
Simple Novel Translation Refiner Demo Server
Works with core dependencies only: requests, beautifulsoup4, python-dotenv, loguru
"""

import json
import re
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import requests
from bs4 import BeautifulSoup
from loguru import logger
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SimpleNovelServer(BaseHTTPRequestHandler):
    
    def log_message(self, format, *args):
        """Override default logging to use loguru"""
        logger.info(f"{self.address_string()} - {format % args}")
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        path = urlparse(self.path).path
        
        if path == '/':
            self.send_json_response({
                "message": "🚀 Novel Translation Refiner Demo Server",
                "status": "running",
                "version": "1.0.0",
                "features": [
                    "✅ Web scraping from any URL",
                    "✅ Basic text cleaning & refinement",
                    "✅ Machine translation artifact removal",
                    "✅ CORS-enabled API endpoints"
                ],
                "endpoints": {
                    "GET /": "Server information",
                    "GET /health": "Health check",
                    "GET /demo-scrape": "Demo web scraping",
                    "POST /api/refine-text": "Text refinement",
                    "POST /api/scrape-url": "Custom URL scraping"
                }
            })
            
        elif path == '/health':
            self.send_json_response({"status": "healthy", "timestamp": self.get_timestamp()})
            
        elif path.startswith('/demo-scrape'):
            self.demo_scrape_page()
            
        else:
            self.send_json_response({"error": "Endpoint not found"}, 404)
    
    def do_POST(self):
        """Handle POST requests"""
        path = urlparse(self.path).path
        
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
            else:
                data = {}
        except Exception as e:
            logger.warning(f"Failed to parse POST data: {e}")
            data = {}
        
        if path == '/api/refine-text':
            self.refine_text(data)
        elif path == '/api/scrape-url':
            self.scrape_url(data)
        else:
            self.send_json_response({"error": "Endpoint not found"}, 404)
    
    def send_json_response(self, data, status_code=200):
        """Send JSON response with proper headers"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def demo_scrape_page(self):
        """Demo web scraping functionality"""
        try:
            logger.info("Running demo scrape...")
            
            # Demo scraping a simple test page
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get('https://httpbin.org/html', headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract and clean content
            text = soup.get_text()
            clean_text = self.clean_text(text)
            
            result = {
                "success": True,
                "demo_url": "https://httpbin.org/html",
                "original_length": len(text),
                "cleaned_length": len(clean_text),
                "sample_text": clean_text[:500] + "..." if len(clean_text) > 500 else clean_text,
                "message": "✅ Demo scraping successful!",
                "processing_info": {
                    "characters_removed": len(text) - len(clean_text),
                    "cleanup_applied": ["extra_whitespace", "brackets", "parentheses"]
                }
            }
            
            logger.success("Demo scrape completed successfully")
            
        except Exception as e:
            logger.error(f"Demo scraping failed: {e}")
            result = {
                "success": False,
                "error": str(e),
                "message": "❌ Demo scraping failed"
            }
        
        self.send_json_response(result)
    
    def scrape_url(self, data):
        """Scrape content from a custom URL"""
        url = data.get('url', '')
        
        if not url:
            self.send_json_response({"error": "URL is required"}, 400)
            return
        
        try:
            logger.info(f"Scraping URL: {url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract basic information
            title = soup.find('title')
            title_text = title.get_text(strip=True) if title else "No title found"
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                element.decompose()
            
            # Extract and clean text
            text = soup.get_text()
            clean_text = self.clean_text(text)
            
            # Basic content analysis
            paragraphs = clean_text.split('\n')
            substantial_paragraphs = [p for p in paragraphs if len(p.strip()) > 50]
            
            result = {
                "success": True,
                "url": url,
                "title": title_text,
                "content_length": len(clean_text),
                "word_count": len(clean_text.split()),
                "paragraph_count": len(substantial_paragraphs),
                "content": clean_text[:2000] + "..." if len(clean_text) > 2000 else clean_text,
                "message": "✅ URL scraping successful!"
            }
            
            logger.success(f"Successfully scraped {url}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            result = {
                "success": False,
                "error": f"Failed to fetch URL: {str(e)}",
                "url": url
            }
        except Exception as e:
            logger.error(f"Scraping failed for {url}: {e}")
            result = {
                "success": False,
                "error": str(e),
                "url": url
            }
        
        self.send_json_response(result)
    
    def refine_text(self, data):
        """Basic text refinement without heavy NLP"""
        text = data.get('text', '')
        
        if not text:
            self.send_json_response({"error": "Text is required"}, 400)
            return
        
        logger.info(f"Refining text ({len(text)} characters)")
        
        try:
            # Apply refinement
            refined = self.advanced_refinement(text)
            changes = self.get_changes(text, refined)
            
            result = {
                "success": True,
                "original_text": text,
                "refined_text": refined,
                "changes_made": changes,
                "confidence_score": self.calculate_confidence(changes),
                "processing_time": 0.1,
                "statistics": {
                    "original_word_count": len(text.split()),
                    "refined_word_count": len(refined.split()),
                    "character_change": len(refined) - len(text),
                    "improvements_applied": len(changes)
                }
            }
            
            logger.success("Text refinement completed")
            
        except Exception as e:
            logger.error(f"Text refinement failed: {e}")
            result = {
                "success": False,
                "error": str(e)
            }
        
        self.send_json_response(result)
    
    def clean_text(self, text):
        """Clean extracted text"""
        if not text:
            return ""
            
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common artifacts
        text = re.sub(r'\[.*?\]', '', text)  # Remove [brackets]
        text = re.sub(r'\(.*?\)', '', text)  # Remove (parentheses) - translator notes
        
        # Fix line breaks
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        return text.strip()
    
    def advanced_refinement(self, text):
        """Enhanced text refinement with more patterns"""
        refined = text
        
        # Machine translation fixes
        mt_fixes = [
            (r'\bthis\s+king\b', 'I'),
            (r'\bthis\s+emperor\b', 'I'),
            (r'\bthis\s+young\s+master\b', 'I'),
            (r'\bthis\s+lord\b', 'I'),
            (r'\bvery\s+much\s+like\b', 'similar to'),
            (r'\bat\s+this\s+time\b', 'now'),
            (r'\bin\s+this\s+moment\b', 'at this moment'),
            (r'\bmore\s+and\s+more\b', 'increasingly'),
            (r'\bwhat\s+kind\s+of\b', 'what'),
            (r'\bthis\s+kind\s+of\b', 'this type of'),
        ]
        
        # Repetition fixes
        repetition_fixes = [
            (r'\bthe\s+the\b', 'the'),
            (r'\bhe\s+he\b', 'he'),
            (r'\bshe\s+she\b', 'she'),
            (r'\bit\s+it\b', 'it'),
            (r'\band\s+and\b', 'and'),
            (r'\bvery\s+very\b', 'very'),
        ]
        
        # Apply all fixes
        all_fixes = mt_fixes + repetition_fixes
        for pattern, replacement in all_fixes:
            refined = re.sub(pattern, replacement, refined, flags=re.IGNORECASE)
        
        # Punctuation fixes
        refined = re.sub(r'\s+([,.!?;:])', r'\1', refined)
        refined = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', refined)
        
        return refined
    
    def get_changes(self, original, refined):
        """Detect and categorize changes made"""
        changes = []
        
        if original != refined:
            # Simple change detection
            if 'this king' in original.lower() or 'this emperor' in original.lower():
                changes.append({
                    "type": "pronoun_fix",
                    "description": "Fixed 'this king/emperor' patterns"
                })
            
            if re.search(r'\b(\w+)\s+\1\b', original, re.IGNORECASE):
                changes.append({
                    "type": "repetition_fix",
                    "description": "Fixed word repetitions"
                })
            
            if 'very much like' in original.lower():
                changes.append({
                    "type": "phrase_improvement",
                    "description": "Improved unnatural phrases"
                })
            
            if len(changes) == 0:
                changes.append({
                    "type": "general_improvement",
                    "description": "Applied general text improvements"
                })
        
        return changes
    
    def calculate_confidence(self, changes):
        """Calculate confidence score based on changes"""
        if not changes:
            return 1.0
        
        base_score = 0.8
        improvement_bonus = len(changes) * 0.05
        return min(1.0, base_score + improvement_bonus)
    
    def get_timestamp(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()

def main():
    """Start the demo server"""
    port = int(os.getenv('PORT', 8000))
    
    # Setup logging
    logger.remove()  # Remove default handler
    logger.add(
        lambda msg: print(msg, end=''),
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
        colorize=True
    )
    
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleNovelServer)
    
    logger.success("🚀 Novel Translation Refiner Demo Server")
    logger.info(f"📍 Server running at http://localhost:{port}")
    logger.info("🔗 Available endpoints:")
    logger.info("   GET  / - Server information & API docs")
    logger.info("   GET  /health - Health check")
    logger.info("   GET  /demo-scrape - Demo web scraping")
    logger.info("   POST /api/refine-text - Text refinement")
    logger.info("   POST /api/scrape-url - Custom URL scraping")
    logger.info("")
    logger.info(f"💡 Quick test: http://localhost:{port}/demo-scrape")
    logger.warning("⛔ Press Ctrl+C to stop the server")
    logger.info("")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.warning("🛑 Server shutdown requested")
        httpd.server_close()
        logger.success("✅ Server stopped cleanly")

if __name__ == '__main__':
    main() 