import requests
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

from .citation_manager import CitationManager, FactExtractor
from .paraphrasing import ParaphrasingEngine, TextPostProcessor


class OpenAccessRetriever:
    def __init__(self):
        self.arxiv_base = "http://export.arxiv.org/api/query"
        self.openalex_base = "https://api.openalex.org/works"
        self.crossref_base = "https://api.crossref.org/works"
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'GrantProposalGenerator/1.0'})
        
    def search_arxiv(self, query: str, max_results: int = 25) -> List[Dict]:
        params = {
            'search_query': f'all:{query}',
            'start': 0,
            'max_results': max_results,
            'sortBy': 'relevance',
            'sortOrder': 'descending'
        }
        
        try:
            response = self.session.get(self.arxiv_base, params=params, timeout=60)
            if response.status_code == 200:
                return self._parse_arxiv_xml(response.text)
        except Exception as e:
            print(f"arXiv error: {e}")
        return []
    
    def search_openalex(self, query: str, max_results: int = 25) -> List[Dict]:
        params = {
            'search': query,
            'filter': 'is_oa:true',
            'per-page': max_results,
            'mailto': 'researcher@institution.edu'
        }
        
        try:
            response = self.session.get(self.openalex_base, params=params, timeout=60)
            if response.status_code == 200:
                data = response.json()
                results = []
                for work in data.get('results', []):
                    abstract = work.get('abstract_inverted_index', {})
                    abstract_text = self._reconstruct_abstract(abstract) if abstract else ''
                    
                    if not abstract_text or len(abstract_text) < 100:
                        continue
                    
                    results.append({
                        'title': work.get('title', ''),
                        'abstract': abstract_text,
                        'authors': [a.get('author', {}).get('display_name', '') for a in work.get('authorships', [])[:5]],
                        'year': work.get('publication_year', ''),
                        'doi': work.get('doi', '').replace('https://doi.org/', '') if work.get('doi') else '',
                        'url': work.get('doi', ''),
                        'source': 'OpenAlex',
                        'venue': work.get('primary_location', {}).get('source', {}).get('display_name', ''),
                        'cited_by_count': work.get('cited_by_count', 0)
                    })
                return results
        except Exception as e:
            print(f"OpenAlex error: {e}")
        return []
    
    def search_crossref(self, query: str, max_results: int = 25) -> List[Dict]:
        params = {
            'query': query,
            'rows': max_results,
            'filter': 'type:journal-article',
            'select': 'DOI,title,author,abstract,published,container-title'
        }
        
        for attempt in range(3):
            try:
                response = self.session.get(self.crossref_base, params=params, timeout=60)
                if response.status_code == 200:
                    data = response.json()
                    results = []
                    for item in data.get('message', {}).get('items', []):
                        title = item.get('title', [''])[0] if item.get('title') else ''
                        abstract = item.get('abstract', '')
                        
                        if not title or not abstract or len(abstract) < 100:
                            continue
                        
                        authors = []
                        for a in item.get('author', [])[:5]:
                            name = f"{a.get('given', '')} {a.get('family', '')}".strip()
                            if name:
                                authors.append(name)
                        
                        year = ''
                        if 'published' in item:
                            date_parts = item['published'].get('date-parts', [[]])
                            if date_parts and date_parts[0]:
                                year = str(date_parts[0][0])
                        
                        results.append({
                            'title': title,
                            'abstract': abstract,
                            'authors': authors,
                            'year': year,
                            'doi': item.get('DOI', ''),
                            'url': f"https://doi.org/{item.get('DOI', '')}",
                            'source': 'Crossref',
                            'venue': item.get('container-title', [''])[0] if item.get('container-title') else ''
                        })
                    return results
            except requests.exceptions.Timeout:
                if attempt < 2:
                    time.sleep(3)
                    continue
                print(f"Crossref timeout after {attempt + 1} attempts")
            except Exception as e:
                print(f"Crossref error: {e}")
                break
        return []
    
    def _reconstruct_abstract(self, inverted_index: Dict) -> str:
        if not inverted_index:
            return ''
        word_positions = []
        for word, positions in inverted_index.items():
            for pos in positions:
                word_positions.append((pos, word))
        word_positions.sort()
        return ' '.join([word for _, word in word_positions])
    
    def _parse_arxiv_xml(self, xml_text: str) -> List[Dict]:
        import xml.etree.ElementTree as ET
        results = []
        try:
            root = ET.fromstring(xml_text)
            namespace = {'atom': 'http://www.w3.org/2005/Atom'}
            
            for entry in root.findall('atom:entry', namespace):
                title = entry.find('atom:title', namespace)
                summary = entry.find('atom:summary', namespace)
                published = entry.find('atom:published', namespace)
                authors = entry.findall('atom:author/atom:name', namespace)
                link = entry.find('atom:id', namespace)
                
                title_text = title.text.strip().replace('\n', ' ') if title is not None else ''
                abstract_text = summary.text.strip().replace('\n', ' ') if summary is not None else ''
                
                if not title_text or not abstract_text or len(abstract_text) < 100:
                    continue
                
                arxiv_id = link.text.split('/abs/')[-1] if link is not None else ''
                
                results.append({
                    'title': title_text,
                    'abstract': abstract_text,
                    'authors': [a.text for a in authors[:5]],
                    'year': published.text[:4] if published is not None else '',
                    'doi': f"arXiv:{arxiv_id}",
                    'url': link.text if link is not None else '',
                    'source': 'arXiv',
                    'venue': 'arXiv preprint'
                })
        except Exception as e:
            print(f"XML parsing error: {e}")
        return results
    
    def retrieve_parallel(self, query: str, max_per_source: int = 25) -> List[Dict]:
        all_results = []
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(self.search_arxiv, query, max_per_source): 'arxiv',
                executor.submit(self.search_openalex, query, max_per_source): 'openalex',
                executor.submit(self.search_crossref, query, max_per_source): 'crossref'
            }
            
            for future in as_completed(futures, timeout=180):
                source = futures[future]
                try:
                    results = future.result()
                    print(f"Retrieved {len(results)} papers from {source}")
                    all_results.extend(results)
                except Exception as e:
                    print(f"{source} retrieval failed: {e}")
        
        return all_results


class AdvancedPaperAnalyzer:
    def __init__(self, fact_extractor: FactExtractor):
        self.fact_extractor = fact_extractor
    
    def cluster_by_architecture(self, papers: List[Dict]) -> Dict[str, List[Dict]]:
        clusters = defaultdict(list)
        
        for paper in papers:
            facts = self.fact_extractor.extract_facts(paper)
            arch_details = facts.get('architecture_details', '').lower()
            method = facts.get('method', '').lower()
            
            if 'resnet' in arch_details or 'resnet' in method:
                clusters['ResNet-Based Architectures'].append(paper)
            elif 'transformer' in arch_details or 'vit' in arch_details or 'bert' in arch_details or 'transformer' in method:
                clusters['Transformer-Based Approaches'].append(paper)
            elif 'lstm' in arch_details or 'gru' in arch_details or 'rnn' in method:
                clusters['Recurrent Neural Network Methods'].append(paper)
            elif 'xception' in arch_details or 'efficientnet' in arch_details or 'vgg' in arch_details:
                clusters['CNN-Based Detection Systems'].append(paper)
            elif 'clip' in arch_details or 'clip' in method:
                clusters['Vision-Language Models'].append(paper)
            elif 'ensemble' in method or 'hybrid' in arch_details:
                clusters['Ensemble and Hybrid Methods'].append(paper)
            elif 'gan' in method or 'generative' in method:
                clusters['Generative Model Approaches'].append(paper)
            else:
                clusters['Alternative Approaches'].append(paper)
        
        return {k: v for k, v in clusters.items() if v}
    
    def cluster_by_dataset(self, papers: List[Dict]) -> Dict[str, List[Dict]]:
        clusters = defaultdict(list)
        
        for paper in papers:
            facts = self.fact_extractor.extract_facts(paper)
            dataset_info = facts.get('dataset_info', '').lower()
            
            if 'faceforensics' in dataset_info:
                clusters['FaceForensics++ Dataset'].append(paper)
            elif 'celeb-df' in dataset_info or 'celebdf' in dataset_info:
                clusters['Celeb-DF Dataset'].append(paper)
            elif 'dfdc' in dataset_info or 'deepfake detection challenge' in dataset_info:
                clusters['DFDC Dataset'].append(paper)
            elif 'imagenet' in dataset_info:
                clusters['ImageNet-Based'].append(paper)
            elif 'wild' in dataset_info or 'real-world' in dataset_info:
                clusters['Real-World Datasets'].append(paper)
            else:
                clusters['Various Datasets'].append(paper)
        
        return {k: v for k, v in clusters.items() if v}
    
    def cluster_by_performance(self, papers: List[Dict]) -> Dict[str, List[Dict]]:
        high_performers = []
        medium_performers = []
        emerging_methods = []
        no_metrics = []
        
        for paper in papers:
            facts = self.fact_extractor.extract_facts(paper)
            metrics = facts.get('metrics_detailed', {})
            
            if 'accuracy' in metrics:
                try:
                    acc_str = metrics['accuracy'].replace('%', '').strip()
                    accuracy = float(acc_str)
                    
                    if accuracy >= 95:
                        high_performers.append(paper)
                    elif accuracy >= 90:
                        medium_performers.append(paper)
                    else:
                        emerging_methods.append(paper)
                except (ValueError, AttributeError):
                    no_metrics.append(paper)
            else:
                no_metrics.append(paper)
        
        clusters = {}
        if high_performers:
            clusters['High-Performance Methods (≥95% accuracy)'] = high_performers
        if medium_performers:
            clusters['Competitive Methods (90-95% accuracy)'] = medium_performers
        if emerging_methods:
            clusters['Emerging Approaches (<90% accuracy)'] = emerging_methods
        
        return clusters
    
    def cluster_by_methodology(self, papers: List[Dict]) -> Dict[str, List[Dict]]:
        clusters = defaultdict(list)
        
        for paper in papers:
            facts = self.fact_extractor.extract_facts(paper)
            method = facts.get('method', '').lower()
            arch_details = facts.get('architecture_details', '').lower()
            training = facts.get('training_details', '').lower()
            
            if 'frequency' in method or 'frequency' in arch_details or 'fft' in method or 'spectral' in method:
                clusters['Frequency-Domain Analysis'].append(paper)
            elif 'temporal' in method or 'temporal' in arch_details or 'lstm' in arch_details or 'video' in method:
                clusters['Temporal Consistency Methods'].append(paper)
            elif 'attention' in arch_details or 'attention' in method:
                clusters['Attention-Based Methods'].append(paper)
            elif 'transfer learning' in training or 'pre-trained' in arch_details or 'fine-tun' in training:
                clusters['Transfer Learning Approaches'].append(paper)
            elif 'contrastive' in training or 'contrastive' in method:
                clusters['Contrastive Learning Methods'].append(paper)
            elif 'supervised' in method:
                clusters['Supervised Learning Approaches'].append(paper)
            elif 'unsupervised' in method or 'self-supervised' in method:
                clusters['Self-Supervised and Unsupervised Methods'].append(paper)
            else:
                clusters['General Deep Learning Methods'].append(paper)
        
        return {k: v for k, v in clusters.items() if v}
    
    def get_paper_statistics(self, papers: List[Dict]) -> Dict:
        stats = {
            'total_papers': len(papers),
            'architectures': defaultdict(int),
            'datasets': defaultdict(int),
            'avg_accuracy': None,
            'performance_range': None,
            'year_distribution': defaultdict(int),
            'methodologies': defaultdict(int)
        }
        
        accuracies = []
        
        for paper in papers:
            facts = self.fact_extractor.extract_facts(paper)
            
            arch = facts.get('architecture_details', '')
            if 'architecture:' in arch:
                arch_name = arch.split('architecture:')[1].split(';')[0].strip()
                if arch_name:
                    stats['architectures'][arch_name] += 1
            
            dataset = facts.get('dataset_info', '')
            if dataset and dataset != 'benchmark datasets':
                dataset_name = dataset.split('(')[0].strip()
                if dataset_name:
                    stats['datasets'][dataset_name] += 1
            
            metrics = facts.get('metrics_detailed', {})
            if 'accuracy' in metrics:
                try:
                    acc = float(metrics['accuracy'].replace('%', ''))
                    accuracies.append(acc)
                except:
                    pass
            
            year = paper.get('year', '')
            if year and year != 'n.d.':
                stats['year_distribution'][year] += 1
            
            method = facts.get('method', '')
            if method and method != 'computational methodology':
                stats['methodologies'][method] += 1
        
        if accuracies:
            stats['avg_accuracy'] = sum(accuracies) / len(accuracies)
            stats['performance_range'] = (min(accuracies), max(accuracies))
        
        return stats


class ThematicGrouper:
    @staticmethod
    def group_papers_by_theme(papers: List[Dict], extractor: FactExtractor) -> Dict[str, List[Dict]]:
        themes = defaultdict(list)
        
        for paper in papers:
            facts = extractor.extract_facts(paper)
            method = facts.get('method', '').lower()
            application = facts.get('application', '').lower()
            arch_details = facts.get('architecture_details', '').lower()
            
            if 'resnet' in arch_details or 'resnet' in method:
                themes['ResNet-Based Architectures'].append(paper)
            elif 'transformer' in arch_details or 'vit' in arch_details or 'bert' in method:
                themes['Transformer Architectures'].append(paper)
            elif any(kw in method for kw in ['deep learning', 'neural network', 'cnn', 'convolutional']):
                if 'lstm' in arch_details or 'rnn' in method:
                    themes['Recurrent Neural Networks'].append(paper)
                else:
                    themes['Deep Learning Approaches'].append(paper)
            elif any(kw in method for kw in ['machine learning', 'classification', 'regression', 'supervised', 'unsupervised']):
                themes['Machine Learning Methods'].append(paper)
            elif any(kw in application for kw in ['security', 'cybersecurity', 'intrusion', 'attack', 'threat']):
                themes['Security and Privacy'].append(paper)
            elif any(kw in application for kw in ['network', '5g', '6g', 'wireless', 'communication']):
                themes['Network Technologies'].append(paper)
            elif any(kw in application for kw in ['iot', 'edge', 'cloud', 'fog']):
                themes['Edge and Cloud Computing'].append(paper)
            elif any(kw in method for kw in ['optimization', 'algorithm', 'heuristic']):
                themes['Optimization Methods'].append(paper)
            elif 'ensemble' in method or 'hybrid' in arch_details:
                themes['Ensemble and Hybrid Methods'].append(paper)
            elif 'attention' in arch_details:
                themes['Attention-Based Methods'].append(paper)
            else:
                themes['General Approaches'].append(paper)
        
        return dict(themes)


class RAGSystem:
    def __init__(self):
        self.retriever = OpenAccessRetriever()
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.citation_manager = CitationManager()
        self.fact_extractor = FactExtractor()
        self.paraphraser = ParaphrasingEngine(self.citation_manager)
        self.text_processor = TextPostProcessor()
        self.grouper = ThematicGrouper()
        self.analyzer = AdvancedPaperAnalyzer(self.fact_extractor)
        
    def retrieve_and_rank(self, query: str, top_k: int = 30) -> List[Dict]:
        print(f"Starting retrieval for query: {query[:100]}...")
        
        documents = self.retriever.retrieve_parallel(query, max_per_source=25)
        
        print(f"Total documents retrieved: {len(documents)}")
        
        if not documents:
            print("No documents retrieved")
            return []
        
        documents = [doc for doc in documents 
                    if doc.get('title') 
                    and doc.get('abstract') 
                    and len(doc.get('abstract', '')) < 2000
                    and doc.get('authors')]
        
        print(f"Documents after filtering: {len(documents)}")
        
        if not documents:
            print("No documents passed filtering")
            return []
        
        query_embedding = self.embedding_model.encode([query])[0]
        
        doc_texts = [
            f"{doc['title']} {(doc['abstract'][:700] + '...') if len(doc['abstract']) > 700 else doc['abstract']}"
            for doc in documents
        ]

        doc_embeddings = self.embedding_model.encode(doc_texts)
        similarities = np.dot(doc_embeddings, query_embedding) / (
            np.linalg.norm(doc_embeddings, axis=1) * np.linalg.norm(query_embedding))
        
        top_indices = np.argsort(similarities)[::-1][:top_k]
        ranked_docs = [documents[i] for i in top_indices]
        print(f"Returning top {len(ranked_docs)} ranked documents")
        
        return ranked_docs