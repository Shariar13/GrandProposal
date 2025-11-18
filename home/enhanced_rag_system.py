"""
Enhanced RAG System for Grant Proposal Generation
Collects comprehensive research data with perfect citations for AI generation
"""
import requests
import json
from typing import List, Dict, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from datetime import datetime
import hashlib


class EnhancedRAGSystem:
    """
    Improved RAG system that comprehensively collects and structures research data
    with perfect citations before passing to OpenAI for proposal generation.
    """

    def __init__(self):
        self.arxiv_base_url = "http://export.arxiv.org/api/query"
        self.openalex_base_url = "https://api.openalex.org/works"
        self.crossref_base_url = "https://api.crossref.org/works"
        self.semantic_scholar_base_url = "https://api.semanticscholar.org/graph/v1/paper/search"

        # Rate limiting
        self.last_request_time = {}
        self.min_request_interval = {
            'arxiv': 3,  # 3 seconds between requests
            'openalex': 0.1,  # OpenAlex is more permissive
            'crossref': 0.05,
            'semantic_scholar': 1
        }

    def _rate_limit(self, source: str):
        """Implement rate limiting for API requests"""
        if source in self.last_request_time:
            elapsed = time.time() - self.last_request_time[source]
            if elapsed < self.min_request_interval[source]:
                time.sleep(self.min_request_interval[source] - elapsed)
        self.last_request_time[source] = time.time()

    def search_arxiv(self, query: str, max_results: int = 50) -> List[Dict]:
        """Search arXiv for academic papers"""
        self._rate_limit('arxiv')

        params = {
            'search_query': f'all:{query}',
            'start': 0,
            'max_results': max_results,
            'sortBy': 'relevance',
            'sortOrder': 'descending'
        }

        try:
            response = requests.get(self.arxiv_base_url, params=params, timeout=30)
            response.raise_for_status()

            # Parse XML response
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)

            papers = []
            for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                try:
                    paper = self._parse_arxiv_entry(entry)
                    if paper:
                        papers.append(paper)
                except Exception as e:
                    continue

            return papers
        except Exception as e:
            print(f"Error searching arXiv: {e}")
            return []

    def _parse_arxiv_entry(self, entry) -> Dict:
        """Parse arXiv XML entry into structured data"""
        ns = {'atom': 'http://www.w3.org/2005/Atom', 'arxiv': 'http://arxiv.org/schemas/atom'}

        title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
        summary = entry.find('atom:summary', ns).text.strip().replace('\n', ' ')

        # Authors
        authors = []
        for author in entry.findall('atom:author', ns):
            name_elem = author.find('atom:name', ns)
            if name_elem is not None:
                authors.append(name_elem.text.strip())

        # Publication date
        published = entry.find('atom:published', ns).text.strip()
        year = published.split('-')[0]

        # arXiv ID and URL
        arxiv_id = entry.find('atom:id', ns).text.strip().split('/abs/')[-1]
        url = entry.find('atom:id', ns).text.strip()

        # Categories
        categories = []
        for category in entry.findall('atom:category', ns):
            term = category.get('term')
            if term:
                categories.append(term)

        # DOI if available
        doi = None
        doi_elem = entry.find('arxiv:doi', ns)
        if doi_elem is not None:
            doi = doi_elem.text.strip()

        return {
            'source': 'arXiv',
            'id': arxiv_id,
            'title': title,
            'authors': authors,
            'year': year,
            'abstract': summary,
            'url': url,
            'doi': doi,
            'categories': categories,
            'citation_key': self._generate_citation_key(authors, year, title),
            'apa_citation': self._format_apa_citation(authors, year, title, url, doi),
            'bibtex': self._generate_bibtex(authors, year, title, arxiv_id, doi)
        }

    def search_openalex(self, query: str, max_results: int = 50) -> List[Dict]:
        """Search OpenAlex for academic papers"""
        self._rate_limit('openalex')

        params = {
            'search': query,
            'per_page': max_results,
            'sort': 'relevance_score:desc',
            'filter': 'is_paratext:false'  # Exclude non-research works
        }

        headers = {
            'User-Agent': 'GrantProposalGenerator/1.0 (mailto:research@example.com)'
        }

        try:
            response = requests.get(self.openalex_base_url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()

            papers = []
            for result in data.get('results', []):
                try:
                    paper = self._parse_openalex_result(result)
                    if paper:
                        papers.append(paper)
                except Exception as e:
                    continue

            return papers
        except Exception as e:
            print(f"Error searching OpenAlex: {e}")
            return []

    def _parse_openalex_result(self, result: Dict) -> Dict:
        """Parse OpenAlex result into structured data"""
        title = result.get('title', 'Untitled')

        # Authors
        authors = []
        for authorship in result.get('authorships', []):
            author = authorship.get('author', {})
            display_name = author.get('display_name')
            if display_name:
                authors.append(display_name)

        # Publication year
        year = str(result.get('publication_year', 'n.d.'))

        # Abstract
        abstract = ''
        if result.get('abstract_inverted_index'):
            # Reconstruct abstract from inverted index
            inverted_index = result['abstract_inverted_index']
            word_positions = []
            for word, positions in inverted_index.items():
                for pos in positions:
                    word_positions.append((pos, word))
            word_positions.sort()
            abstract = ' '.join([word for _, word in word_positions])

        # DOI
        doi = result.get('doi', '').replace('https://doi.org/', '')

        # URL
        url = result.get('doi', result.get('id', ''))

        # Citations count
        cited_by_count = result.get('cited_by_count', 0)

        # Concepts/Keywords
        concepts = [concept.get('display_name') for concept in result.get('concepts', [])[:10]]

        return {
            'source': 'OpenAlex',
            'id': result.get('id', ''),
            'title': title,
            'authors': authors,
            'year': year,
            'abstract': abstract,
            'url': url,
            'doi': doi,
            'cited_by_count': cited_by_count,
            'concepts': concepts,
            'citation_key': self._generate_citation_key(authors, year, title),
            'apa_citation': self._format_apa_citation(authors, year, title, url, doi),
            'bibtex': self._generate_bibtex(authors, year, title, doi=doi)
        }

    def search_semantic_scholar(self, query: str, max_results: int = 50) -> List[Dict]:
        """Search Semantic Scholar for academic papers"""
        self._rate_limit('semantic_scholar')

        params = {
            'query': query,
            'limit': max_results,
            'fields': 'title,authors,year,abstract,citationCount,url,externalIds,publicationTypes,influentialCitationCount'
        }

        try:
            response = requests.get(self.semantic_scholar_base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            papers = []
            for result in data.get('data', []):
                try:
                    paper = self._parse_semantic_scholar_result(result)
                    if paper:
                        papers.append(paper)
                except Exception as e:
                    continue

            return papers
        except Exception as e:
            print(f"Error searching Semantic Scholar: {e}")
            return []

    def _parse_semantic_scholar_result(self, result: Dict) -> Dict:
        """Parse Semantic Scholar result into structured data"""
        title = result.get('title', 'Untitled')

        # Authors
        authors = [author.get('name', '') for author in result.get('authors', [])]

        # Year
        year = str(result.get('year', 'n.d.'))

        # Abstract
        abstract = result.get('abstract', '')

        # DOI and other IDs
        external_ids = result.get('externalIds', {})
        doi = external_ids.get('DOI', '')
        arxiv_id = external_ids.get('ArXiv', '')

        # URL
        url = result.get('url', '')

        # Citations
        citation_count = result.get('citationCount', 0)
        influential_citation_count = result.get('influentialCitationCount', 0)

        return {
            'source': 'Semantic Scholar',
            'id': result.get('paperId', ''),
            'title': title,
            'authors': authors,
            'year': year,
            'abstract': abstract,
            'url': url,
            'doi': doi,
            'arxiv_id': arxiv_id,
            'citation_count': citation_count,
            'influential_citation_count': influential_citation_count,
            'citation_key': self._generate_citation_key(authors, year, title),
            'apa_citation': self._format_apa_citation(authors, year, title, url, doi),
            'bibtex': self._generate_bibtex(authors, year, title, doi=doi, arxiv_id=arxiv_id)
        }

    def comprehensive_search(self, query: str, max_results_per_source: int = 50) -> Dict[str, Any]:
        """
        Perform comprehensive search across all sources in parallel
        Returns structured data ready for AI generation
        """
        print(f"🔍 Starting comprehensive search for: {query}")

        # Parallel search across all sources
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(self.search_arxiv, query, max_results_per_source): 'arxiv',
                executor.submit(self.search_openalex, query, max_results_per_source): 'openalex',
                executor.submit(self.search_semantic_scholar, query, max_results_per_source): 'semantic_scholar',
            }

            results = {}
            for future in as_completed(futures):
                source = futures[future]
                try:
                    papers = future.result()
                    results[source] = papers
                    print(f"✓ Retrieved {len(papers)} papers from {source}")
                except Exception as e:
                    print(f"✗ Error retrieving from {source}: {e}")
                    results[source] = []

        # Combine and deduplicate
        all_papers = self._combine_and_deduplicate(results)
        print(f"📚 Total unique papers after deduplication: {len(all_papers)}")

        # Rank by relevance and quality
        ranked_papers = self._rank_papers(all_papers, query)

        # Extract key information
        structured_data = self._structure_research_data(ranked_papers, query)

        return structured_data

    def _combine_and_deduplicate(self, results: Dict[str, List[Dict]]) -> List[Dict]:
        """Combine papers from different sources and remove duplicates"""
        seen_titles = set()
        seen_dois = set()
        unique_papers = []

        # Flatten all papers
        all_papers = []
        for source, papers in results.items():
            all_papers.extend(papers)

        for paper in all_papers:
            title_normalized = paper['title'].lower().strip()
            doi = paper.get('doi', '').strip()

            # Check for duplicates
            is_duplicate = False

            if doi and doi in seen_dois:
                is_duplicate = True
            elif title_normalized in seen_titles:
                is_duplicate = True

            if not is_duplicate:
                unique_papers.append(paper)
                seen_titles.add(title_normalized)
                if doi:
                    seen_dois.add(doi)

        return unique_papers

    def _rank_papers(self, papers: List[Dict], query: str) -> List[Dict]:
        """Rank papers by relevance and quality"""
        # Simple ranking based on:
        # 1. Title/abstract relevance to query
        # 2. Citation count (if available)
        # 3. Recency

        query_terms = set(query.lower().split())

        for paper in papers:
            score = 0

            # Relevance score based on query terms
            title_terms = set(paper['title'].lower().split())
            abstract_terms = set(paper['abstract'].lower().split()) if paper['abstract'] else set()

            title_overlap = len(query_terms & title_terms)
            abstract_overlap = len(query_terms & abstract_terms)

            score += title_overlap * 10  # Title matches weighted more
            score += abstract_overlap * 2

            # Citation count (normalize)
            citation_count = paper.get('cited_by_count', paper.get('citation_count', 0))
            score += min(citation_count / 100, 10)  # Cap at 10 points

            # Recency (more recent is better)
            try:
                year = int(paper['year'])
                current_year = datetime.now().year
                if year >= current_year - 3:
                    score += 5
                elif year >= current_year - 5:
                    score += 3
                elif year >= current_year - 10:
                    score += 1
            except:
                pass

            paper['relevance_score'] = score

        # Sort by relevance score
        papers.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)

        return papers

    def _structure_research_data(self, papers: List[Dict], query: str) -> Dict[str, Any]:
        """Structure research data for AI generation"""

        # Take top papers
        top_papers = papers[:100]  # Use top 100 papers

        # Organize by themes/topics (simple clustering by shared terms)
        themes = self._extract_themes(top_papers)

        # Extract methodologies
        methodologies = self._extract_methodologies(top_papers)

        # Extract datasets mentioned
        datasets = self._extract_datasets(top_papers)

        # Create citation library
        citation_library = {paper['citation_key']: paper for paper in top_papers}

        # Generate structured output
        structured_data = {
            'query': query,
            'total_papers': len(top_papers),
            'collection_date': datetime.now().isoformat(),

            # Papers organized by relevance
            'papers': top_papers,

            # Citation library for easy reference
            'citation_library': citation_library,

            # Structured insights
            'themes': themes,
            'methodologies': methodologies,
            'datasets': datasets,

            # Bibliography in multiple formats
            'bibliography': {
                'apa': [paper['apa_citation'] for paper in top_papers],
                'bibtex': [paper['bibtex'] for paper in top_papers],
            },

            # Research gaps and opportunities
            'research_gaps': self._identify_research_gaps(top_papers, themes),

            # Timeline of research
            'timeline': self._create_research_timeline(top_papers),

            # Key researchers
            'key_researchers': self._identify_key_researchers(top_papers),
        }

        return structured_data

    def _extract_themes(self, papers: List[Dict]) -> Dict[str, List[str]]:
        """Extract major themes from papers"""
        themes = {}

        # Use concepts/categories from papers
        for paper in papers:
            concepts = paper.get('concepts', paper.get('categories', []))
            for concept in concepts:
                if concept not in themes:
                    themes[concept] = []
                themes[concept].append(paper['citation_key'])

        # Sort by frequency
        sorted_themes = {k: v for k, v in sorted(themes.items(), key=lambda x: len(x[1]), reverse=True)}

        return sorted_themes

    def _extract_methodologies(self, papers: List[Dict]) -> List[str]:
        """Extract methodologies mentioned in papers"""
        # Common research methodologies
        methodology_keywords = [
            'neural network', 'deep learning', 'machine learning', 'CNN', 'RNN', 'LSTM',
            'transformer', 'GAN', 'reinforcement learning', 'supervised learning',
            'unsupervised learning', 'semi-supervised', 'transfer learning',
            'survey', 'experiment', 'case study', 'interview', 'ethnography',
            'meta-analysis', 'systematic review', 'RCT', 'longitudinal study'
        ]

        found_methodologies = set()
        for paper in papers:
            text = (paper['title'] + ' ' + paper['abstract']).lower()
            for methodology in methodology_keywords:
                if methodology.lower() in text:
                    found_methodologies.add(methodology)

        return list(found_methodologies)

    def _extract_datasets(self, papers: List[Dict]) -> List[str]:
        """Extract datasets mentioned in papers"""
        # Common datasets
        dataset_keywords = [
            'ImageNet', 'COCO', 'MNIST', 'CIFAR', 'Pascal VOC',
            'FaceForensics', 'Celeb-DF', 'DFDC', 'DeepFake',
            'SQuAD', 'GLUE', 'SuperGLUE', 'WikiText', 'BookCorpus',
            'Common Crawl', 'LAION', 'OpenImages'
        ]

        found_datasets = set()
        for paper in papers:
            text = (paper['title'] + ' ' + paper['abstract'])
            for dataset in dataset_keywords:
                if dataset in text:
                    found_datasets.add(dataset)

        return list(found_datasets)

    def _identify_research_gaps(self, papers: List[Dict], themes: Dict) -> List[str]:
        """Identify potential research gaps"""
        gaps = []

        # Analyze abstracts for gap-indicating phrases
        gap_phrases = [
            'however', 'limited', 'few studies', 'gap', 'challenge', 'open problem',
            'future work', 'remains unclear', 'poorly understood', 'needs further'
        ]

        for paper in papers[:20]:  # Check top 20 papers
            abstract = paper['abstract'].lower()
            for phrase in gap_phrases:
                if phrase in abstract:
                    # Extract sentence containing the phrase
                    sentences = abstract.split('.')
                    for sentence in sentences:
                        if phrase in sentence:
                            gaps.append(sentence.strip())
                            break

        return gaps[:10]  # Return top 10 gaps

    def _create_research_timeline(self, papers: List[Dict]) -> Dict[str, int]:
        """Create timeline of research by year"""
        timeline = {}
        for paper in papers:
            year = paper['year']
            if year != 'n.d.':
                timeline[year] = timeline.get(year, 0) + 1

        return dict(sorted(timeline.items()))

    def _identify_key_researchers(self, papers: List[Dict]) -> List[Dict[str, Any]]:
        """Identify key researchers based on authorship and citations"""
        author_stats = {}

        for paper in papers:
            citation_count = paper.get('cited_by_count', paper.get('citation_count', 0))
            for author in paper['authors']:
                if author not in author_stats:
                    author_stats[author] = {
                        'name': author,
                        'paper_count': 0,
                        'total_citations': 0,
                        'papers': []
                    }
                author_stats[author]['paper_count'] += 1
                author_stats[author]['total_citations'] += citation_count
                author_stats[author]['papers'].append(paper['citation_key'])

        # Sort by paper count and citations
        key_researchers = sorted(
            author_stats.values(),
            key=lambda x: (x['paper_count'], x['total_citations']),
            reverse=True
        )

        return key_researchers[:20]  # Top 20 researchers

    def _generate_citation_key(self, authors: List[str], year: str, title: str) -> str:
        """Generate unique citation key"""
        if not authors:
            first_author = "Unknown"
        else:
            first_author = authors[0].split()[-1]  # Last name

        # Clean title for key
        title_words = title.split()[:3]
        title_part = ''.join([w.capitalize() for w in title_words])

        return f"{first_author}{year}{title_part}"

    def _format_apa_citation(self, authors: List[str], year: str, title: str, url: str, doi: str = None) -> str:
        """Format citation in APA style"""
        # Format authors
        if not authors:
            author_str = "Unknown"
        elif len(authors) == 1:
            author_str = authors[0]
        elif len(authors) == 2:
            author_str = f"{authors[0]} & {authors[1]}"
        elif len(authors) <= 20:
            author_str = ", ".join(authors[:-1]) + f", & {authors[-1]}"
        else:
            author_str = ", ".join(authors[:19]) + ", ... " + authors[-1]

        # Build citation
        citation = f"{author_str} ({year}). {title}."

        if doi:
            citation += f" https://doi.org/{doi}"
        elif url:
            citation += f" {url}"

        return citation

    def _generate_bibtex(self, authors: List[str], year: str, title: str,
                         arxiv_id: str = None, doi: str = None) -> str:
        """Generate BibTeX entry"""
        # Create citation key
        citation_key = self._generate_citation_key(authors, year, title)

        # Format authors for BibTeX
        author_str = " and ".join(authors) if authors else "Unknown"

        # Determine entry type
        if arxiv_id:
            entry_type = "article"
            extra_fields = f"  eprint = {{{arxiv_id}}},\n  archivePrefix = {{arXiv}},\n"
        else:
            entry_type = "article"
            extra_fields = ""

        if doi:
            extra_fields += f"  doi = {{{doi}}},\n"

        bibtex = f"""@{entry_type}{{{citation_key},
  author = {{{author_str}}},
  title = {{{title}}},
  year = {{{year}}},
{extra_fields}}}"""

        return bibtex
