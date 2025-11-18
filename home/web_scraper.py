"""
Comprehensive Web Scraping System
Scrapes from multiple sources: Google Scholar, arXiv, news sites, and custom URLs
"""
import requests
from bs4 import BeautifulSoup
from newspaper import Article
from urllib.parse import urlparse, quote_plus
import re
import time
from typing import Dict, List, Any
from fake_useragent import UserAgent
import json


class WebScraperSystem:
    """
    Comprehensive web scraping system that collects data from:
    - Google Scholar
    - Academic news sites (Nature News, Science Daily)
    - Trusted news sources (BBC, Reuters, The Guardian)
    - Custom URLs provided by users
    - arXiv papers
    - Research blogs and preprints
    """

    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.ua.random
        })

    def comprehensive_web_search(
        self,
        query: str,
        include_news: bool = True,
        include_scholar: bool = True,
        custom_urls: List[str] = None,
        max_results: int = 50
    ) -> Dict[str, Any]:
        """
        Perform comprehensive web search across all sources
        """
        results = {
            'academic_papers': [],
            'news_articles': [],
            'custom_content': [],
            'total_sources': 0,
            'query': query,
            'timestamp': time.time()
        }

        # 1. Google Scholar search
        if include_scholar:
            scholar_results = self.search_google_scholar(query, max_results=20)
            results['academic_papers'].extend(scholar_results)

        # 2. News sources
        if include_news:
            news_results = self.search_news_sources(query, max_results=15)
            results['news_articles'].extend(news_results)

        # 3. Custom URLs
        if custom_urls:
            for url in custom_urls:
                content = self.extract_url_content(url)
                if content:
                    results['custom_content'].append(content)

        # 4. Academic news
        academic_news = self.search_academic_news(query, max_results=10)
        results['news_articles'].extend(academic_news)

        results['total_sources'] = (
            len(results['academic_papers']) +
            len(results['news_articles']) +
            len(results['custom_content'])
        )

        return results

    def search_google_scholar(self, query: str, max_results: int = 20) -> List[Dict]:
        """
        Scrape Google Scholar for academic papers
        Note: Be respectful of rate limits
        """
        papers = []

        try:
            # Google Scholar search URL
            url = f"https://scholar.google.com/scholar?q={quote_plus(query)}&hl=en"

            headers = {
                'User-Agent': self.ua.random,
                'Accept': 'text/html,application/xhtml+xml',
                'Accept-Language': 'en-US,en;q=0.9',
            }

            response = requests.get(url, headers=headers, timeout=10)
            time.sleep(2)  # Be respectful

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Parse scholar results
                for idx, result in enumerate(soup.select('.gs_ri')):
                    if idx >= max_results:
                        break

                    try:
                        # Extract title
                        title_elem = result.select_one('.gs_rt')
                        title = title_elem.get_text() if title_elem else "Unknown Title"

                        # Clean title (remove [PDF], [HTML], etc.)
                        title = re.sub(r'\[.*?\]', '', title).strip()

                        # Extract link
                        link = title_elem.find('a')['href'] if title_elem and title_elem.find('a') else None

                        # Extract authors and publication info
                        authors_elem = result.select_one('.gs_a')
                        authors_text = authors_elem.get_text() if authors_elem else ""

                        # Parse authors and year
                        authors = []
                        year = None
                        if authors_text:
                            parts = authors_text.split('-')
                            if len(parts) > 0:
                                authors = [a.strip() for a in parts[0].split(',')]
                            # Try to extract year
                            year_match = re.search(r'\b(19|20)\d{2}\b', authors_text)
                            if year_match:
                                year = int(year_match.group())

                        # Extract abstract/snippet
                        abstract_elem = result.select_one('.gs_rs')
                        abstract = abstract_elem.get_text() if abstract_elem else ""

                        # Extract citation count
                        citations = 0
                        cite_elem = result.select_one('.gs_fl a')
                        if cite_elem and 'Cited by' in cite_elem.get_text():
                            cite_match = re.search(r'Cited by (\d+)', cite_elem.get_text())
                            if cite_match:
                                citations = int(cite_match.group(1))

                        paper = {
                            'title': title,
                            'authors': authors,
                            'year': year or 2024,
                            'abstract': abstract,
                            'url': link,
                            'source': 'Google Scholar',
                            'citations': citations,
                            'citation_key': f"Scholar{idx+1}_{year or 2024}",
                            'apa_citation': self._format_apa_citation(
                                authors, year or 2024, title
                            )
                        }

                        papers.append(paper)

                    except Exception as e:
                        print(f"Error parsing scholar result: {e}")
                        continue

        except Exception as e:
            print(f"Error searching Google Scholar: {e}")

        return papers

    def search_news_sources(self, query: str, max_results: int = 15) -> List[Dict]:
        """
        Search trusted news sources: BBC, Reuters, The Guardian, NYTimes
        """
        articles = []

        news_sources = [
            {
                'name': 'BBC News',
                'search_url': f'https://www.bbc.co.uk/search?q={quote_plus(query)}',
                'domain': 'bbc.co.uk'
            },
            {
                'name': 'The Guardian',
                'search_url': f'https://www.theguardian.com/search?q={quote_plus(query)}',
                'domain': 'theguardian.com'
            },
            {
                'name': 'Reuters',
                'search_url': f'https://www.reuters.com/search/news?blob={quote_plus(query)}',
                'domain': 'reuters.com'
            }
        ]

        for source in news_sources[:2]:  # Limit to avoid rate limits
            try:
                articles.extend(
                    self._scrape_news_source(source, query, max_results=5)
                )
                time.sleep(3)  # Be respectful
            except Exception as e:
                print(f"Error scraping {source['name']}: {e}")

        return articles[:max_results]

    def _scrape_news_source(
        self,
        source: Dict,
        query: str,
        max_results: int = 5
    ) -> List[Dict]:
        """Scrape a specific news source"""
        articles = []

        try:
            headers = {
                'User-Agent': self.ua.random,
                'Accept': 'text/html',
            }

            response = requests.get(source['search_url'], headers=headers, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Find article links (generic selectors)
                links = soup.find_all('a', href=True)

                article_urls = []
                for link in links:
                    href = link.get('href')
                    if href and source['domain'] in href:
                        if href.startswith('http'):
                            article_urls.append(href)
                        elif href.startswith('/'):
                            article_urls.append(f"https://{source['domain']}{href}")

                    if len(article_urls) >= max_results:
                        break

                # Extract content from each article
                for url in article_urls[:max_results]:
                    article_data = self.extract_url_content(url)
                    if article_data:
                        article_data['source'] = source['name']
                        articles.append(article_data)
                    time.sleep(1)

        except Exception as e:
            print(f"Error scraping {source['name']}: {e}")

        return articles

    def search_academic_news(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search academic news sources: Nature News, Science Daily, Phys.org
        """
        articles = []

        # ScienceDaily search
        try:
            url = f"https://www.sciencedaily.com/search/?keyword={quote_plus(query)}"
            response = requests.get(url, headers={'User-Agent': self.ua.random}, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                for idx, item in enumerate(soup.select('.search-result')):
                    if idx >= max_results:
                        break

                    try:
                        title_elem = item.select_one('h3 a')
                        title = title_elem.get_text().strip() if title_elem else ""
                        link = "https://www.sciencedaily.com" + title_elem['href'] if title_elem else ""

                        summary_elem = item.select_one('.summary')
                        summary = summary_elem.get_text().strip() if summary_elem else ""

                        date_elem = item.select_one('.date')
                        date = date_elem.get_text().strip() if date_elem else ""

                        articles.append({
                            'title': title,
                            'content': summary,
                            'url': link,
                            'source': 'ScienceDaily',
                            'date': date,
                            'type': 'academic_news'
                        })
                    except:
                        continue

        except Exception as e:
            print(f"Error searching ScienceDaily: {e}")

        return articles

    def extract_url_content(self, url: str) -> Dict[str, Any]:
        """
        Extract content from any URL using newspaper3k
        """
        try:
            article = Article(url)
            article.download()
            article.parse()
            article.nlp()

            return {
                'title': article.title,
                'authors': article.authors,
                'content': article.text,
                'summary': article.summary,
                'keywords': article.keywords,
                'url': url,
                'publish_date': str(article.publish_date) if article.publish_date else None,
                'top_image': article.top_image,
                'source': urlparse(url).netloc,
                'type': 'web_article'
            }

        except Exception as e:
            print(f"Error extracting content from {url}: {e}")
            return None

    def scrape_arxiv_direct(self, arxiv_id: str) -> Dict[str, Any]:
        """
        Scrape arXiv paper directly by ID
        """
        try:
            url = f"https://arxiv.org/abs/{arxiv_id}"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                title = soup.find('h1', class_='title').get_text().replace('Title:', '').strip()
                authors = [a.get_text() for a in soup.select('.authors a')]
                abstract = soup.find('blockquote', class_='abstract').get_text().replace('Abstract:', '').strip()

                # Get PDF link
                pdf_link = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

                return {
                    'title': title,
                    'authors': authors,
                    'abstract': abstract,
                    'arxiv_id': arxiv_id,
                    'url': url,
                    'pdf_url': pdf_link,
                    'source': 'arXiv',
                    'type': 'academic_paper'
                }

        except Exception as e:
            print(f"Error scraping arXiv {arxiv_id}: {e}")
            return None

    def _format_apa_citation(
        self,
        authors: List[str],
        year: int,
        title: str
    ) -> str:
        """Format citation in APA style"""
        if not authors:
            return f"Unknown. ({year}). {title}."

        if len(authors) == 1:
            author_str = authors[0]
        elif len(authors) == 2:
            author_str = f"{authors[0]} & {authors[1]}"
        else:
            author_str = f"{authors[0]} et al."

        return f"{author_str} ({year}). {title}."

    def search_research_blogs(self, query: str) -> List[Dict]:
        """
        Search popular research blogs and preprint servers
        """
        sources = []

        # Add bioRxiv, medRxiv if relevant
        # This would require specific scrapers for each platform

        return sources
