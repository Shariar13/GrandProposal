"""
Dynamic Proposal Discovery System
Searches for proposal calls and templates online in real-time
Does NOT rely on preset backend templates
"""
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from urllib.parse import quote_plus, urlparse
import re
import json
from typing import Dict, List, Any
import time


class DynamicProposalDiscovery:
    """
    Discovers proposal calls and requirements dynamically from the web
    Searches trusted sources for current open calls and their templates
    """

    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.ua.random
        })

        # Trusted funding body websites
        self.funding_sources = {
            'horizon_europe': {
                'name': 'Horizon Europe',
                'url': 'https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/home',
                'search_patterns': ['horizon europe', 'H2020', 'FP9']
            },
            'nsf': {
                'name': 'National Science Foundation',
                'url': 'https://www.nsf.gov/funding/',
                'search_patterns': ['NSF grant', 'NSF funding']
            },
            'nih': {
                'name': 'National Institutes of Health',
                'url': 'https://grants.nih.gov/',
                'search_patterns': ['NIH grant', 'R01', 'R21']
            },
            'erc': {
                'name': 'European Research Council',
                'url': 'https://erc.europa.eu/apply-grant',
                'search_patterns': ['ERC grant', 'starting grant', 'advanced grant']
            },
            'wellcome': {
                'name': 'Wellcome Trust',
                'url': 'https://wellcome.org/grant-funding',
                'search_patterns': ['Wellcome grant', 'Wellcome funding']
            },
            'gates': {
                'name': 'Gates Foundation',
                'url': 'https://www.gatesfoundation.org/about/how-we-work/general-information/grant-opportunities',
                'search_patterns': ['Gates Foundation grant']
            }
        }

    def discover_open_calls(
        self,
        funding_body: str = None,
        research_area: str = None
    ) -> List[Dict[str, Any]]:
        """
        Discover currently open funding calls from the web
        """
        calls = []

        # Search Google for open calls
        search_queries = []

        if funding_body:
            source_info = self.funding_sources.get(funding_body.lower())
            if source_info:
                search_queries.extend(source_info['search_patterns'])

        if research_area:
            search_queries.append(f"{research_area} grant funding 2024 2025")

        if not search_queries:
            search_queries = ["research grant funding open calls 2024"]

        for query in search_queries[:3]:
            results = self._search_google_for_calls(query)
            calls.extend(results)
            time.sleep(2)

        # Deduplicate
        seen_urls = set()
        unique_calls = []
        for call in calls:
            if call['url'] not in seen_urls:
                seen_urls.add(call['url'])
                unique_calls.append(call)

        return unique_calls[:20]

    def _search_google_for_calls(self, query: str) -> List[Dict]:
        """Search Google for funding calls"""
        calls = []

        try:
            url = f"https://www.google.com/search?q={quote_plus(query)}"
            headers = {
                'User-Agent': self.ua.random,
                'Accept': 'text/html',
            }

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Extract search results
                for result in soup.select('.g'):
                    try:
                        title_elem = result.select_one('h3')
                        title = title_elem.get_text() if title_elem else ""

                        link_elem = result.select_one('a')
                        link = link_elem['href'] if link_elem else ""

                        snippet_elem = result.select_one('.VwiC3b')
                        snippet = snippet_elem.get_text() if snippet_elem else ""

                        # Filter for actual funding calls
                        if any(keyword in title.lower() or keyword in snippet.lower()
                               for keyword in ['grant', 'funding', 'call', 'rfp', 'proposal']):

                            calls.append({
                                'title': title,
                                'url': link,
                                'description': snippet,
                                'source': 'Google Search',
                                'discovered_at': time.time()
                            })

                    except:
                        continue

        except Exception as e:
            print(f"Error searching Google: {e}")

        return calls

    def extract_call_requirements(self, call_url: str) -> Dict[str, Any]:
        """
        Extract requirements from a funding call webpage
        """
        requirements = {
            'url': call_url,
            'title': None,
            'deadline': None,
            'funding_amount': None,
            'eligibility': [],
            'required_sections': [],
            'page_limit': None,
            'submission_process': [],
            'evaluation_criteria': [],
            'raw_content': ""
        }

        try:
            response = requests.get(
                call_url,
                headers={'User-Agent': self.ua.random},
                timeout=15
            )

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Extract title
                title_tag = soup.find('h1')
                if title_tag:
                    requirements['title'] = title_tag.get_text().strip()

                # Get all text
                text = soup.get_text()
                requirements['raw_content'] = text

                # Extract deadline
                deadline_patterns = [
                    r'deadline[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                    r'due[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                    r'submission[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
                ]
                for pattern in deadline_patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        requirements['deadline'] = match.group(1)
                        break

                # Extract funding amount
                amount_patterns = [
                    r'\$\s*([\d,]+(?:\.\d{2})?)\s*(?:million|M)?',
                    r'€\s*([\d,]+(?:\.\d{2})?)\s*(?:million|M)?',
                    r'up to\s*\$?([\d,]+)'
                ]
                for pattern in amount_patterns:
                    match = re.search(pattern, text)
                    if match:
                        requirements['funding_amount'] = match.group(0)
                        break

                # Extract page limit
                page_patterns = [
                    r'(\d+)\s*page\s*limit',
                    r'maximum\s*of\s*(\d+)\s*pages',
                    r'not\s*exceed\s*(\d+)\s*pages'
                ]
                for pattern in page_patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        requirements['page_limit'] = int(match.group(1))
                        break

                # Extract required sections
                section_keywords = [
                    'executive summary', 'abstract', 'introduction',
                    'background', 'literature review', 'methodology',
                    'work plan', 'budget', 'impact', 'innovation',
                    'objectives', 'deliverables', 'timeline'
                ]

                for keyword in section_keywords:
                    if keyword in text.lower():
                        requirements['required_sections'].append(keyword.title())

                # Extract eligibility criteria
                if 'eligibility' in text.lower() or 'eligible' in text.lower():
                    # Find paragraph containing eligibility
                    for p in soup.find_all('p'):
                        p_text = p.get_text().lower()
                        if 'eligib' in p_text:
                            requirements['eligibility'].append(p.get_text().strip())

        except Exception as e:
            print(f"Error extracting requirements from {call_url}: {e}")

        return requirements

    def search_proposal_templates_online(
        self,
        funding_body: str,
        proposal_type: str = None
    ) -> List[Dict[str, Any]]:
        """
        Search for proposal templates online from trusted sources
        """
        templates = []

        # Search queries
        queries = [
            f"{funding_body} proposal template",
            f"{funding_body} grant application template",
            f"{funding_body} successful proposal example",
        ]

        if proposal_type:
            queries.append(f"{funding_body} {proposal_type} template")

        for query in queries[:3]:
            # Search Google
            search_url = f"https://www.google.com/search?q={quote_plus(query)} filetype:pdf OR filetype:doc"

            try:
                response = requests.get(
                    search_url,
                    headers={'User-Agent': self.ua.random},
                    timeout=10
                )

                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    for result in soup.select('.g')[:5]:
                        try:
                            title_elem = result.select_one('h3')
                            title = title_elem.get_text() if title_elem else ""

                            link_elem = result.select_one('a')
                            link = link_elem['href'] if link_elem else ""

                            # Filter for actual templates
                            if any(keyword in title.lower() for keyword in ['template', 'example', 'sample', 'guide']):
                                templates.append({
                                    'title': title,
                                    'url': link,
                                    'type': 'template',
                                    'funding_body': funding_body,
                                    'format': self._detect_file_format(link)
                                })

                        except:
                            continue

                time.sleep(2)

            except Exception as e:
                print(f"Error searching for templates: {e}")

        return templates

    def _detect_file_format(self, url: str) -> str:
        """Detect file format from URL"""
        url_lower = url.lower()
        if '.pdf' in url_lower:
            return 'pdf'
        elif '.doc' in url_lower or '.docx' in url_lower:
            return 'docx'
        elif '.txt' in url_lower:
            return 'txt'
        else:
            return 'webpage'

    def analyze_template_structure(self, template_url: str) -> Dict[str, Any]:
        """
        Analyze a template to extract its structure
        """
        structure = {
            'url': template_url,
            'sections': [],
            'formatting_style': {},
            'estimated_pages': None
        }

        try:
            # If it's a webpage, scrape it
            if '.pdf' not in template_url and '.doc' not in template_url:
                response = requests.get(
                    template_url,
                    headers={'User-Agent': self.ua.random},
                    timeout=15
                )

                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Extract headings as sections
                    for heading in soup.find_all(['h1', 'h2', 'h3']):
                        section_title = heading.get_text().strip()
                        if len(section_title) > 3 and len(section_title) < 100:
                            structure['sections'].append(section_title)

                    # Remove duplicates while preserving order
                    seen = set()
                    unique_sections = []
                    for section in structure['sections']:
                        if section not in seen:
                            seen.add(section)
                            unique_sections.append(section)
                    structure['sections'] = unique_sections

        except Exception as e:
            print(f"Error analyzing template structure: {e}")

        return structure

    def create_dynamic_proposal_structure(
        self,
        funding_body: str,
        research_area: str
    ) -> Dict[str, Any]:
        """
        Create a proposal structure dynamically by searching online
        """
        print(f"Creating dynamic structure for {funding_body} in {research_area}...")

        # Step 1: Find open calls
        calls = self.discover_open_calls(funding_body, research_area)
        print(f"Found {len(calls)} open calls")

        # Step 2: Extract requirements from most relevant call
        requirements = None
        if calls:
            requirements = self.extract_call_requirements(calls[0]['url'])
            print(f"Extracted requirements: {len(requirements['required_sections'])} sections")

        # Step 3: Search for templates
        templates = self.search_proposal_templates_online(funding_body)
        print(f"Found {len(templates)} templates")

        # Step 4: Analyze template structures
        template_structures = []
        for template in templates[:3]:
            structure = self.analyze_template_structure(template['url'])
            if structure['sections']:
                template_structures.append(structure)

        # Step 5: Combine all information
        dynamic_structure = {
            'funding_body': funding_body,
            'research_area': research_area,
            'open_calls': calls[:5],
            'requirements': requirements,
            'templates_found': templates,
            'template_structures': template_structures,
            'recommended_sections': self._merge_section_recommendations(
                requirements,
                template_structures
            ),
            'generated_at': time.time()
        }

        return dynamic_structure

    def _merge_section_recommendations(
        self,
        requirements: Dict,
        template_structures: List[Dict]
    ) -> List[str]:
        """
        Merge section recommendations from requirements and templates
        """
        sections = []

        # Add required sections from call
        if requirements and requirements['required_sections']:
            sections.extend(requirements['required_sections'])

        # Add sections from templates
        section_frequency = {}
        for template in template_structures:
            for section in template['sections']:
                section_frequency[section] = section_frequency.get(section, 0) + 1

        # Add frequently occurring sections
        for section, freq in sorted(section_frequency.items(), key=lambda x: x[1], reverse=True):
            if section not in sections and freq >= 2:
                sections.append(section)

        # Remove duplicates while preserving order
        seen = set()
        unique_sections = []
        for section in sections:
            section_lower = section.lower()
            if section_lower not in seen:
                seen.add(section_lower)
                unique_sections.append(section)

        return unique_sections[:15]  # Limit to 15 sections
