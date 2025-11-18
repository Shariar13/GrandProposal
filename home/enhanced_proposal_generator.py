"""
Enhanced Proposal Generator using OpenAI with RAG data
Generates complete, well-cited proposals from comprehensive research data
"""
import os
import json
from typing import Dict, List, Any, Generator
from openai import OpenAI
from authentication.models import ProposalType, ProposalTemplate, SavedProposal
import time


class EnhancedProposalGenerator:
    """
    Generates complete grant proposals using OpenAI API with comprehensive RAG data.
    The RAG system provides all research data and citations, then OpenAI generates
    the proposal with perfect citation integration.
    """

    def __init__(self, api_key: str = None):
        """Initialize the proposal generator with OpenAI API"""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not provided")

        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4-turbo-preview"  # or "gpt-4o" for latest
        self.max_tokens = 4096

    def generate_complete_proposal(
        self,
        proposal_type: ProposalType,
        title: str,
        keywords: str,
        description: str,
        rag_data: Dict[str, Any],
        user_requirements: Dict[str, Any] = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Generate a complete proposal section by section using RAG data
        Yields progress updates as sections are generated
        """
        # Get templates for this proposal type
        templates = proposal_type.templates.all().order_by('section_order')

        if not templates.exists():
            yield {
                'type': 'error',
                'message': f'No templates found for {proposal_type.name}'
            }
            return

        yield {
            'type': 'info',
            'message': f'Starting generation of {proposal_type.name} proposal',
            'total_sections': templates.count()
        }

        # Prepare context from RAG data
        research_context = self._prepare_research_context(rag_data)

        # Generate proposal metadata
        proposal_metadata = {
            'title': title,
            'keywords': keywords,
            'description': description,
            'proposal_type': proposal_type.name,
            'total_papers': rag_data.get('total_papers', 0),
            'generated_sections': []
        }

        # Generate each section
        for idx, template in enumerate(templates, 1):
            yield {
                'type': 'section_start',
                'section_name': template.section_name,
                'section_number': idx,
                'total_sections': templates.count()
            }

            try:
                # Generate section content
                section_content = self._generate_section(
                    template=template,
                    title=title,
                    description=description,
                    research_context=research_context,
                    rag_data=rag_data,
                    user_requirements=user_requirements
                )

                proposal_metadata['generated_sections'].append({
                    'name': template.section_name,
                    'content': section_content,
                    'word_count': len(section_content.split())
                })

                yield {
                    'type': 'section_complete',
                    'section_name': template.section_name,
                    'content': section_content,
                    'word_count': len(section_content.split())
                }

            except Exception as e:
                yield {
                    'type': 'section_error',
                    'section_name': template.section_name,
                    'error': str(e)
                }

        # Compile full proposal
        full_proposal = self._compile_proposal(proposal_metadata)

        yield {
            'type': 'complete',
            'full_proposal': full_proposal,
            'metadata': proposal_metadata,
            'bibliography': rag_data.get('bibliography', {}),
            'total_words': sum(s['word_count'] for s in proposal_metadata['generated_sections'])
        }

    def _prepare_research_context(self, rag_data: Dict[str, Any]) -> str:
        """Prepare comprehensive research context from RAG data"""
        context_parts = []

        # Overview
        context_parts.append(f"# Research Context")
        context_parts.append(f"Total Papers Analyzed: {rag_data.get('total_papers', 0)}")
        context_parts.append("")

        # Key themes
        if rag_data.get('themes'):
            context_parts.append("## Major Research Themes:")
            for theme, papers in list(rag_data['themes'].items())[:10]:
                context_parts.append(f"- {theme}: {len(papers)} papers")
            context_parts.append("")

        # Methodologies
        if rag_data.get('methodologies'):
            context_parts.append("## Common Methodologies:")
            for method in rag_data['methodologies'][:15]:
                context_parts.append(f"- {method}")
            context_parts.append("")

        # Datasets
        if rag_data.get('datasets'):
            context_parts.append("## Frequently Used Datasets:")
            for dataset in rag_data['datasets'][:10]:
                context_parts.append(f"- {dataset}")
            context_parts.append("")

        # Research timeline
        if rag_data.get('timeline'):
            context_parts.append("## Publication Timeline:")
            for year, count in list(rag_data['timeline'].items())[-10:]:
                context_parts.append(f"- {year}: {count} papers")
            context_parts.append("")

        # Key researchers
        if rag_data.get('key_researchers'):
            context_parts.append("## Key Researchers:")
            for researcher in rag_data['key_researchers'][:10]:
                context_parts.append(
                    f"- {researcher['name']}: {researcher['paper_count']} papers, "
                    f"{researcher['total_citations']} citations"
                )
            context_parts.append("")

        # Research gaps
        if rag_data.get('research_gaps'):
            context_parts.append("## Identified Research Gaps:")
            for gap in rag_data['research_gaps'][:5]:
                context_parts.append(f"- {gap}")
            context_parts.append("")

        return "\n".join(context_parts)

    def _generate_section(
        self,
        template: ProposalTemplate,
        title: str,
        description: str,
        research_context: str,
        rag_data: Dict[str, Any],
        user_requirements: Dict[str, Any] = None
    ) -> str:
        """Generate a single section using OpenAI with RAG data"""

        # Select most relevant papers for this section
        relevant_papers = self._select_relevant_papers(
            section_name=template.section_name,
            papers=rag_data.get('papers', []),
            max_papers=30
        )

        # Build comprehensive prompt
        system_prompt = self._build_system_prompt(template, rag_data)
        user_prompt = self._build_user_prompt(
            template=template,
            title=title,
            description=description,
            research_context=research_context,
            relevant_papers=relevant_papers,
            user_requirements=user_requirements
        )

        # Generate content with OpenAI
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=self.max_tokens,
                top_p=0.9,
                frequency_penalty=0.3,
                presence_penalty=0.3
            )

            content = response.choices[0].message.content
            return content

        except Exception as e:
            raise Exception(f"Error generating section {template.section_name}: {str(e)}")

    def _build_system_prompt(self, template: ProposalTemplate, rag_data: Dict) -> str:
        """Build system prompt for OpenAI"""
        return f"""You are an expert grant proposal writer specializing in {template.proposal_type.name} proposals.

Your task is to write the "{template.section_name}" section of a grant proposal.

CRITICAL CITATION REQUIREMENTS:
1. You MUST use ONLY the papers provided in the research data
2. NEVER fabricate or hallucinate citations
3. Every factual claim MUST be supported by a citation from the provided papers
4. Use in-text citations in APA format: (Author, Year) or Author (Year)
5. Use the exact citation keys provided in the paper data
6. When citing multiple sources, use: (Author1, Year1; Author2, Year2)

SECTION REQUIREMENTS:
- Word count: {template.min_words} - {template.max_words} words
- Required: {template.is_required}
- Description: {template.description}

WRITING STYLE:
- Academic and professional
- Clear and concise
- Evidence-based with proper citations
- Avoid jargon unless necessary
- Use active voice where appropriate
- Maintain logical flow

FORMATTING:
- Use markdown formatting
- Use headings and subheadings where appropriate
- Use bullet points and numbered lists for clarity
- Include tables if relevant

Remember: Quality over quantity. Every statement should add value to the proposal."""

    def _build_user_prompt(
        self,
        template: ProposalTemplate,
        title: str,
        description: str,
        research_context: str,
        relevant_papers: List[Dict],
        user_requirements: Dict = None
    ) -> str:
        """Build user prompt with all context"""

        prompt_parts = []

        # Proposal overview
        prompt_parts.append(f"# Proposal Overview")
        prompt_parts.append(f"**Title:** {title}")
        prompt_parts.append(f"**Description:** {description}")
        prompt_parts.append("")

        # Research context
        prompt_parts.append(research_context)
        prompt_parts.append("")

        # Relevant papers with full details
        prompt_parts.append("# Relevant Research Papers")
        prompt_parts.append("Use ONLY these papers for citations:")
        prompt_parts.append("")

        for i, paper in enumerate(relevant_papers, 1):
            prompt_parts.append(f"## Paper {i}: {paper['citation_key']}")
            prompt_parts.append(f"**Title:** {paper['title']}")
            prompt_parts.append(f"**Authors:** {', '.join(paper['authors'][:5])}")
            prompt_parts.append(f"**Year:** {paper['year']}")
            prompt_parts.append(f"**Abstract:** {paper['abstract'][:500]}...")
            prompt_parts.append(f"**Citation:** {paper['apa_citation']}")
            prompt_parts.append(f"**Citation Key:** `{paper['citation_key']}`")
            prompt_parts.append("")

        # Section-specific instructions
        prompt_parts.append(f"# Your Task")
        prompt_parts.append(f"Write the **{template.section_name}** section following this guidance:")
        prompt_parts.append(template.prompt_template)
        prompt_parts.append("")

        # Additional requirements
        if user_requirements:
            prompt_parts.append("# Additional Requirements:")
            for key, value in user_requirements.items():
                prompt_parts.append(f"- {key}: {value}")
            prompt_parts.append("")

        # Final instructions
        prompt_parts.append("# Final Instructions:")
        prompt_parts.append("1. Write ONLY the section content, do not include a title")
        prompt_parts.append("2. Cite papers using their citation keys")
        prompt_parts.append("3. Ensure all claims are supported by the provided papers")
        prompt_parts.append("4. Meet the word count requirements")
        prompt_parts.append("5. Use professional academic language")
        prompt_parts.append("")
        prompt_parts.append("Begin writing now:")

        return "\n".join(prompt_parts)

    def _select_relevant_papers(
        self,
        section_name: str,
        papers: List[Dict],
        max_papers: int = 30
    ) -> List[Dict]:
        """Select most relevant papers for a specific section"""

        # Section-specific paper selection logic
        section_keywords = {
            'Introduction': ['background', 'context', 'motivation', 'problem'],
            'Background': ['history', 'evolution', 'previous', 'existing'],
            'Literature Review': ['review', 'survey', 'comparative', 'analysis'],
            'Methodology': ['method', 'approach', 'technique', 'algorithm', 'framework'],
            'Innovation': ['novel', 'new', 'innovative', 'breakthrough', 'advanced'],
            'Impact': ['impact', 'benefit', 'application', 'deployment', 'real-world'],
            'Work Plan': ['plan', 'timeline', 'schedule', 'milestone', 'deliverable'],
        }

        # Get keywords for this section
        keywords = []
        for key in section_keywords:
            if key.lower() in section_name.lower():
                keywords.extend(section_keywords[key])

        if not keywords:
            # No specific keywords, return top papers by relevance
            return papers[:max_papers]

        # Score papers based on section relevance
        scored_papers = []
        for paper in papers:
            score = paper.get('relevance_score', 0)

            # Boost score if keywords appear in title or abstract
            text = (paper['title'] + ' ' + paper.get('abstract', '')).lower()
            keyword_matches = sum(1 for kw in keywords if kw in text)
            score += keyword_matches * 2

            scored_papers.append((score, paper))

        # Sort by score and return top papers
        scored_papers.sort(key=lambda x: x[0], reverse=True)
        return [paper for score, paper in scored_papers[:max_papers]]

    def _compile_proposal(self, metadata: Dict[str, Any]) -> str:
        """Compile all sections into complete proposal"""
        parts = []

        # Title page
        parts.append(f"# {metadata['title']}")
        parts.append("")
        parts.append(f"**Proposal Type:** {metadata['proposal_type']}")
        parts.append(f"**Keywords:** {metadata['keywords']}")
        parts.append("")
        parts.append("---")
        parts.append("")

        # Executive Summary / Abstract
        parts.append("## Executive Summary")
        parts.append("")
        parts.append(metadata['description'])
        parts.append("")
        parts.append("---")
        parts.append("")

        # All sections
        for section in metadata['generated_sections']:
            parts.append(f"## {section['name']}")
            parts.append("")
            parts.append(section['content'])
            parts.append("")
            parts.append("---")
            parts.append("")

        return "\n".join(parts)

    def generate_bibliography(self, rag_data: Dict[str, Any], format: str = 'apa') -> str:
        """Generate formatted bibliography from RAG data"""
        if format == 'apa':
            citations = rag_data.get('bibliography', {}).get('apa', [])
            return "\n\n".join(citations)
        elif format == 'bibtex':
            citations = rag_data.get('bibliography', {}).get('bibtex', [])
            return "\n\n".join(citations)
        else:
            return "Invalid format. Use 'apa' or 'bibtex'."

    def stream_generation(
        self,
        proposal_type: ProposalType,
        title: str,
        keywords: str,
        description: str,
        rag_data: Dict[str, Any],
        user_requirements: Dict[str, Any] = None
    ) -> Generator[str, None, None]:
        """
        Stream proposal generation with real-time updates
        Yields JSON strings for frontend consumption
        """
        for update in self.generate_complete_proposal(
            proposal_type=proposal_type,
            title=title,
            keywords=keywords,
            description=description,
            rag_data=rag_data,
            user_requirements=user_requirements
        ):
            yield f"data: {json.dumps(update)}\n\n"

    def enhance_existing_section(
        self,
        section_content: str,
        section_name: str,
        rag_data: Dict[str, Any],
        enhancement_instructions: str = None
    ) -> str:
        """Enhance an existing section with better citations and content"""

        system_prompt = f"""You are an expert grant proposal editor. Your task is to enhance
the provided "{section_name}" section while:

1. Improving citation quality using ONLY the provided research papers
2. Strengthening arguments with evidence
3. Improving clarity and flow
4. Ensuring all facts are properly cited
5. Maintaining the original structure and key points

NEVER invent citations. Use ONLY the papers provided."""

        user_prompt = f"""# Current Section Content:
{section_content}

# Available Research Papers:
{self._format_papers_for_enhancement(rag_data.get('papers', [])[:20])}

# Enhancement Instructions:
{enhancement_instructions or "Enhance this section with better citations and stronger arguments."}

Provide the enhanced section:"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.6,
                max_tokens=self.max_tokens
            )

            return response.choices[0].message.content

        except Exception as e:
            raise Exception(f"Error enhancing section: {str(e)}")

    def _format_papers_for_enhancement(self, papers: List[Dict]) -> str:
        """Format papers for enhancement prompt"""
        formatted = []
        for paper in papers:
            formatted.append(
                f"- {paper['citation_key']}: {paper['title']} "
                f"({', '.join(paper['authors'][:2])}, {paper['year']})"
            )
        return "\n".join(formatted)
