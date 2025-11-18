from typing import List, Dict, Tuple, Optional
import random
import re
from collections import defaultdict

class ParaphrasingEngine:
    def __init__(self, citation_manager):
        self.citation_manager = citation_manager
        self.used_templates = defaultdict(list)
        
        self.used_verbs = defaultdict(set)
        self.recent_citation_styles = []
        self.sentence_count = 0
        
        self.reporting_verbs = {
            'finding': {
                'strong': ['demonstrates', 'establishes', 'reveals', 'confirms', 'validates', 'documents'],
                'moderate': ['suggests', 'indicates', 'shows', 'implies', 'reports', 'observes'],
                'tentative': ['proposes', 'hypothesizes', 'posits', 'explores', 'examines']
            },
            'method': {
                'strong': ['employs', 'implements', 'utilizes', 'leverages', 'integrates', 'deploys'],
                'moderate': ['applies', 'adopts', 'incorporates', 'uses', 'introduces'],
                'tentative': ['explores', 'investigates', 'examines', 'tests', 'evaluates']
            },
            'result': {
                'strong': ['achieves', 'attains', 'demonstrates', 'yields', 'produces', 'obtains'],
                'moderate': ['reports', 'observes', 'documents', 'records', 'notes', 'finds'],
                'tentative': ['suggests', 'indicates', 'implies', 'hints at', 'points toward']
            },
            'challenge': {
                'strong': ['highlights', 'identifies', 'exposes', 'reveals', 'uncovers'],
                'moderate': ['notes', 'observes', 'recognizes', 'acknowledges', 'addresses'],
                'tentative': ['suggests', 'hints at', 'implies', 'raises questions about']
            }
        }
        
        self.hedging_phrases = ['appears to', 'seems to', 'tends to', 'may', 'might', 'could']
        self.intensifiers = ['substantially', 'significantly', 'considerably', 'markedly', 'notably', 'particularly']
        
        self.citation_styles = ['integral', 'non_integral', 'narrative', 'parenthetical']
    
    def paraphrase_architecture_details(self, paper: Dict, facts: Dict) -> str:
        authors = self._format_authors(paper.get('authors', []))
        year = paper.get('year', 'n.d.')
        citation_num = self.citation_manager.add_citation(paper)
        
        arch_details = facts.get('architecture_details', '')
        
        if not arch_details or arch_details == 'deep neural network architecture':
            return f"{authors} ({year}) developed a neural network-based detection system [{citation_num}]."
        
        components = []
        if 'architecture:' in arch_details:
            arch_part = arch_details.split('architecture:')[1].split(';')[0].strip()
            components.append(f"utilizing {arch_part}")
        
        if 'components:' in arch_details:
            comp_part = arch_details.split('components:')[1].split(';')[0].strip()
            components.append(f"incorporating {comp_part}")
        
        if 'loss:' in arch_details:
            loss_part = arch_details.split('loss:')[1].split(';')[0].strip()
            components.append(f"optimized with {loss_part}")
        
        if 'optimizer:' in arch_details:
            opt_part = arch_details.split('optimizer:')[1].split(';')[0].strip()
            components.append(f"using {opt_part} optimizer")
        
        if components:
            base = f"{authors} ({year}) developed a detection architecture"
            details = ', '.join(components[:3])
            return f"{base} {details} [{citation_num}]."
        
        return f"{authors} ({year}) proposed an approach based on {arch_details.split(':')[0]} [{citation_num}]."
    
    def paraphrase_training_methodology(self, paper: Dict, facts: Dict) -> str:
        authors = self._format_authors(paper.get('authors', []))
        year = paper.get('year', 'n.d.')
        citation_num = self.citation_manager.add_citation(paper)
        
        training = facts.get('training_details', '')
        dataset = facts.get('dataset_info', '')
        
        if training == 'standard training procedure':
            if dataset and dataset != 'benchmark datasets':
                return f"The model was trained on {dataset} [{citation_num}]."
            return f"{authors} ({year}) employed standard training protocols [{citation_num}]."
        
        parts = []
        if dataset and dataset != 'benchmark datasets':
            parts.append(f"trained on {dataset}")
        
        if training:
            training_clean = training.replace(';', ',')
            parts.append(f"with {training_clean}")
        
        if parts:
            return f"{authors} ({year}) {', '.join(parts)} [{citation_num}]."
        
        return f"{authors} ({year}) implemented rigorous training procedures [{citation_num}]."
    
    def paraphrase_quantitative_results(self, paper: Dict, facts: Dict) -> str:
        authors = self._format_authors(paper.get('authors', []))
        year = paper.get('year', 'n.d.')
        citation_num = self.citation_manager.add_citation(paper)
        
        metrics = facts.get('metrics_detailed', {})
        baselines = facts.get('baseline_comparison', '')
        
        if not metrics:
            result = facts.get('result', 'competitive performance')
            return f"{authors} ({year}) reported {result} [{citation_num}]."
        
        metric_parts = []
        if 'accuracy' in metrics:
            metric_parts.append(f"{metrics['accuracy']} accuracy")
        if 'auc' in metrics:
            metric_parts.append(f"AUC of {metrics['auc']}")
        if 'f1_score' in metrics:
            metric_parts.append(f"F1-score of {metrics['f1_score']}")
        if 'precision' in metrics:
            metric_parts.append(f"{metrics['precision']} precision")
        if 'recall' in metrics:
            metric_parts.append(f"{metrics['recall']} recall")
        
        if not metric_parts:
            return f"{authors} ({year}) demonstrated strong performance metrics [{citation_num}]."
        
        result_str = f"The approach achieved {', '.join(metric_parts[:3])}"
        
        if baselines and baselines != 'state-of-the-art approaches':
            result_str += f", outperforming {baselines}"
        
        return f"{result_str} [{citation_num}]."
    
    def paraphrase_dataset_evaluation(self, paper: Dict, facts: Dict) -> str:
        authors = self._format_authors(paper.get('authors', []))
        year = paper.get('year', 'n.d.')
        citation_num = self.citation_manager.add_citation(paper)
        
        dataset = facts.get('dataset_info', '')
        
        if not dataset or dataset == 'benchmark datasets':
            return f"{authors} ({year}) evaluated their approach on standard benchmark datasets [{citation_num}]."
        
        has_size = '(' in dataset
        
        structures = [
            f"{authors} ({year}) conducted comprehensive evaluation on {dataset} [{citation_num}].",
            f"Experimental validation on {dataset} was performed by {authors} ({year}) [{citation_num}].",
            f"{authors} ({year}) assessed performance using {dataset} [{citation_num}]."
        ]
        
        return random.choice(structures)
    
    def paraphrase_comparative_analysis(self, paper: Dict, facts: Dict) -> str:
        authors = self._format_authors(paper.get('authors', []))
        year = paper.get('year', 'n.d.')
        citation_num = self.citation_manager.add_citation(paper)
        
        baselines = facts.get('baseline_comparison', '')
        metrics = facts.get('metrics_detailed', {})
        
        if not baselines or baselines == 'state-of-the-art approaches':
            return f"{authors} ({year}) compared their method against existing state-of-the-art approaches [{citation_num}]."
        
        if metrics and 'accuracy' in metrics:
            return f"Comparative analysis by {authors} ({year}) demonstrated superiority over {baselines}, achieving {metrics['accuracy']} accuracy [{citation_num}]."
        
        structures = [
            f"{authors} ({year}) benchmarked against {baselines}, demonstrating competitive performance [{citation_num}].",
            f"In comparison with {baselines}, {authors} ({year}) showed improved detection capabilities [{citation_num}].",
            f"{authors} ({year}) outperformed {baselines} across multiple evaluation metrics [{citation_num}]."
        ]
        
        return random.choice(structures)
    
    def paraphrase_technical_contribution(self, paper: Dict, facts: Dict) -> str:
        authors = self._format_authors(paper.get('authors', []))
        year = paper.get('year', 'n.d.')
        citation_num = self.citation_manager.add_citation(paper)
        
        contribution = facts.get('specific_contributions', '')
        
        if not contribution or contribution == 'methodological advances in the domain':
            arch = facts.get('architecture_details', '')
            if arch and arch != 'deep neural network architecture':
                return f"The key contribution of {authors} ({year}) lies in their novel architectural design incorporating {arch.split(':')[0]} [{citation_num}]."
            return f"{authors} ({year}) contributed methodological innovations to the field [{citation_num}]."
        
        if len(contribution) > 100:
            contribution = contribution[:97] + '...'
        
        structures = [
            f"{authors} ({year}) introduced {contribution} [{citation_num}].",
            f"The primary contribution of {authors} ({year}) encompasses {contribution} [{citation_num}].",
            f"{authors} ({year}) advanced the field through {contribution} [{citation_num}]."
        ]
        
        return random.choice(structures)
    
    def paraphrase_limitation_analysis(self, paper: Dict, facts: Dict) -> str:
        authors = self._format_authors(paper.get('authors', []))
        year = paper.get('year', 'n.d.')
        citation_num = self.citation_manager.add_citation(paper)
        
        challenge = facts.get('challenge', '')
        
        if not challenge or challenge == 'challenges in generalization and robustness across diverse conditions':
            return f"However, {authors} ({year}) acknowledged limitations in generalization and robustness [{citation_num}]."
        
        if len(challenge) > 120:
            challenge = challenge[:117] + '...'
        
        challenge_lower = challenge.lower() if challenge[0].isupper() else challenge
        
        structures = [
            f"However, {authors} ({year}) identified that {challenge_lower} [{citation_num}].",
            f"Nevertheless, {authors} ({year}) noted {challenge_lower} [{citation_num}].",
            f"Despite these advances, {authors} ({year}) recognized that {challenge_lower} [{citation_num}]."
        ]
        
        return random.choice(structures)
    
    def synthesize_technical_trends(self, papers: List[Dict], aspect: str) -> str:
        if len(papers) < 2:
            return ""
        
        citation_nums = [self.citation_manager.add_citation(p) for p in papers[:5]]
        citations = f"[{', '.join(map(str, citation_nums))}]"
        
        trends = [
            f"Recent investigations {citations} converge on {aspect} as a critical factor in detection performance.",
            f"Multiple studies {citations} have explored {aspect}, revealing its importance for robust detection.",
            f"Emerging research {citations} highlights {aspect} as central to advancing detection capabilities.",
            f"Consistent findings across studies {citations} emphasize the role of {aspect} in effective detection."
        ]
        
        return random.choice(trends)
    
    def synthesize_performance_comparison(self, papers: List[Dict]) -> str:
        if len(papers) < 3:
            return ""
        
        citation_nums = [self.citation_manager.add_citation(p) for p in papers[:4]]
        citations = f"[{', '.join(map(str, citation_nums))}]"
        
        comparisons = [
            f"Comparative analysis across approaches {citations} reveals substantial performance heterogeneity depending on architectural choices and training strategies.",
            f"Performance evaluation of multiple methods {citations} demonstrates that detection accuracy varies significantly with model complexity and dataset characteristics.",
            f"Recent benchmarking studies {citations} indicate that no single approach dominates across all evaluation scenarios, suggesting context-dependent optimization requirements."
        ]
        
        return random.choice(comparisons)
    
    def paraphrase_finding(self, paper: Dict, facts: Dict) -> str:
        strength = self._assess_claim_strength(facts['finding'])
        verb = self._get_varied_verb('finding', strength)
        
        cite_style = self._select_citation_style()
        author_text, citation = self._format_citation(paper, cite_style)
        
        structures = self._build_finding_structures(author_text, paper['year'], verb, facts['finding'], citation, cite_style)
        sentence = random.choice(structures)
        
        sentence = self._add_hedging_if_appropriate(sentence, strength)
        sentence = self._add_intensifier_if_appropriate(sentence, strength)
        
        self.sentence_count += 1
        return self._clean_sentence(sentence)
    
    def paraphrase_method(self, paper: Dict, facts: Dict) -> str:
        verb = self._get_varied_verb('method', 'strong')
        
        cite_style = self._select_citation_style()
        author_text, citation = self._format_citation(paper, cite_style)
        
        structures = [
            f"{author_text} {verb} {facts['method']} to address {facts['application']} {citation}",
            f"The application of {facts['method']} to {facts['application']} was developed by {author_text} {citation}",
            f"By leveraging {facts['method']}, {author_text} tackled {facts['application']} challenges {citation}",
            f"{facts['method'].capitalize()}-based methodologies for {facts['application']} were introduced {citation}",
            f"In addressing {facts['application']}, {author_text} {verb} {facts['method']} {citation}",
            f"{author_text} advanced {facts['application']} through {facts['method']} {citation}"
        ]
        
        sentence = random.choice(structures)
        self.sentence_count += 1
        return self._clean_sentence(sentence)
    
    def paraphrase_result(self, paper: Dict, facts: Dict) -> str:
        strength = self._assess_result_strength(facts['result'])
        verb = self._get_varied_verb('result', strength)
        
        cite_style = self._select_citation_style()
        author_text, citation = self._format_citation(paper, cite_style)
        
        has_numbers = bool(re.search(r'\d+\.?\d*%?', facts['result']))
        
        if has_numbers and cite_style == 'non_integral':
            structures = [
                f"{facts['result'].capitalize()}, representing {random.choice(self.intensifiers)} improved performance {citation}",
                f"Performance metrics of {facts['result']} were documented {citation}",
                f"{facts['result'].capitalize()} across evaluation scenarios {citation}"
            ]
        else:
            structures = [
                f"{author_text} {verb} {facts['result']} {citation}",
                f"Experimental evaluation by {author_text} yielded {facts['result']} {citation}",
                f"The system developed by {author_text} attained {facts['result']} {citation}",
                f"{facts['result'].capitalize()} emerged from {author_text}'s analysis {citation}"
            ]
        
        sentence = random.choice(structures)
        sentence = self._add_intensifier_if_appropriate(sentence, strength)
        
        self.sentence_count += 1
        return self._clean_sentence(sentence)
    
    def paraphrase_challenge(self, paper: Dict, facts: Dict) -> str:
        verb = self._get_varied_verb('challenge', 'moderate')
        
        cite_style = self._select_citation_style()
        author_text, citation = self._format_citation(paper, cite_style)
        
        markers = ['However', 'Nevertheless', 'Despite these advances', 'Yet', 'Nonetheless', 'Conversely']
        marker = random.choice(markers)
        
        structures = [
            f"{marker}, {author_text} {verb} {facts['challenge']} as a persistent concern {citation}",
            f"{marker}, {facts['challenge']} remain problematic {citation}",
            f"{marker}, the analysis by {author_text} {verb} critical limitations in {facts['challenge']} {citation}",
            f"{marker}, {facts['challenge']} continue to pose challenges {citation}",
            f"{marker}, {author_text} acknowledged that {facts['challenge']} require further investigation {citation}"
        ]
        
        sentence = random.choice(structures)
        self.sentence_count += 1
        return self._clean_sentence(sentence)
    
    def synthesize_multiple(self, papers: List[Dict], topic: str, aspect: str) -> str:
        citation_nums = [self.citation_manager.add_citation(p) for p in papers[:5]]
        citations = f"[{', '.join(map(str, citation_nums))}]"
        
        patterns = ['convergent', 'progressive', 'thematic']
        pattern = random.choice(patterns)
        
        if pattern == 'convergent':
            structures = [
                f"Converging evidence across multiple investigations {citations} demonstrates advances in {aspect} for {topic}",
                f"A consistent pattern emerges from recent studies {citations}, indicating progress in {aspect} within {topic}",
                f"Multiple lines of inquiry {citations} collectively point toward the importance of {aspect} in {topic}",
                f"Substantial consensus exists in the literature {citations} regarding the role of {aspect} in {topic}"
            ]
        elif pattern == 'progressive':
            structures = [
                f"Progressive refinement across studies {citations} has enhanced understanding of {aspect} in {topic}",
                f"Building on foundational work, subsequent investigations {citations} have extended research on {aspect} for {topic}",
                f"The evolution of research {citations} demonstrates advancing sophistication in {aspect} within {topic} domains"
            ]
        else:
            structures = [
                f"Thematic analysis of recent literature {citations} reveals {aspect} as central to {topic}",
                f"Research consistently emphasizes {aspect} in {topic} applications {citations}",
                f"Multiple investigations {citations} have explored {aspect} within {topic} contexts"
            ]
        
        sentence = random.choice(structures)
        self.sentence_count += 1
        return self._clean_sentence(sentence)
    
    def _get_varied_verb(self, verb_type: str, strength: str) -> str:
        available = [v for v in self.reporting_verbs[verb_type][strength] 
                     if v not in self.used_verbs[verb_type]]
        
        if not available:
            self.used_verbs[verb_type].clear()
            available = self.reporting_verbs[verb_type][strength]
        
        verb = random.choice(available)
        self.used_verbs[verb_type].add(verb)
        
        if len(self.used_verbs[verb_type]) > 10:
            oldest = list(self.used_verbs[verb_type])[:3]
            for v in oldest:
                self.used_verbs[verb_type].discard(v)
        
        return verb
    
    def _select_citation_style(self) -> str:
        available = [s for s in self.citation_styles if s not in self.recent_citation_styles[-2:]]
        if not available:
            available = self.citation_styles
        
        style = random.choice(available)
        self.recent_citation_styles.append(style)
        if len(self.recent_citation_styles) > 5:
            self.recent_citation_styles.pop(0)
        
        return style
    
    def _format_citation(self, paper: Dict, style: str) -> Tuple[str, str]:
        citation_num = self.citation_manager.add_citation(paper)
        authors = self._format_authors(paper['authors'])
        year = paper.get('year', 'n.d.')
        
        if style == 'integral':
            return f"{authors} ({year})", f"[{citation_num}]"
        elif style == 'narrative':
            possessive = authors + "'s" if not authors.endswith('al.') else authors + "'"
            return possessive, f"[{citation_num}]"
        elif style == 'parenthetical':
            return f"({authors}, {year})", f"[{citation_num}]"
        else:
            return "", f"[{citation_num}]"
    
    def _format_authors(self, authors: List[str]) -> str:
        if not authors:
            return "Researchers"
        
        last_names = []
        for author in authors[:2]:
            parts = author.split()
            last_names.append(parts[-1] if parts else author)
        
        if len(authors) == 1:
            return last_names[0]
        elif len(authors) == 2:
            return f"{last_names[0]} and {last_names[1]}"
        else:
            return f"{last_names[0]} et al."
    
    def _build_finding_structures(self, author_text: str, year: str, verb: str, 
                                  finding: str, citation: str, cite_style: str) -> List[str]:
        structures = []
        
        if cite_style == 'integral':
            structures.extend([
                f"{author_text} {verb} that {finding} {citation}",
                f"The work of {author_text} {verb} {finding} {citation}",
                f"{author_text} {verb} evidence of {finding} {citation}"
            ])
        elif cite_style == 'narrative':
            structures.extend([
                f"In {author_text} analysis, {finding} {citation}",
                f"{author_text} research {verb} {finding} {citation}",
                f"Through {author_text} investigation, {finding} was documented {citation}"
            ])
        elif cite_style == 'non_integral':
            structures.extend([
                f"{finding.capitalize()} {citation}",
                f"Evidence {verb} {finding} {citation}",
                f"{finding.capitalize()} represents a key advance {citation}"
            ])
        else:
            structures.extend([
                f"Recent work {author_text} {verb} {finding} {citation}",
                f"Investigations {author_text} revealed {finding} {citation}"
            ])
        
        return structures
    
    def _assess_claim_strength(self, finding: str) -> str:
        finding_lower = finding.lower()
        
        strong_indicators = ['demonstrate', 'prove', 'confirm', 'establish', 'validate', 'significant']
        tentative_indicators = ['suggest', 'indicate', 'imply', 'may', 'might', 'could', 'possible']
        
        if any(ind in finding_lower for ind in strong_indicators):
            return 'strong'
        elif any(ind in finding_lower for ind in tentative_indicators):
            return 'tentative'
        else:
            return 'moderate'
    
    def _assess_result_strength(self, result: str) -> str:
        if 'significant' in result.lower() or re.search(r'9\d%', result):
            return 'strong'
        elif 'modest' in result.lower() or 'limited' in result.lower():
            return 'tentative'
        else:
            return 'moderate'
    
    def _add_hedging_if_appropriate(self, sentence: str, strength: str) -> str:
        if strength == 'tentative' and random.random() < 0.5:
            hedge = random.choice(self.hedging_phrases)
            for pattern in [r'\b(demonstrates?|shows?|indicates?)\b']:
                if re.search(pattern, sentence):
                    sentence = re.sub(pattern, f'{hedge} \\1', sentence, count=1)
                    break
        return sentence
    
    def _add_intensifier_if_appropriate(self, sentence: str, strength: str) -> str:
        if strength == 'strong' and random.random() < 0.4:
            intensifier = random.choice(self.intensifiers)
            patterns = [r'\bimprove[sd]?\b', r'\boutperform[s]?\b', r'\benhance[sd]?\b', r'\bsuperior\b']
            for pattern in patterns:
                if re.search(pattern, sentence):
                    sentence = re.sub(pattern, f'{intensifier} \\g<0>', sentence, count=1)
                    break
        return sentence
    
    def _clean_sentence(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\s+([.,;:])', r'\1', text)
        text = text.strip()
        if not text.endswith('.'):
            text += '.'
        return text


class TextPostProcessor:
    @staticmethod
    def clean_text(text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', text)
        text = TextPostProcessor._remove_duplicate_words(text)
        text = TextPostProcessor._remove_duplicate_phrases(text)
        text = TextPostProcessor._fix_incomplete_sentences(text)
        text = TextPostProcessor._split_long_paragraphs(text)
        text = TextPostProcessor._fix_citation_clusters(text)
        text = TextPostProcessor._ensure_proper_spacing(text)
        return text.strip()
    
    @staticmethod
    def _remove_duplicate_words(text: str) -> str:
        text = re.sub(r'\b(\w+)\s+\1\b', r'\1', text, flags=re.IGNORECASE)
        text = re.sub(r'shows?\s+that\s+shows?', 'shows', text, flags=re.IGNORECASE)
        text = re.sub(r'demonstrates?\s+that\s+demonstrates?', 'demonstrates', text, flags=re.IGNORECASE)
        text = re.sub(r'has\s+shown\s+shows', 'has shown', text, flags=re.IGNORECASE)
        return text
    
    @staticmethod
    def _remove_duplicate_phrases(text: str) -> str:
        sentences = re.split(r'([.!?]\s+)', text)
        seen_trigrams = set()
        cleaned_sentences = []
        
        for i in range(0, len(sentences)-1, 2):
            sentence = sentences[i]
            words = sentence.split()
            
            is_duplicate = False
            for j in range(len(words)-2):
                trigram = ' '.join(words[j:j+3]).lower()
                if len(trigram) > 20 and trigram in seen_trigrams:
                    is_duplicate = True
                    break
                seen_trigrams.add(trigram)
            
            if not is_duplicate:
                cleaned_sentences.append(sentence)
                if i+1 < len(sentences):
                    cleaned_sentences.append(sentences[i+1])
            
            if len(seen_trigrams) > 150:
                seen_trigrams = set(list(seen_trigrams)[-100:])
        
        return ''.join(cleaned_sentences)
    
    @staticmethod
    def _fix_incomplete_sentences(text: str) -> str:
        incomplete_endings = [
            r'\s+are\s*[\.\,]', r'\s+is\s*[\.\,]', r'\s+for\s*[\.\,]', 
            r'\s+to\s*[\.\,]', r'\s+the\s*[\.\,]', r'\s+and\s*[\.\,]', 
            r'\s+in\s*[\.\,]', r'\s+of\s*[\.\,]', r'\s+with\s*[\.\,]',
            r'\s+at\s*[\.\,]', r'\s+by\s*[\.\,]', r'\s+from\s*[\.\,]'
        ]
        
        for pattern in incomplete_endings:
            text = re.sub(pattern, '.', text)
        
        sentences = re.split(r'([.!?]\s+)', text)
        complete_sentences = []
        
        for i in range(0, len(sentences)-1, 2):
            sentence = sentences[i].strip()
            separator = sentences[i+1] if i+1 < len(sentences) else ''
            
            if len(sentence.split()) >= 5:
                complete_sentences.append(sentence + separator)
        
        return ''.join(complete_sentences)
    
    @staticmethod
    def _split_long_paragraphs(text: str) -> str:
        sentences = re.split(r'([.!?]\s+)', text)
        result = []
        sentence_count = 0
        
        for i in range(0, len(sentences)-1, 2):
            sentence = sentences[i]
            separator = sentences[i+1] if i+1 < len(sentences) else ''
            result.append(sentence + separator)
            sentence_count += 1
            
            if sentence_count >= 5 and i < len(sentences) - 2:
                result.append('\n\n')
                sentence_count = 0
        
        return ''.join(result)
    
    @staticmethod
    def _fix_citation_clusters(text: str) -> str:
        def limit_citations(match):
            citations = match.group(1).split(',')
            if len(citations) > 4:
                return f"[{','.join(citations[:4])}]"
            return match.group(0)
        
        text = re.sub(r'\[([0-9,\s]+)\]', limit_citations, text)
        return text
    
    @staticmethod
    def _ensure_proper_spacing(text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\s+([.,;:])', r'\1', text)
        text = re.sub(r'\[\s+(\d+)', r'[\1', text)
        text = re.sub(r'(\d+)\s+\]', r'\1]', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'\s*\n\s*', '\n', text)
        return text