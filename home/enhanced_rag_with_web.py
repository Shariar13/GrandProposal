"""
Enhanced RAG System with Web Scraping
Combines API searches with web scraping for comprehensive research
"""
from .enhanced_rag_system import EnhancedRAGSystem
from .web_scraper import WebScraperSystem
from typing import Dict, List, Any
import time


class EnhancedRAGWithWeb(EnhancedRAGSystem):
    """
    Extended RAG system that includes web scraping capabilities
    Searches:  - arXiv, OpenAlex, Semantic Scholar (APIs)
    - Google Scholar (web scraping)
    - News sources (BBC, Reuters, ScienceDaily)
    - Custom URLs
    """

    def __init__(self):
        super().__init__()
        self.web_scraper = WebScraperSystem()

    def comprehensive_search_with_web(
        self,
        query: str,
        max_results_per_source: int = 50,
        include_news: bool = True,
        custom_urls: List[str] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive search using both APIs and web scraping
        """
        print(f"Starting comprehensive search for: {query}")

        # Step 1: Use original RAG system (APIs)
        print("Step 1: Searching academic databases via APIs...")
        api_results = self.comprehensive_search(query, max_results_per_source)

        # Step 2: Add web scraping results
        print("Step 2: Scraping web sources...")
        web_results = self.web_scraper.comprehensive_web_search(
            query=query,
            include_news=include_news,
            include_scholar=True,
            custom_urls=custom_urls,
            max_results=50
        )

        # Step 3: Merge results
        print("Step 3: Merging and deduplicating results...")
        merged_results = self._merge_results(api_results, web_results)

        # Step 4: Re-analyze combined data
        print("Step 4: Analyzing combined dataset...")
        merged_results = self._reanalyze_combined_data(merged_results)

        print(f"Search complete: {merged_results['total_papers']} papers, {merged_results['total_news']} news articles")

        return merged_results

    def _merge_results(
        self,
        api_results: Dict[str, Any],
        web_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge API and web scraping results
        """
        merged = {
            'total_papers': 0,
            'total_news': 0,
            'papers': [],
            'news_articles': [],
            'sources': {
                'arxiv': 0,
                'openalex': 0,
                'semantic_scholar': 0,
                'google_scholar': 0,
                'news_sources': 0,
                'custom_urls': 0
            },
            'bibliography': {'apa': [], 'bibtex': []},
            'themes': {},
            'methodologies': [],
            'datasets': [],
            'timeline': {},
            'key_researchers': [],
            'research_gaps': []
        }

        # Add API papers
        if 'papers' in api_results:
            merged['papers'].extend(api_results['papers'])
            merged['total_papers'] += len(api_results['papers'])

        # Add web-scraped academic papers
        if 'academic_papers' in web_results:
            # Deduplicate by title
            existing_titles = {p['title'].lower() for p in merged['papers']}

            for paper in web_results['academic_papers']:
                if paper['title'].lower() not in existing_titles:
                    merged['papers'].append(paper)
                    existing_titles.add(paper['title'].lower())
                    merged['total_papers'] += 1
                    merged['sources']['google_scholar'] += 1

        # Add news articles
        if 'news_articles' in web_results:
            merged['news_articles'] = web_results['news_articles']
            merged['total_news'] = len(web_results['news_articles'])
            merged['sources']['news_sources'] = len(web_results['news_articles'])

        # Add custom content
        if 'custom_content' in web_results:
            for content in web_results['custom_content']:
                merged['news_articles'].append(content)
                merged['total_news'] += 1
                merged['sources']['custom_urls'] += 1

        # Copy other metadata from API results
        for key in ['themes', 'methodologies', 'datasets', 'timeline', 'key_researchers', 'research_gaps']:
            if key in api_results:
                merged[key] = api_results[key]

        # Update bibliographies
        for paper in merged['papers']:
            if 'apa_citation' in paper:
                merged['bibliography']['apa'].append(paper['apa_citation'])
            if 'bibtex_citation' in paper:
                merged['bibliography']['bibtex'].append(paper['bibtex_citation'])

        return merged

    def _reanalyze_combined_data(self, merged_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Re-analyze the combined dataset for themes, gaps, etc.
        """
        papers = merged_results['papers']

        if not papers:
            return merged_results

        # Update timeline with all papers
        timeline = {}
        for paper in papers:
            year = paper.get('year', 'Unknown')
            if year and year != 'Unknown':
                timeline[str(year)] = timeline.get(str(year), 0) + 1

        merged_results['timeline'] = dict(sorted(timeline.items()))

        # Extract methodologies from abstracts
        methodology_keywords = [
            'machine learning', 'deep learning', 'neural network', 'CNN', 'RNN',
            'transformer', 'BERT', 'GPT', 'regression', 'classification',
            'clustering', 'reinforcement learning', 'supervised', 'unsupervised',
            'survey', 'experimental', 'simulation', 'statistical analysis'
        ]

        methodology_counts = {}
        for paper in papers:
            abstract = paper.get('abstract', '').lower()
            for method in methodology_keywords:
                if method.lower() in abstract:
                    methodology_counts[method] = methodology_counts.get(method, 0) + 1

        merged_results['methodologies'] = [
            method for method, count in sorted(
                methodology_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:15]
        ]

        # Extract datasets
        dataset_patterns = [
            'ImageNet', 'COCO', 'MNIST', 'CIFAR', 'VOC', 'CelebA',
            'WikiText', 'SQuAD', 'GLUE', 'SuperGLUE', 'CommonCrawl'
        ]

        dataset_counts = {}
        for paper in papers:
            abstract = paper.get('abstract', '')
            for dataset in dataset_patterns:
                if dataset in abstract:
                    dataset_counts[dataset] = dataset_counts.get(dataset, 0) + 1

        merged_results['datasets'] = [
            dataset for dataset, count in sorted(
                dataset_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
        ]

        return merged_results

    def search_with_urls(
        self,
        query: str,
        custom_urls: List[str],
        max_results_per_source: int = 50
    ) -> Dict[str, Any]:
        """
        Search with custom URLs provided by user
        """
        return self.comprehensive_search_with_web(
            query=query,
            max_results_per_source=max_results_per_source,
            include_news=True,
            custom_urls=custom_urls
        )
