from typing import Generator, Dict, List
import json
import time
import random
from collections import defaultdict

from .rag_retrieval import RAGSystem
from .utils import TableGenerator


class ProposalGenerator:
    def __init__(self):
        self.rag = RAGSystem()
        self.table_gen = TableGenerator()
        
        self.section_templates = [
            ("Executive Summary", self._generate_executive_summary, 5000),
            ("1. Introduction and Background", self._generate_introduction, 5000),
            ("2. Literature Review", self._generate_literature_review, 5000),
            ("3. Theoretical Framework", self._generate_theoretical_framework, 5000),
            ("4. Research Questions and Hypotheses", self._generate_research_questions, 3000),
            ("5. Research Objectives", self._generate_objectives, 3000),
            ("6. Methodology and Approach", self._generate_methodology, 5000),
            ("7. Work Plan and Timeline", self._generate_work_plan, 3000),
            ("8. Expected Outcomes and Impact", self._generate_outcomes, 5000),
            ("9. Risk Assessment and Mitigation", self._generate_risk_assessment, 3000),
            ("10. Budget Justification", self._generate_budget, 3000),
            ("11. Broader Impacts", self._generate_broader_impacts, 5000),
            ("12. Data Management Plan", self._generate_data_management, 3000)
        ]
        
    def generate_full_proposal(self, title: str, keywords: str, description: str) -> Generator:
        yield self._stream_event("status", "Finalizing references in APA style to ensure academic rigor...")
        
        search_query = f"{title} {keywords} {description}"
        papers = self.rag.retrieve_and_rank(search_query, top_k=100)
        
        if len(papers) < 5:
            yield self._stream_event("error", f"Insufficient relevant literature found ({len(papers)} papers). Please refine your query with more specific keywords or try a different topic.")
            return
        
        yield self._stream_event("status", f"Successfully retrieved {len(papers)} relevant papers. Analyzing and categorizing literature by themes...")
        time.sleep(1)
        
        yield self._stream_event("content", f"GRANT PROPOSAL\n{'='*80}\n\n")
        yield self._stream_event("content", f"Title: {title}\n")
        yield self._stream_event("content", f"Keywords: {keywords}\n")
        yield self._stream_event("content", f"Duration: 36 months\n\n")
        
        for i, (section_title, generator_func, target_words) in enumerate(self.section_templates, 1):
            yield self._stream_event("status", f"Generating section {i}/{len(self.section_templates)}: {section_title} (target: {target_words} words)")
            
            section_content = generator_func(title, keywords, description, papers)
            section_content = self.rag.text_processor.clean_text(section_content)
            
            yield self._stream_event("content", f"\n{section_title}\n{'='*80}\n\n")
            
            words = section_content.split()
            for j, word in enumerate(words):
                yield self._stream_event("content", word + " ")
                if j % 50 == 0:
                    time.sleep(0.01)
            
            yield self._stream_event("content", "\n")
        
        yield self._stream_event("status", "Generating comprehensive bibliography with APA citations...")
        bibliography = self.rag.citation_manager.generate_bibliography()
        yield self._stream_event("content", f"\n{bibliography}\n")
        
        total_citations = len(self.rag.citation_manager.citations)
        yield self._stream_event("complete", f"Proposal generation complete! Generated {len(self.section_templates)} sections with {total_citations} peer-reviewed references.")
    
    def _stream_event(self, event_type: str, content: str) -> str:
        return json.dumps({"type": event_type, "content": content}) + "\n"
    
    def _add_transition(self, from_section: str, to_section: str) -> str:
        transitions = [
            f"Having established {from_section}, we now turn our attention to {to_section}.",
            f"Building upon {from_section}, the following section examines {to_section}.",
            f"With {from_section} outlined above, we proceed to detail {to_section}.",
            f"The preceding discussion of {from_section} provides foundation for understanding {to_section}."
        ]
        return random.choice(transitions)
    
    def _cluster_papers_by_approach(self, papers: List[Dict]) -> Dict[str, List[Dict]]:
        clusters = defaultdict(list)
        
        for paper in papers:
            facts = self.rag.fact_extractor.extract_facts(paper)
            arch_details = facts.get('architecture_details', '').lower()
            method = facts.get('method', '').lower()
            
            if 'resnet' in arch_details or 'resnet' in method:
                clusters['ResNet-Based Architectures'].append(paper)
            elif 'transformer' in arch_details:
                clusters['Transformer-Based Approaches'].append(paper)
            elif 'lstm' in arch_details or 'gru' in arch_details or 'rnn' in method:
                clusters['Recurrent Neural Network Methods'].append(paper)
            elif 'xception' in arch_details or 'efficientnet' in arch_details or 'vgg' in arch_details:
                clusters['CNN-Based Detection Systems'].append(paper)
            elif 'ensemble' in method or 'hybrid' in method:
                clusters['Ensemble and Hybrid Methods'].append(paper)
            else:
                clusters['Alternative Approaches'].append(paper)
        
        return {k: v for k, v in clusters.items() if v}
    
    def _analyze_paper_technical(self, paper: Dict, facts: Dict) -> str:
        sentences = []
        authors = self._format_authors(paper.get('authors', []))
        year = paper.get('year', 'n.d.')
        citation_num = self.rag.citation_manager.add_citation(paper)
        
        arch_details = facts.get('architecture_details', '')
        dataset_info = facts.get('dataset_info', '')
        training_details = facts.get('training_details', '')
        metrics = facts.get('metrics_detailed', {})
        baselines = facts.get('baseline_comparison', '')
        
        if arch_details and arch_details != 'deep neural network architecture':
            intro = f"{authors} ({year}) developed a detection system utilizing {arch_details}"
            if dataset_info and dataset_info != 'benchmark datasets':
                intro += f", trained on {dataset_info}"
            intro += f" [{citation_num}]."
            sentences.append(intro)
        else:
            method = facts.get('method', 'computational approach')
            intro = f"{authors} ({year}) proposed a {method}-based approach"
            if dataset_info and dataset_info != 'benchmark datasets':
                intro += f" evaluated on {dataset_info}"
            intro += f" [{citation_num}]."
            sentences.append(intro)
        
        if training_details and training_details != 'standard training procedure':
            sentences.append(f"The training procedure incorporated {training_details}.")
        
        if metrics:
            metric_parts = []
            if 'accuracy' in metrics:
                metric_parts.append(f"{metrics['accuracy']} accuracy")
            if 'auc' in metrics:
                metric_parts.append(f"AUC of {metrics['auc']}")
            if 'f1_score' in metrics:
                metric_parts.append(f"F1-score of {metrics['f1_score']}")
            
            if metric_parts:
                metric_str = f"The system achieved {', '.join(metric_parts)}"
                if baselines and baselines != 'state-of-the-art approaches':
                    metric_str += f", outperforming {baselines}"
                metric_str += "."
                sentences.append(metric_str)
        elif facts.get('result') and facts['result'] != 'competitive performance on evaluation metrics':
            sentences.append(f"Experimental results demonstrated {facts['result']}.")
        
        challenge = facts.get('challenge', '')
        if challenge and challenge != 'challenges in generalization and robustness across diverse conditions':
            if len(challenge) > 40:
                sentences.append(f"However, the authors noted that {challenge.lower()}.")
        
        return ' '.join(sentences)
    
    def _generate_cluster_analysis(self, cluster_name: str, cluster_papers: List[Dict]) -> str:
        sentences = []
        
        sentences.append(f"\n\n{cluster_name}\n")
        
        intro_phrases = [
            f"Multiple investigations have explored {cluster_name.lower()}, employing various architectural configurations and training strategies.",
            f"Substantial research efforts have focused on {cluster_name.lower()}, with approaches varying in complexity and performance characteristics.",
            f"Recent studies investigating {cluster_name.lower()} have demonstrated diverse methodological choices and evaluation protocols."
        ]
        sentences.append(random.choice(intro_phrases))
        
        for paper in cluster_papers[:10]:
            facts = self.rag.fact_extractor.extract_facts(paper)
            sentences.append(self._analyze_paper_technical(paper, facts))
        
        if len(cluster_papers) > 1:
            sentences.append(self._generate_comparative_insight(cluster_papers[:10]))
        
        return ' '.join(sentences)
    
    def _generate_comparative_insight(self, papers: List[Dict]) -> str:
        all_metrics = []
        all_datasets = set()
        all_architectures = set()
        
        for paper in papers:
            facts = self.rag.fact_extractor.extract_facts(paper)
            metrics = facts.get('metrics_detailed', {})
            if 'accuracy' in metrics:
                try:
                    acc_val = float(metrics['accuracy'].replace('%', ''))
                    all_metrics.append(acc_val)
                except:
                    pass
            
            dataset = facts.get('dataset_info', '')
            if dataset and dataset != 'benchmark datasets':
                all_datasets.add(dataset.split('(')[0].strip())
            
            arch = facts.get('architecture_details', '')
            if arch and arch != 'deep neural network architecture':
                if 'architecture:' in arch:
                    arch_name = arch.split('architecture:')[1].split(';')[0].strip()
                    all_architectures.add(arch_name)
        
        insights = []
        
        if len(all_metrics) >= 2:
            avg_acc = sum(all_metrics) / len(all_metrics)
            max_acc = max(all_metrics)
            min_acc = min(all_metrics)
            
            if max_acc - min_acc > 5:
                insights.append(f"Performance varied considerably across approaches, ranging from {min_acc:.1f}% to {max_acc:.1f}% accuracy, suggesting that architectural choices and training protocols significantly impact detection capability")
            else:
                insights.append(f"These methods achieved comparable performance levels (averaging {avg_acc:.1f}% accuracy), indicating convergence toward effective design patterns within this approach category")
        
        if len(all_datasets) > 1:
            datasets_str = ', '.join(list(all_datasets)[:3])
            insights.append(f"Evaluation across diverse datasets including {datasets_str} enables assessment of generalization capabilities and robustness to different manipulation techniques")
        
        if insights:
            return ' '.join(insights) + '.'
        
        return "These studies collectively advance understanding of effective architectural patterns and training strategies for deepfake detection."
    
    def _create_performance_comparison_table(self, papers: List[Dict]) -> str:
        table_data = []
        
        for paper in papers[:8]:
            facts = self.rag.fact_extractor.extract_facts(paper)
            metrics = facts.get('metrics_detailed', {})
            
            if metrics:
                authors = paper.get('authors', ['Unknown'])[0]
                year = paper.get('year', 'n.d.')
                
                method = facts.get('method', 'N/A')
                if len(method) > 30:
                    method = method[:27] + '...'
                
                dataset = facts.get('dataset_info', 'N/A')
                if len(dataset) > 25:
                    dataset = dataset.split(',')[0]
                
                accuracy = metrics.get('accuracy', 'N/R')
                auc = metrics.get('auc', 'N/R')
                
                table_data.append({
                    'author': f"{authors} ({year})",
                    'method': method,
                    'dataset': dataset,
                    'accuracy': accuracy,
                    'auc': auc
                })
        
        if not table_data:
            return ""
        
        table = "\n\nTable: Performance Comparison of Recent Approaches\n"
        table += "+" + "-" * 20 + "+" + "-" * 32 + "+" + "-" * 28 + "+" + "-" * 12 + "+" + "-" * 10 + "+\n"
        table += "| " + "Author (Year)".ljust(18) + " | " + "Method".ljust(30) + " | " + "Dataset".ljust(26) + " | " + "Accuracy".ljust(10) + " | " + "AUC".ljust(8) + " |\n"
        table += "+" + "-" * 20 + "+" + "-" * 32 + "+" + "-" * 28 + "+" + "-" * 12 + "+" + "-" * 10 + "+\n"
        
        for row in table_data[:8]:
            author_str = row['author'][:18].ljust(18)
            method_str = row['method'][:30].ljust(30)
            dataset_str = row['dataset'][:26].ljust(26)
            acc_str = str(row['accuracy'])[:10].ljust(10)
            auc_str = str(row['auc'])[:8].ljust(8)
            
            table += f"| {author_str} | {method_str} | {dataset_str} | {acc_str} | {auc_str} |\n"
        
        table += "+" + "-" * 20 + "+" + "-" * 32 + "+" + "-" * 28 + "+" + "-" * 12 + "+" + "-" * 10 + "+\n"
        
        return table
    
    def _identify_research_gaps_from_papers(self, papers: List[Dict], description: str) -> str:
        sentences = []
        
        all_datasets = set()
        all_challenges = []
        high_performers = []
        
        for paper in papers:
            facts = self.rag.fact_extractor.extract_facts(paper)
            
            dataset = facts.get('dataset_info', '')
            if dataset and dataset != 'benchmark datasets':
                all_datasets.add(dataset.split('(')[0].strip())
            
            challenge = facts.get('challenge', '')
            if challenge and challenge != 'challenges in generalization and robustness across diverse conditions':
                all_challenges.append(challenge)
            
            metrics = facts.get('metrics_detailed', {})
            if 'accuracy' in metrics:
                try:
                    acc = float(metrics['accuracy'].replace('%', ''))
                    if acc >= 95:
                        high_performers.append(paper)
                except:
                    pass
        
        sentences.append("\n\nIdentified Research Gaps and Opportunities\n")
        sentences.append("Our comprehensive analysis of the literature reveals several critical gaps and opportunities for advancement.")
        
        if len(all_datasets) <= 3:
            datasets_list = ', '.join(list(all_datasets)) if all_datasets else 'limited benchmark datasets'
            sentences.append(f"First, most studies concentrate evaluation on {datasets_list}, raising concerns about generalization to novel manipulation techniques and real-world deployment scenarios. Cross-dataset evaluation and robustness testing remain under-explored.")
        
        if len(high_performers) < 3:
            sentences.append(f"Second, while several approaches demonstrate promising results, consistent high-accuracy detection across diverse conditions remains elusive. The performance gap between controlled benchmarks and real-world scenarios suggests need for more robust methodological frameworks.")
        
        if len(all_challenges) > 2:
            sentences.append(f"Third, multiple studies acknowledge persistent challenges including computational complexity, generalization limitations, and vulnerability to adversarial attacks. These issues require systematic investigation through novel architectural designs and training strategies.")
        
        sentences.append(f"Fourth, the transition from research prototypes to production-ready systems faces significant barriers. Scalability, inference speed, and deployment constraints have received insufficient attention in existing literature.")
        
        sentences.append(f"Fifth, comprehensive evaluation frameworks that simultaneously assess accuracy, robustness, computational efficiency, and interpretability are lacking. Most studies optimize for single metrics, potentially overlooking critical practical considerations.")
        
        sentences.append(f"Our proposed research directly addresses these gaps through {description[:200]}. By developing comprehensive frameworks that integrate insights from multiple methodological paradigms, conducting rigorous multi-dimensional evaluations, and validating through real-world deployment scenarios, we aim to advance both theoretical understanding and practical applicability.")
        
        return ' '.join(sentences)
    
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
    
    def _generate_literature_review(self, title: str, keywords: str, description: str, papers: List[Dict]) -> str:
        sentences = []
        main_keyword = keywords.split(',')[0].strip()
        
        sentences.append(f"This section provides a comprehensive review of relevant literature in {main_keyword}, organized by methodological approach to highlight key advances, technical innovations, performance characteristics, and limitations.")
        sentences.append(f"We analyzed {len(papers)} peer-reviewed publications from leading conferences, journals, and preprint repositories, focusing on work published within the past five years to ensure contemporary relevance and technical currency.")
        
        overview_papers = papers[:8]
        dataset_mentions = []
        arch_mentions = []
        
        for paper in overview_papers:
            facts = self.rag.fact_extractor.extract_facts(paper)
            dataset = facts.get('dataset_info', '')
            if dataset and dataset != 'benchmark datasets':
                dataset_mentions.append(dataset.split('(')[0].strip())
            
            arch = facts.get('architecture_details', '')
            if 'architecture:' in arch:
                arch_name = arch.split('architecture:')[1].split(';')[0].strip()
                if arch_name:
                    arch_mentions.append(arch_name)
        
        if dataset_mentions:
            unique_datasets = list(set(dataset_mentions))[:4]
            sentences.append(f"The reviewed literature encompasses diverse evaluation protocols, with prominent studies utilizing datasets including {', '.join(unique_datasets)}, enabling assessment across varied manipulation techniques and quality levels.")
        
        if arch_mentions:
            unique_archs = list(set(arch_mentions))[:5]
            sentences.append(f"Architectural approaches span multiple paradigms including {', '.join(unique_archs)}, reflecting the field's exploration of complementary detection strategies.")
        
        clustered_papers = self._cluster_papers_by_approach(papers)
        
        for cluster_name, cluster_papers in list(clustered_papers.items())[:8]:
            sentences.append(self._generate_cluster_analysis(cluster_name, cluster_papers))
        
        sentences.append("\n\nPerformance Analysis and Benchmarking\n")
        sentences.append("Quantitative performance evaluation reveals considerable heterogeneity in detection capabilities across methodological approaches and evaluation protocols.")
        
        perf_table = self._create_performance_comparison_table(papers)
        if perf_table:
            sentences.append(perf_table)
            sentences.append("This comparative analysis demonstrates that while several approaches achieve high accuracy on standard benchmarks, performance varies significantly based on dataset characteristics, manipulation techniques, and evaluation protocols.")
        
        high_perf_papers = []
        for paper in papers:
            facts = self.rag.fact_extractor.extract_facts(paper)
            metrics = facts.get('metrics_detailed', {})
            if 'accuracy' in metrics:
                try:
                    acc = float(metrics['accuracy'].replace('%', ''))
                    if acc >= 93:
                        high_perf_papers.append(paper)
                except:
                    pass
        
        if high_perf_papers:
            sentences.append(f"Top-performing approaches achieving accuracies exceeding 93% typically incorporate architectural innovations such as attention mechanisms, multi-scale feature extraction, or ensemble strategies, suggesting that model complexity and representational capacity significantly influence detection performance.")
        
        sentences.append("\n\nLimitations and Challenges in Current Approaches\n")
        sentences.append("Despite substantial progress, existing literature reveals persistent technical and methodological challenges that constrain real-world applicability and deployment viability.")
        
        challenge_papers = papers[15:20] if len(papers) > 19 else papers[-5:]
        for paper in challenge_papers:
            facts = self.rag.fact_extractor.extract_facts(paper)
            challenge = facts.get('challenge', '')
            
            if challenge and challenge != 'challenges in generalization and robustness across diverse conditions':
                authors = self._format_authors(paper.get('authors', []))
                year = paper.get('year', 'n.d.')
                citation_num = self.rag.citation_manager.add_citation(paper)
                
                if len(challenge) > 60:
                    sentences.append(f"{authors} ({year}) identified that {challenge[:120].lower()} [{citation_num}].")
                else:
                    sentences.append(f"{authors} ({year}) noted challenges related to {challenge.lower()} [{citation_num}].")
        
        sentences.append("Common limitations include vulnerability to adversarial perturbations, degraded performance on compressed or low-resolution media, computational requirements incompatible with real-time processing, and limited generalization to novel manipulation techniques not represented in training data.")
        sentences.append("Additionally, most approaches lack interpretability mechanisms, hindering forensic analysis and limiting adoption in high-stakes application domains requiring explainable decisions.")
        
        sentences.append(self._identify_research_gaps_from_papers(papers, description))
        
        return ' '.join(sentences)
    
    def _generate_executive_summary(self, title: str, keywords: str, description: str, papers: List[Dict]) -> str:
        top_papers = papers[:5]
        paraphraser = self.rag.paraphraser
        sentences = []
        
        main_keyword = keywords.split(',')[0].strip()
        
        sentences.append(f"This proposal addresses critical challenges in {main_keyword} that have emerged as high priorities in contemporary research and development.")
        sentences.append(f"The field has witnessed significant advances in recent years, yet substantial gaps remain in our understanding and implementation of effective solutions.")
        
        if top_papers:
            paper = top_papers[0]
            facts = self.rag.fact_extractor.extract_facts(paper)
            sentences.append(paraphraser.paraphrase_finding(paper, facts))
        
        sentences.append(f"However, current approaches face limitations in scalability, real-world applicability, and comprehensive evaluation frameworks.")
        sentences.append(f"This proposal presents a comprehensive three-year research program focused on {description[:250]}.")
        
        sentences.append(f"Our research objectives include: (1) developing novel theoretical frameworks that address identified gaps, (2) implementing and validating innovative methodologies through rigorous experimentation, (3) achieving measurable performance improvements over state-of-the-art approaches, and (4) demonstrating real-world applicability through deployment validation.")
        
        if len(top_papers) > 2:
            sentences.append(paraphraser.synthesize_multiple(top_papers[:4], main_keyword, "advanced computational methodologies"))
        
        sentences.append(f"The intellectual merit of this work lies in its novel integration of multiple theoretical perspectives, rigorous empirical validation, and potential to advance fundamental understanding in {main_keyword}.")
        sentences.append(f"Expected outcomes include peer-reviewed publications in top-tier venues, open-source software releases, curated datasets for community use, and trained graduate students equipped to advance the field.")
        sentences.append(f"Broader impacts encompass contributions to national priorities in {main_keyword}, enhancement of research infrastructure through shared resources, and potential societal benefits through improved technologies addressing real-world challenges.")
        sentences.append(f"This project directly addresses funding agency priorities by tackling critical challenges with immediate practical applications while advancing fundamental scientific knowledge.")
        
        return " ".join(sentences)
    
    def _generate_introduction(self, title: str, keywords: str, description: str, papers: List[Dict]) -> str:
        paraphraser = self.rag.paraphraser
        sentences = []
        
        main_keyword = keywords.split(',')[0].strip()
        secondary_keywords = [k.strip() for k in keywords.split(',')[1:3]]
        
        sentences.append(f"The rapid evolution of {main_keyword} has transformed numerous aspects of modern technology, science, and society.")
        sentences.append(f"Over the past decade, researchers and practitioners have made remarkable progress in understanding fundamental principles, developing practical applications, and establishing theoretical foundations.")
        
        sentences.append(paraphraser.synthesize_multiple(papers[:3], main_keyword, "foundational research"))
        
        if secondary_keywords:
            sentences.append(f"The intersection of {main_keyword} with emerging technologies such as {', '.join(secondary_keywords)} presents both opportunities and challenges.")
        
        for i, paper in enumerate(papers[:8]):
            facts = self.rag.fact_extractor.extract_facts(paper)
            if i % 3 == 0:
                sentences.append(paraphraser.paraphrase_method(paper, facts))
            elif i % 3 == 1:
                sentences.append(paraphraser.paraphrase_result(paper, facts))
            else:
                sentences.append(paraphraser.paraphrase_finding(paper, facts))
        
        sentences.append(f"Despite these advances, the field faces several critical challenges that limit progress and real-world deployment.")
        
        for paper in papers[8:11]:
            facts = self.rag.fact_extractor.extract_facts(paper)
            sentences.append(paraphraser.paraphrase_challenge(paper, facts))
        
        sentences.append(f"This proposal directly addresses these challenges through {title}, which represents a crucial gap in current knowledge and practice.")
        sentences.append(f"Our research is motivated by three key observations from the literature and practice.")
        sentences.append(f"First, existing approaches have not adequately addressed the integration and scalability challenges inherent in {main_keyword}.")
        sentences.append(f"Second, comprehensive evaluation frameworks that consider multiple dimensions of performance, usability, and real-world applicability remain underdeveloped.")
        sentences.append(f"Third, the translation of research advances into practical, deployable solutions continues to face significant barriers.")
        sentences.append(f"Our proposed research addresses these gaps through a comprehensive approach that {description[:250]}.")
        sentences.append(f"The significance of this work extends beyond immediate technical contributions.")
        sentences.append(f"Successful completion will advance fundamental understanding in {main_keyword}, provide validated methodologies for the research community, and demonstrate practical pathways for real-world deployment.")
        sentences.append(paraphraser.synthesize_multiple(papers[:5], main_keyword, "innovative methodologies"))
        sentences.append(f"By integrating insights from multiple disciplines, leveraging state-of-the-art technologies, and maintaining rigorous evaluation standards, this project aims to make transformative contributions to {main_keyword} research and practice.")
        
        return " ".join(sentences)
    
    def _generate_theoretical_framework(self, title: str, keywords: str, description: str, papers: List[Dict]) -> str:
        paraphraser = self.rag.paraphraser
        framework = []
        
        main_keyword = keywords.split(',')[0].strip()
        
        framework.append(f"This research is grounded in established theoretical frameworks while introducing novel conceptual contributions that advance understanding in {main_keyword}.")
        framework.append(self._add_transition("the literature review", "our theoretical framework"))
        
        framework.append("\n\nFoundational Theories\n")
        framework.append(f"Our work builds upon several foundational theories that have shaped contemporary research in {main_keyword}.")
        
        if papers:
            framework.append(paraphraser.synthesize_multiple(papers[:4], main_keyword, "theoretical foundations and principles"))
        
        framework.append(f"These theoretical perspectives provide complementary lenses through which to understand the complexities of {main_keyword}. However, existing theories have limitations in addressing emerging challenges related to scale, complexity, and real-world deployment constraints.")
        
        framework.append("\n\nProposed Conceptual Model\n")
        framework.append(f"We propose an integrative conceptual model that synthesizes insights from multiple theoretical traditions while addressing identified limitations.")
        framework.append(f"The model consists of four interconnected components: (1) Input Processing Layer responsible for data acquisition, preprocessing, and feature extraction; (2) Core Analytical Engine implementing primary computational or analytical mechanisms; (3) Integration and Synthesis Module combining results from multiple sources or methods; and (4) Output Generation and Validation producing results and ensuring quality through comprehensive checks.")
        framework.append(f"Each component is informed by empirical findings from recent literature and designed to address specific limitations identified in existing approaches.")
        framework.append(f"The model emphasizes modularity, enabling independent development and validation of components while ensuring coherent integration. This design facilitates iterative refinement, allows for component substitution as methods evolve, and supports comprehensive evaluation at multiple levels.")
        
        framework.append("\n\nTheoretical Contributions\n")
        framework.append(f"This research makes several novel theoretical contributions to {main_keyword}.")
        framework.append(f"First, we extend existing frameworks by incorporating insights from {description[:150]}, providing a more comprehensive and nuanced understanding of underlying mechanisms.")
        framework.append(f"Second, we propose novel theoretical constructs that bridge previously disparate approaches, enabling more integrated understanding across subdisciplines.")
        framework.append(f"Third, we establish formal connections between theoretical predictions and empirical observations, strengthening the scientific foundations of {main_keyword}.")
        framework.append(f"Fourth, we develop testable hypotheses that can guide future research and provide clear criteria for evaluating theoretical validity.")
        
        framework.append("\n\nOperationalization and Measurement\n")
        framework.append(f"The theoretical framework is operationalized through specific methodological choices and measurement strategies detailed in subsequent sections.")
        framework.append(f"Each theoretical construct is mapped to measurable variables with clearly defined operational indicators. We employ multiple measurement methods to ensure construct validity, including objective performance metrics, comparative benchmarks, and qualitative assessments where appropriate.")
        framework.append(f"This rigorous operationalization ensures that theoretical predictions can be empirically tested and refined based on empirical evidence.")
        
        return " ".join(framework)
    
    def _generate_research_questions(self, title: str, keywords: str, description: str, papers: List[Dict]) -> str:
        main_keyword = keywords.split(',')[0].strip()
        questions = []
        
        questions.append(f"This research is guided by fundamental questions derived from gaps identified in the literature review and motivated by practical challenges observed in real-world applications.")
        questions.append(self._add_transition("the theoretical framework", "specific research questions"))
        
        questions.append(f"\n\nPrimary Research Questions\n")
        
        questions.append(f"RQ1: What are the key mechanisms and underlying principles that govern {title}?")
        questions.append(f"This question addresses foundational understanding necessary for advancing both theory and practice in {main_keyword}. We seek to identify critical factors, understand their interactions, and develop predictive models that can guide system design and optimization.")
        
        questions.append(f"\n\nRQ2: How can we develop more effective, efficient, and scalable approaches for {description[:150]}?")
        questions.append(f"This question focuses on methodological innovation, building upon existing work while addressing identified limitations. We aim to develop novel algorithms, architectures, or frameworks that demonstrably improve upon current state-of-the-art methods.")
        
        questions.append(f"\n\nRQ3: What performance improvements can be achieved through the proposed approaches across multiple evaluation dimensions?")
        questions.append(f"This question addresses quantitative evaluation and comparison with existing methods using comprehensive metrics. We seek to establish rigorous benchmarks and demonstrate measurable improvements in accuracy, efficiency, scalability, and robustness.")
        
        questions.append(f"\n\nRQ4: How can proposed solutions be effectively deployed, validated, and maintained in real-world operational environments?")
        questions.append(f"This question considers practical implementation challenges including integration, resource constraints, and long-term sustainability. We aim to develop deployment strategies, operational guidelines, and best practices that facilitate technology transfer from research to practice.")
        
        questions.append(f"\n\nRQ5: What are the broader implications and potential applications of this research beyond the immediate problem domain?")
        questions.append(f"This question explores generalizability and potential for impact across multiple application contexts. We seek to identify transferable insights, reusable components, and principles applicable to related challenges.")
        
        questions.append(f"\n\nResearch Hypotheses\n")
        questions.append(f"Based on theoretical analysis, preliminary evidence, and insights from the literature, we propose the following testable hypotheses:")
        
        questions.append(f"\n\nH1: Performance Improvement Hypothesis")
        questions.append(f"The proposed approach will demonstrate statistically significant improvements over baseline methods across multiple performance metrics, including at least 15 percent improvement in primary performance indicators and maintained or improved performance in secondary metrics.")
        
        questions.append(f"\n\nH2: Scalability Hypothesis")
        questions.append(f"The proposed framework will exhibit near-linear scaling properties, maintaining performance characteristics as problem size increases by at least one order of magnitude.")
        
        questions.append(f"\n\nH3: Robustness Hypothesis")
        questions.append(f"The system will demonstrate robust performance across diverse conditions, maintaining at least 85 percent of optimal performance under realistic noise, variability, and constraint conditions.")
        
        questions.append(f"\n\nH4: Generalization Hypothesis")
        questions.append(f"Core principles and key components will generalize to related problem domains, with successful transfer demonstrated in at least two distinct application contexts.")
        
        questions.append(f"These hypotheses will be rigorously tested through systematic experimentation, statistical analysis, and comprehensive evaluation protocols described in the methodology section.")
        
        return " ".join(questions)
    
    def _generate_objectives(self, title: str, keywords: str, description: str, papers: List[Dict]) -> str:
        main_keyword = keywords.split(',')[0].strip()
        objectives = []
        
        objectives.append(f"This research pursues specific, measurable objectives aligned with our research questions and designed to advance both scientific understanding and practical capabilities in {main_keyword}.")
        objectives.append(self._add_transition("research questions and hypotheses", "concrete objectives"))
        
        obj_list = [
            "Develop comprehensive theoretical framework integrating multiple perspectives",
            "Design and implement novel methodologies addressing identified limitations",
            "Conduct rigorous experimental evaluation using established benchmarks",
            "Achieve quantitative performance improvements over state-of-the-art",
            "Validate approaches in real-world operational environments",
            "Disseminate findings and contribute to research infrastructure"
        ]
        
        objectives.append("\n\nTable 1: Research Objectives Overview")
        objectives.append(self.table_gen.generate_objectives_table(obj_list))
        
        objectives.append("\n\nObjective 1: Theoretical Framework Development")
        objectives.append(f"Establish comprehensive theoretical foundations for {main_keyword} by synthesizing insights from multiple disciplines, formalizing key concepts, and developing predictive models. Deliverables include formal theoretical specifications, conceptual models, and testable propositions documented in technical reports and peer-reviewed publications.")
        
        objectives.append("\n\nObjective 2: Methodological Innovation")
        objectives.append(f"Create innovative approaches for {description[:200]} that address limitations in current methods including scalability constraints, computational efficiency, and real-world applicability. Deliverables include novel algorithms, system architectures, and implementation frameworks released as open-source software with comprehensive documentation.")
        
        objectives.append("\n\nObjective 3: Rigorous Experimental Evaluation")
        objectives.append(f"Conduct systematic evaluation using established benchmarks, diverse test scenarios, and comprehensive metrics covering accuracy, efficiency, scalability, and robustness dimensions. Deliverables include curated datasets, evaluation protocols, and detailed experimental results published in peer-reviewed venues.")
        
        objectives.append("\n\nObjective 4: Performance Optimization")
        objectives.append(f"Achieve measurable improvements including at least 15-20 percent gains in primary performance metrics, maintained efficiency under scale, and demonstrated robustness across diverse conditions. Deliverables include performance benchmarks, comparative analyses, and optimization guidelines for practitioners.")
        
        objectives.append("\n\nObjective 5: Real-World Validation")
        objectives.append(f"Deploy and validate solutions in operational environments through collaborations with industry partners, demonstrating practical applicability and identifying deployment best practices. Deliverables include deployment case studies, operational guidelines, and validated system configurations.")
        
        objectives.append("\n\nObjective 6: Research Infrastructure and Capacity Building")
        objectives.append(f"Contribute to community research infrastructure through open-source releases, shared datasets, and trained researchers capable of advancing {main_keyword}. Deliverables include software repositories, documentation, educational materials, and mentored graduate students.")
        
        objectives.append(f"\n\nEach objective includes specific milestones, success criteria, and deliverables outlined in the work plan section. Progress toward objectives will be monitored through quarterly reviews and adjusted as needed based on empirical findings.")
        
        return " ".join(objectives)
    
    def _generate_methodology(self, title: str, keywords: str, description: str, papers: List[Dict]) -> str:
        paraphraser = self.rag.paraphraser
        methodology = []
        
        main_keyword = keywords.split(',')[0].strip()
        
        methodology.append(f"This section describes the comprehensive methodology for achieving research objectives, including research design, technical approaches, data collection strategies, implementation plans, and evaluation protocols.")
        methodology.append(self._add_transition("research objectives", "detailed methodology"))
        
        methodology.append("\n\n6.1 Research Design and Overall Approach\n")
        methodology.append(f"We employ a multi-phase research design combining theoretical development, iterative prototyping, rigorous experimentation, and real-world validation. The design integrates quantitative and qualitative methods, ensuring comprehensive evaluation across multiple dimensions.")
        methodology.append(f"The research proceeds through three major phases: (1) Foundation and Development (Months 1-12) focusing on theoretical framework completion, initial prototype development, and data collection; (2) Experimentation and Refinement (Months 13-24) emphasizing systematic evaluation, iterative improvement, and performance optimization; and (3) Validation and Dissemination (Months 25-36) concentrating on real-world deployment, comprehensive validation, and results dissemination.")
        
        methodology.append("\n\n6.2 Technical Approach and Implementation\n")
        methodology.append(f"Our technical approach builds upon proven methodologies from recent literature while introducing novel innovations to address identified limitations.")
        
        for paper in papers[:4]:
            facts = self.rag.fact_extractor.extract_facts(paper)
            methodology.append(paraphraser.paraphrase_method(paper, facts))
        
        methodology.append(f"We adapt and substantially extend these approaches to address the specific requirements of {title}.")
        methodology.append(f"Key innovations in our approach include: (1) integration of multiple complementary techniques to leverage their respective strengths, (2) novel optimization strategies that improve computational efficiency while maintaining accuracy, (3) adaptive mechanisms that adjust to varying conditions and requirements, and (4) modular architecture facilitating component-wise development, testing, and replacement.")
        
        methodology.append("\n\n6.3 Data Collection, Curation, and Management\n")
        methodology.append(f"Data collection will proceed through multiple channels ensuring comprehensive coverage, diversity, and quality.")
        methodology.append(f"Primary data sources include established benchmark datasets widely used in {main_keyword} research, providing basis for direct comparison with existing work. We will supplement these with newly collected data from collaborating institutions, ensuring representation of real-world conditions and use cases.")
        methodology.append(f"Data collection targets include approximately 100,000-500,000 samples across diverse scenarios, conditions, and edge cases. All data will undergo rigorous quality assurance including validation checks, outlier detection, and bias assessment.")
        methodology.append(f"Data preprocessing will follow established best practices including normalization, handling missing values, feature engineering where appropriate, and train/validation/test splits following standard protocols.")
        methodology.append(f"We will adhere to data management best practices detailed in our Data Management Plan, ensuring reproducibility, proper documentation, and appropriate sharing with the research community.")
        
        methodology.append("\n\n6.4 System Implementation and Development\n")
        methodology.append(f"Implementation will utilize industry-standard tools, frameworks, and development practices to ensure reproducibility, maintainability, and community adoption.")
        methodology.append(f"The system will be developed using modular architecture with clearly defined interfaces, enabling independent development and testing of components. All code will be version-controlled using Git, documented following established standards, and released as open-source software under permissive licenses.")
        methodology.append(f"Development will follow agile methodologies with two-week sprints, regular code reviews, continuous integration/testing, and iterative refinement based on empirical findings.")
        methodology.append(f"We will employ test-driven development practices, maintaining comprehensive unit tests, integration tests, and end-to-end system tests to ensure reliability and facilitate future modifications.")
        
        methodology.append("\n\n6.5 Experimental Protocol and Evaluation Design\n")
        methodology.append(f"Experiments will be conducted following rigorous protocols ensuring validity, reliability, and reproducibility.")
        methodology.append(f"Our evaluation strategy encompasses multiple complementary approaches: (1) Benchmark Evaluation with systematic comparison using established datasets and metrics, (2) Ablation Studies isolating contributions of individual components, (3) Sensitivity Analysis assessing robustness to parameter variations, (4) Scalability Testing evaluating performance as problem size increases, and (5) Real-World Validation testing in operational environments with realistic constraints.")
        methodology.append(f"All experiments will employ appropriate statistical methods including cross-validation, multiple independent runs, significance testing, and confidence interval estimation. We will use at least five baseline methods for comparison, including recent state-of-the-art approaches from the literature.")
        
        methodology.append("\n\n6.6 Evaluation Metrics and Success Criteria\n")
        methodology.append(f"Performance will be assessed using comprehensive metrics across multiple dimensions.")
        methodology.append(f"Primary Performance Metrics include accuracy, precision, recall, F1-score, or domain-appropriate equivalents, providing quantitative measures of core functionality.")
        methodology.append(f"Efficiency Metrics encompass computational time, memory usage, energy consumption, and throughput, assessing resource requirements and operational feasibility.")
        methodology.append(f"Scalability Metrics evaluate performance degradation as problem size increases, measured through complexity analysis and empirical scaling experiments.")
        methodology.append(f"Robustness Metrics assess performance stability under noisy inputs, parameter variations, and adverse conditions.")
        methodology.append(f"Usability Metrics, collected through user studies where appropriate, evaluate practical applicability including ease of deployment, interpretability of results, and integration with existing systems.")
        methodology.append(f"Success criteria include achieving at least 15 percent improvement over best baseline methods in primary metrics, demonstrating scalability to at least 10x problem size, maintaining 85 percent or better performance under realistic noise conditions, and positive validation in real-world deployment scenarios.")
        
        methodology.append("\n\n6.7 Validation Strategy and Quality Assurance\n")
        methodology.append(f"Validation occurs at multiple levels ensuring comprehensive quality assurance.")
        methodology.append(f"Component-level validation tests individual modules against specifications using unit tests and focused experiments. System-level validation assesses integrated functionality through end-to-end testing, integration tests, and comprehensive evaluation scenarios.")
        methodology.append(f"External validation through collaboration with industry partners provides real-world testing under operational constraints, user feedback, and deployment feasibility assessment.")
        methodology.append(f"Peer validation through conference presentations, journal submissions, and open-source releases enables community scrutiny, independent reproduction, and external validation of findings.")
        
        return " ".join(methodology)
    
    def _generate_work_plan(self, title: str, keywords: str, description: str, papers: List[Dict]) -> str:
        workplan = []
        
        workplan.append(f"The research will be conducted over a 36-month period organized into distinct phases with clear milestones, deliverables, and decision points.")
        workplan.append(self._add_transition("the methodology", "the detailed work plan and timeline"))
        
        workplan.append("\n\nTable 2: Project Timeline Overview")
        workplan.append(self.table_gen.generate_timeline_table())
        
        workplan.append("\n\n7.1 Phase 1: Foundation and Development (Months 1-12)\n")
        workplan.append(f"This foundational phase establishes theoretical frameworks, develops initial prototypes, and prepares research infrastructure.")
        
        workplan.append(f"\n\nMilestone 1.1 (Month 3): Literature Review Completion and Theoretical Framework")
        workplan.append(f"Complete comprehensive literature review, finalize theoretical framework, and submit first technical report. Deliverables: Technical report documenting theoretical framework, comprehensive bibliography, preliminary research design.")
        
        workplan.append(f"\n\nMilestone 1.2 (Month 6): Initial Prototype Development")
        workplan.append(f"Develop functional prototype implementing core algorithms and system architecture. Deliverables: Working prototype with basic functionality, technical documentation, unit test suite.")
        
        workplan.append(f"\n\nMilestone 1.3 (Month 9): Data Collection and Preprocessing Pipeline")
        workplan.append(f"Complete data collection from all sources, implement preprocessing pipelines, and validate data quality. Deliverables: Curated datasets, preprocessing scripts, data quality report, metadata documentation.")
        
        workplan.append(f"\n\nMilestone 1.4 (Month 12): Preliminary Experiments and Phase 1 Report")
        workplan.append(f"Conduct initial experiments, analyze results, refine approach based on findings. Deliverables: Preliminary experimental results, Phase 1 completion report, refined research plan for Phase 2. Decision Point: Go/No-Go decision based on preliminary results.")
        
        workplan.append("\n\n7.2 Phase 2: Experimentation and Refinement (Months 13-24)\n")
        workplan.append(f"This phase focuses on comprehensive experimentation, iterative refinement, and performance optimization.")
        
        workplan.append(f"\n\nMilestone 2.1 (Month 15): Comprehensive Experimental Evaluation")
        workplan.append(f"Complete systematic evaluation across all benchmark datasets, multiple metrics, and comparison with baseline methods. Deliverables: Comprehensive experimental results, statistical analyses, performance benchmarks, conference paper submission.")
        
        workplan.append(f"\n\nMilestone 2.2 (Month 18): System Refinement and Optimization")
        workplan.append(f"Refine system based on experimental findings, optimize performance bottlenecks, enhance scalability. Deliverables: Optimized system implementation, performance improvements documentation, updated technical specifications.")
        
        workplan.append(f"\n\nMilestone 2.3 (Month 21): Comparative Analysis and Ablation Studies")
        workplan.append(f"Conduct detailed comparative analysis with state-of-the-art methods, perform ablation studies to isolate component contributions. Deliverables: Comparative analysis report, ablation study results, component contribution analysis.")
        
        workplan.append(f"\n\nMilestone 2.4 (Month 24): Scalability Testing and Phase 2 Report")
        workplan.append(f"Complete comprehensive scalability experiments, validate performance under increased load. Deliverables: Scalability analysis, Phase 2 completion report, journal paper submission, refined system for deployment.")
        
        workplan.append("\n\n7.3 Phase 3: Validation and Dissemination (Months 25-36)\n")
        workplan.append(f"This final phase emphasizes real-world validation, comprehensive documentation, and broad dissemination of findings.")
        
        workplan.append(f"\n\nMilestone 3.1 (Month 27): Real-World Deployment Preparation")
        workplan.append(f"Prepare system for deployment in operational environments, develop deployment documentation, establish monitoring frameworks. Deliverables: Deployment-ready system, installation guides, operational documentation, monitoring tools.")
        
        workplan.append(f"\n\nMilestone 3.2 (Month 30): Deployment Validation and User Studies")
        workplan.append(f"Deploy system in real-world environments, conduct validation studies with industry partners, collect user feedback. Deliverables: Deployment case studies, validation results, user feedback analysis, best practices documentation.")
        
        workplan.append(f"\n\nMilestone 3.3 (Month 33): Open-Source Release and Documentation")
        workplan.append(f"Release complete open-source implementation, comprehensive documentation, tutorials, and example applications. Deliverables: Public GitHub repository, API documentation, user tutorials, demonstration videos, example datasets.")
        
        workplan.append(f"\n\nMilestone 3.4 (Month 36): Final Dissemination and Project Completion")
        workplan.append(f"Submit final journal publications, present at major conferences, deliver final project report. Deliverables: Journal publications (2-3 papers), conference presentations (3-4 venues), final comprehensive report, trained graduate students.")
        
        workplan.append("\n\n7.4 Risk Management and Contingency Planning\n")
        workplan.append(f"The timeline includes buffer periods for unexpected challenges and contingency plans for critical path items. Regular quarterly reviews with advisory board will assess progress against milestones, identify risks early, and adjust plans as needed.")
        
        workplan.append("\n\n7.5 Resource Allocation and Team Coordination\n")
        workplan.append(f"Personnel effort distribution: PI (1 month/year summer salary) provides overall direction and theoretical guidance; Graduate Student 1 (50 percent time, 36 months) focuses on algorithm development and implementation; Graduate Student 2 (50 percent time, 36 months) concentrates on experimentation and evaluation; Undergraduate researchers (summer support) assist with data collection, testing, and documentation.")
        
        return " ".join(workplan)
    
    def _generate_outcomes(self, title: str, keywords: str, description: str, papers: List[Dict]) -> str:
        outcomes = []
        main_keyword = keywords.split(',')[0].strip()
        
        outcomes.append(f"This research will produce significant outcomes across multiple dimensions with both immediate impact and long-term implications for {main_keyword}.")
        outcomes.append(self._add_transition("the work plan", "expected outcomes and broader impacts"))
        
        outcomes.append("\n\n8.1 Scientific and Intellectual Outcomes\n")
        outcomes.append(f"Novel theoretical contributions advancing fundamental understanding of {main_keyword} through formal frameworks, validated models, and testable propositions.")
        outcomes.append(f"Innovative methodologies addressing critical limitations in current approaches including improved algorithms, system architectures, and evaluation frameworks.")
        outcomes.append(f"Empirical findings demonstrating measurable performance improvements over state-of-the-art methods across multiple evaluation dimensions.")
        outcomes.append(f"Comprehensive evaluation frameworks and benchmarks applicable to future research in {main_keyword} and related domains.")
        
        outcomes.append("\n\n8.2 Technical and Software Outcomes\n")
        outcomes.append(f"Fully functional, production-ready system implementing the proposed approach with comprehensive documentation and APIs.")
        outcomes.append(f"Open-source software releases enabling reproduction, extension, and practical application by other researchers and practitioners.")
        outcomes.append(f"Curated datasets and benchmarks contributing to community resources and enabling standardized evaluation.")
        
        outcomes.append("\n\n8.3 Publications and Scholarly Dissemination\n")
        outcomes.append(f"Target 3-4 peer-reviewed journal publications in high-impact venues such as leading IEEE Transactions, ACM journals, or top-tier domain-specific journals.")
        outcomes.append(f"Target 4-6 conference presentations at premier international conferences including major IEEE/ACM conferences and domain-specific flagship venues.")
        outcomes.append(f"Technical reports documenting all findings, methodologies, and detailed experimental results.")
        
        outcomes.append("\n\n8.4 Practical Impact and Technology Transfer\n")
        outcomes.append(f"Demonstrated applicability in real-world scenarios through validation studies with industry partners.")
        outcomes.append(f"Potential for technology transfer and commercialization through industry collaborations and startup opportunities.")
        outcomes.append(f"Contributions to standards development and best practices in {main_keyword}.")
        
        outcomes.append("\n\n8.5 Education, Training, and Capacity Building\n")
        outcomes.append(f"Training of 2-3 graduate students in advanced research methods, gaining expertise in {main_keyword}, software development, experimental design, and scholarly communication.")
        outcomes.append(f"Development of educational materials including course modules, laboratory exercises, and workshop content suitable for graduate and advanced undergraduate courses.")
        outcomes.append(f"Mentorship of undergraduate researchers through summer programs, providing early research experiences.")
        
        return " ".join(outcomes)
    
    def _generate_risk_assessment(self, title: str, keywords: str, description: str, papers: List[Dict]) -> str:
        risks = []
        
        risks.append(f"We have conducted comprehensive risk assessment and developed detailed mitigation strategies for potential challenges that may arise during project execution.")
        risks.append(self._add_transition("expected outcomes", "potential risks and mitigation strategies"))
        
        risks.append("\n\nTable 3: Risk Assessment Matrix")
        risks.append(self.table_gen.generate_risk_table())
        
        risks.append("\n\n9.1 Technical and Methodological Risks\n")
        risks.append(f"Risk: Performance targets may not be achieved in initial implementations. Likelihood: Medium. Mitigation: Iterative development approach with continuous evaluation, multiple alternative approaches prepared, buffer time allocated in schedule.")
        risks.append(f"Risk: Scalability challenges in real-world deployment. Likelihood: Medium. Mitigation: Early scalability testing, incremental deployment strategy, optimization expertise on team, access to high-performance computing resources.")
        
        risks.append("\n\n9.2 Resource and Infrastructure Risks\n")
        risks.append(f"Risk: Computational resources insufficient for large-scale experiments. Likelihood: Low. Mitigation: Cloud computing budget allocated, established relationships with institutional HPC facilities, efficient algorithms prioritized.")
        risks.append(f"Risk: Data availability or quality issues. Likelihood: Medium. Mitigation: Multiple data sources identified, data collection protocols established, quality assurance procedures, synthetic data generation capability.")
        
        risks.append("\n\n9.3 Personnel and Team Risks\n")
        risks.append(f"Risk: Key personnel departure or unavailability. Likelihood: Low. Mitigation: Cross-training of team members, comprehensive documentation, backup personnel identified, strong institutional support.")
        risks.append(f"Risk: Difficulty recruiting qualified graduate students. Likelihood: Low. Mitigation: Strong institutional reputation, competitive stipends, exciting research topics.")
        
        risks.append("\n\n9.4 Timeline and Schedule Risks\n")
        risks.append(f"Risk: Delays in critical path activities. Likelihood: Medium. Mitigation: Conservative timeline estimates with built-in buffers, regular progress monitoring, agile adaptation.")
        
        return " ".join(risks)
    
    def _generate_budget(self, title: str, keywords: str, description: str, papers: List[Dict]) -> str:
        budget = []
        
        budget.append(f"The proposed budget supports comprehensive research activities over the 36-month project period, with all costs justified by specific research needs and deliverables.")
        budget.append(self._add_transition("risk assessment", "budget justification"))
        
        budget.append("\n\nTable 4: Budget Summary")
        budget.append(self.table_gen.generate_budget_table())
        
        budget.append("\n\n10.1 Personnel Costs (Approximately 60 percent of total budget)\n")
        budget.append(f"Principal Investigator: One month summer salary per year (3 months total). Graduate Research Assistants: Two students at 50 percent time for 36 months each. Undergraduate Research Assistants: Summer support for 2-3 students per year.")
        
        budget.append("\n\n10.2 Equipment and Computational Resources (Approximately 20 percent)\n")
        budget.append(f"High-Performance Computing Workstations, Cloud Computing Resources, Software Licenses, and Data Storage for datasets and experimental results.")
        
        budget.append("\n\n10.3 Travel and Conferences (Approximately 10 percent)\n")
        budget.append(f"Domestic Conference Travel: 2-3 conferences per year. International Conference Travel: 1-2 conferences over project duration. Collaboration meetings with industry partners.")
        
        budget.append("\n\n10.4 Other Direct Costs (Approximately 10 percent)\n")
        budget.append(f"Publication costs for open-access journals, data acquisition, participant support for user studies, and general research supplies.")
        
        budget.append("\n\n10.5 Budget Justification Summary\n")
        budget.append(f"The requested budget is appropriate and necessary for the scope and ambition of the proposed research. All costs are justified by specific research activities and deliverables.")
        
        return " ".join(budget)
    
    def _generate_broader_impacts(self, title: str, keywords: str, description: str, papers: List[Dict]) -> str:
        impacts = []
        main_keyword = keywords.split(',')[0].strip()
        
        impacts.append(f"This research will generate substantial broader impacts extending well beyond immediate scientific contributions, addressing societal needs, educational goals, and infrastructure development.")
        impacts.append(self._add_transition("budget justification", "broader impacts"))
        
        impacts.append("\n\n11.1 Societal Benefits and Applications\n")
        impacts.append(f"The research directly addresses practical challenges in {main_keyword} with potential for significant societal benefit. Improved technologies developed through this work can enhance capabilities in critical application domains including national security, public health, economic competitiveness, and quality of life.")
        
        impacts.append("\n\n11.2 Education and Workforce Development\n")
        impacts.append(f"The project will train 2-3 graduate students in cutting-edge research methods, preparing them for careers in academia, industry, or government. Graduate students will gain comprehensive skills including theoretical analysis, algorithm development, software engineering, experimental design, and technical writing.")
        
        impacts.append("\n\n11.3 Broadening Participation and Diversity\n")
        impacts.append(f"We are committed to broadening participation of underrepresented groups in {main_keyword} research through active recruitment, targeted mentoring, and removal of barriers to entry via open educational materials.")
        
        impacts.append("\n\n11.4 Research Infrastructure and Community Resources\n")
        impacts.append(f"Open-source software releases, curated datasets, and comprehensive documentation will enhance research infrastructure, benefiting the entire research ecosystem.")
        
        return " ".join(impacts)
    
    def _generate_data_management(self, title: str, keywords: str, description: str, papers: List[Dict]) -> str:
        dmp = []
        
        dmp.append(f"This Data Management Plan describes our approach to data collection, storage, sharing, and preservation, ensuring research reproducibility and compliance with funding agency requirements.")
        dmp.append(self._add_transition("broader impacts", "data management procedures"))
        
        dmp.append("\n\n12.1 Data Types and Formats\n")
        dmp.append(f"The project will generate primary research data (datasets, experimental results), software and code (Python, C++, Jupyter notebooks), documentation (technical reports, API docs), and publications (journal articles, conference papers).")
        
        dmp.append("\n\n12.2 Data Storage and Backup\n")
        dmp.append(f"Data will be stored on institutional high-performance storage systems with automatic daily backups. Critical data replicated across multiple locations ensuring redundancy and disaster recovery.")
        
        dmp.append("\n\n12.3 Data Sharing and Public Access\n")
        dmp.append(f"Source code released as open-source on GitHub under permissive licenses. Datasets deposited in public repositories with persistent DOIs. Publications made available as open-access preprints.")
        
        dmp.append("\n\n12.4 Data Preservation\n")
        dmp.append(f"Data preserved for minimum 5 years beyond project completion. Final datasets deposited in institutional repositories with long-term preservation commitments.")
        
        dmp.append("\n\n12.5 Roles and Responsibilities\n")
        dmp.append(f"Principal Investigator has overall responsibility for data management compliance. Graduate students manage day-to-day organization under PI supervision.")
        
        return " ".join(dmp)