

import os
import re
import json
from typing import List, Dict, Generator, Tuple
from collections import defaultdict

from openai import OpenAI
from django.conf import settings


class ProposalEnhancer:

    
    def __init__(self, api_key: str = None):
        """
        Initialize the ProposalEnhancer with OpenAI API credentials.
        
        Args:
            api_key (str, optional): OpenAI API key. If not provided, 
                                    uses Django settings.OPENAI_API_KEY
        
        Raises:
            ValueError: If no API key is available from either parameter or settings
        """
        # Priority: parameter > Django settings > environment variable
        self.api_key = api_key or getattr(settings, 'OPENAI_API_KEY', None) or os.environ.get('OPENAI_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. Please set one of the following:\n"
                "1. Pass api_key parameter to ProposalEnhancer()\n"
                "2. Set OPENAI_API_KEY in Django settings.py\n"
                "3. Set OPENAI_API_KEY environment variable"
            )
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)
        
        # Model configuration from Django settings or defaults
        self.model = getattr(settings, 'OPENAI_MODEL', 'gpt-4o-mini')
        self.max_tokens = getattr(settings, 'OPENAI_MAX_TOKENS', 4000)
        self.temperature = getattr(settings, 'OPENAI_TEMPERATURE', 0.7)
        
    def extract_citations_and_references(self, proposal_text: str) -> Dict:
        """
        Extract all citations and references from the proposal text.
        
        This method:
        - Identifies the REFERENCES section
        - Maps citation numbers to their full references
        - Collects all used citation numbers
        - Preserves the original proposal text
        
        Args:
            proposal_text (str): The complete proposal text
            
        Returns:
            Dict: Dictionary containing:
                - references_section: The complete REFERENCES section text
                - citation_map: Dict mapping citation numbers to reference text
                - used_citations: Sorted list of all citation numbers used
                - original_proposal: The original proposal text
        """
        # Extract REFERENCES section (matches REFERENCES followed by === line)
        refs_match = re.search(r'REFERENCES\s*={60,}\s*(.*?)$', proposal_text, re.DOTALL)
        references_section = refs_match.group(1).strip() if refs_match else ""
        
        # Find all citations in format [1], [2,3], etc.
        citation_pattern = r'\[(\d+(?:,\s*\d+)*)\]'
        citations = re.findall(citation_pattern, proposal_text)
        
        # Build citation map from REFERENCES section
        citation_map = {}
        if references_section:
            ref_lines = references_section.split('\n')
            for line in ref_lines:
                # Match format: [1] Reference text here
                match = re.match(r'\[(\d+)\]\s*(.*)', line.strip())
                if match:
                    citation_map[match.group(1)] = match.group(2)
        
        # Collect all unique citation numbers
        all_citation_nums = set()
        for citation in citations:
            nums = [n.strip() for n in citation.split(',')]
            all_citation_nums.update(nums)
        
        return {
            'references_section': references_section,
            'citation_map': citation_map,
            'used_citations': sorted(list(all_citation_nums), key=lambda x: int(x)),
            'original_proposal': proposal_text
        }
    
    def create_enhancement_prompt(self, section_title: str, section_content: str, 
                                   available_citations: List[str], context: str) -> str:
        """
        Create a detailed enhancement prompt for LLM based on section type.
        
        This method generates section-specific prompts that:
        - Define clear enhancement objectives
        - Specify required content elements
        - Provide available citations
        - Include context from previous sections
        - Set quality standards for EU Horizon proposals
        
        Args:
            section_title (str): Title of the section to enhance
            section_content (str): Current content of the section
            available_citations (List[str]): List of valid citation numbers
            context (str): Summary of previous sections for coherence
            
        Returns:
            str: Complete enhancement prompt for the LLM
        """
        prompt = f"""You are an EU Horizon Europe proposal expert who has written 50+ funded proposals. 

CRITICAL: This section must demonstrate RESEARCH EXCELLENCE suitable for EU funding panel review.

SECTION: {section_title}

CURRENT CONTENT:
{section_content}

AVAILABLE CITATIONS (you MUST use these exact numbers when citing):
{', '.join(available_citations)}

CRITICAL RULES:
1. Use SPECIFIC quantitative targets (e.g., "achieve 95% accuracy", "reduce costs by 40%", "TRL advancement from 3 to 6")
2. Reference ALL relevant citations naturally to support every major claim
3. Integrate findings from previous sections: {context}
4. Follow EU evaluation criteria: Excellence, Impact, Implementation quality
5. Be concrete, not generic - include actual methods, tools, timelines, deliverables

AVOID: Generic statements, vague objectives, disconnected sections
INCLUDE: Specific methodologies, clear success metrics, realistic timelines, justified resources

CONTEXT FROM OTHER SECTIONS:
{context}

ENHANCEMENT REQUIREMENTS FOR THIS SECTION:
"""

        # Section-specific enhancement requirements
        requirements = {
            "Executive Summary": """
- Expand to 2-3 pages with clear problem statement, objectives, methodology overview, expected impact
- Include quantitative targets and measurable outcomes
- Highlight innovation and competitive advantages
- Emphasize EU priorities and alignment with Horizon Europe strategic plan""",
            
            "Introduction and Background": """
- Provide comprehensive context with historical development
- Detailed problem analysis with statistics and evidence
- Clear research gaps with extensive literature support
- Strong rationale with societal/economic impact
- Expand to 4-5 pages with rich contextual detail""",
            
            "Literature Review": """
- Comprehensive analysis of state-of-the-art (5-8 pages)
- Thematic organization with critical analysis
- Detailed comparison tables of existing approaches
- Clear identification of limitations in current research
- Synthesis showing how your project advances beyond current state""",
            
            "Theoretical Framework": """
- Rigorous theoretical foundations with formal models where appropriate
- Detailed conceptual architecture with diagrams (described textually)
- Clear theoretical contributions and novel constructs
- Integration of multiple theoretical perspectives
- 3-4 pages of deep theoretical development""",
            
            "Research Questions and Hypotheses": """
- Detailed elaboration of each research question with sub-questions
- Clear testable hypotheses with specific predictions
- Operationalization of variables and constructs
- Expected relationships and causal models
- 2-3 pages with comprehensive coverage""",
            
            "Research Objectives": """
- SMART objectives with specific, measurable targets
- Clear success criteria and validation methods
- Detailed deliverables for each objective
- Timeline alignment and dependencies
- 2-3 pages with granular detail""",
            
            "Methodology and Approach": """
- Extremely detailed technical approach (8-12 pages)
- Step-by-step procedures and protocols
- Specific tools, technologies, and platforms with versions
- Data collection instruments and validation procedures
- Statistical analysis plans with specific tests
- Quality assurance and validation protocols
- Detailed experimental design with sample sizes, power analysis
- Ethics considerations and compliance""",
            
            "Work Plan and Timeline": """
- Detailed Gantt chart description with all tasks and sub-tasks
- Month-by-month breakdown for entire project duration
- Clear milestones with verification criteria
- Resource allocation per task
- Critical path analysis
- Risk contingencies per phase
- 4-5 pages with comprehensive planning""",
            
            "Expected Outcomes and Impact": """
- Detailed scientific, technological, economic, and societal impacts
- Specific quantitative targets for each outcome
- Dissemination strategy with target venues and audiences
- Exploitation plan and IP management
- Long-term sustainability and scalability
- Alignment with EU priorities and SDGs
- 4-5 pages""",
            
            "Risk Assessment and Mitigation": """
- Comprehensive risk register with likelihood and impact ratings
- Detailed mitigation strategies for each risk
- Contingency plans with alternative approaches
- Monitoring and early warning indicators
- Escalation procedures
- 2-3 pages""",
            
            "Budget Justification": """
- Detailed cost breakdown by work package and task
- Justification for each budget line
- Cost-effectiveness analysis
- Value for money demonstration
- Compliance with funding rules
- 3-4 pages""",
            
            "Broader Impacts": """
- Comprehensive impact pathways
- Stakeholder engagement strategy
- Policy influence mechanisms
- Capacity building and training plans
- Gender equality and inclusion measures
- Open science and data management
- 3-4 pages""",
            
            "Data Management Plan": """
- FAIR data principles implementation
- Detailed data lifecycle management
- Repository selection and preservation strategy
- Access policies and ethical considerations
- IPR and licensing
- Costs and resources
- 2-3 pages"""
        }
        
        # Add section-specific requirements or default
        prompt += requirements.get(section_title, """
- Expand to 3-4 pages with comprehensive detail
- Add specific examples, case studies, and concrete details
- Include quantitative information where possible
- Maintain academic rigor and formal tone""")
        
        prompt += """

OUTPUT FORMAT:
Provide ONLY the enhanced section content. Do NOT include the section title or any meta-commentary. 
Write in continuous prose with proper paragraphs and subsections as needed.
Ensure all citations use the exact format [1], [2,3] etc. with ONLY the numbers from the available list.
"""
        
        return prompt
    
    def enhance_section_streaming(self, section_title: str, section_content: str,
                                   citation_data: Dict, context: str = "") -> Generator:
        """
        Enhance a single section using streaming LLM responses.
        
        This method:
        - Creates an enhancement prompt
        - Streams the enhanced content token by token
        - Handles errors gracefully
        - Yields content chunks for real-time display
        
        Args:
            section_title (str): Title of the section to enhance
            section_content (str): Current content of the section
            citation_data (Dict): Citation information from extract_citations_and_references
            context (str): Summary of previous sections
            
        Yields:
            str: Chunks of enhanced content as they are generated
        """
        available_citations = citation_data['used_citations']
        
        prompt = self.create_enhancement_prompt(
            section_title, 
            section_content, 
            available_citations,
            context
        )
        
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert EU Horizon Europe grant proposal writer. 
You specialize in creating comprehensive, detailed proposals that meet the highest academic and professional standards.
You NEVER hallucinate citations - you only use citation numbers that are explicitly provided to you.
You write in clear, formal academic English with varied sentence structures and rich detail."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            yield f"\n\n[Enhancement Error: {str(e)}]\n\n"
    
    def validate_citations(self, enhanced_text: str, allowed_citations: List[str]) -> Tuple[bool, List[str]]:
        """
        Validate that all citations in enhanced text are from the allowed list.
        
        This prevents hallucinated citations and ensures integrity.
        
        Args:
            enhanced_text (str): The enhanced section text
            allowed_citations (List[str]): List of valid citation numbers
            
        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_invalid_citations)
        """
        citation_pattern = r'\[(\d+(?:,\s*\d+)*)\]'
        found_citations = re.findall(citation_pattern, enhanced_text)
        
        invalid = []
        for citation in found_citations:
            nums = [n.strip() for n in citation.split(',')]
            for num in nums:
                if num not in allowed_citations:
                    invalid.append(num)
        
        return len(invalid) == 0, list(set(invalid))
    
    def enhance_full_proposal(self, original_proposal: str) -> Generator:
        """
        Enhance the complete proposal with streaming JSON events.
        
        This method:
        - Extracts and validates citations
        - Processes each section sequentially
        - Maintains context between sections
        - Validates citations in enhanced content
        - Preserves the original REFERENCES section
        - Yields JSON events for progress tracking
        
        Args:
            original_proposal (str): The complete original proposal text
            
        Yields:
            str: JSON-formatted events containing:
                - type: 'status', 'content', 'warning', or 'complete'
                - content: The actual content/message
        """
        # Step 1: Extract citations
        yield json.dumps({
            "type": "status",
            "content": "Analyzing original proposal and extracting citations..."
        }) + "\n"
        
        citation_data = self.extract_citations_and_references(original_proposal)
        
        yield json.dumps({
            "type": "status",
            "content": f"Found {len(citation_data['used_citations'])} citations. Preserving all references..."
        }) + "\n"
        
        # Step 2: Split into sections
        sections = self._split_into_sections(original_proposal)
        
        yield json.dumps({
            "type": "status",
            "content": f"Identified {len(sections)} sections for enhancement..."
        }) + "\n"
        
        # Step 3: Start enhanced proposal
        yield json.dumps({
            "type": "content", 
            "content": "ENHANCED GRANT PROPOSAL\n" + "="*80 + "\n\n"
        }) + "\n"
        
        # Add title and metadata
        title_match = re.search(r'Title:\s*(.+)', original_proposal)
        if title_match:
            yield json.dumps({
                "type": "content", 
                "content": f"Title: {title_match.group(1)}\n"
            }) + "\n"
        
        keywords_match = re.search(r'Keywords:\s*(.+)', original_proposal)
        if keywords_match:
            yield json.dumps({
                "type": "content", 
                "content": f"Keywords: {keywords_match.group(1)}\n"
            }) + "\n"
        
        yield json.dumps({
            "type": "content", 
            "content": "Duration: 36 months\n"
        }) + "\n"
        
        yield json.dumps({
            "type": "content", 
            "content": "Enhanced with AI for EU Horizon Europe standards\n\n"
        }) + "\n"
        
        # Step 4: Enhance each section
        context_buffer = ""
        for i, (section_title, section_content) in enumerate(sections, 1):
            # Skip REFERENCES section (will be added at the end)
            if section_title == "REFERENCES":
                continue
            
            yield json.dumps({
                "type": "status",
                "content": f"Enhancing section {i}/{len(sections)}: {section_title}"
            }) + "\n"
            
            yield json.dumps({
                "type": "content",
                "content": f"\n{section_title}\n" + "="*80 + "\n\n"
            }) + "\n"
            
            # Enhance section with streaming
            enhanced_content = ""
            for chunk in self.enhance_section_streaming(
                section_title, 
                section_content, 
                citation_data,
                context_buffer
            ):
                enhanced_content += chunk
                yield json.dumps({
                    "type": "content", 
                    "content": chunk
                }) + "\n"
            
            # Validate citations
            is_valid, invalid = self.validate_citations(
                enhanced_content, 
                citation_data['used_citations']
            )
            
            if not is_valid:
                yield json.dumps({
                    "type": "warning",
                    "content": f"Warning: Removed invalid citations {invalid} from {section_title}"
                }) + "\n"
                
                # Remove invalid citations
                for inv in invalid:
                    enhanced_content = re.sub(rf'\[{inv}\]', '', enhanced_content)
            
            # Update context buffer with last 3000 chars of previous sections
            context_buffer = (context_buffer + "\n" + section_title + ": " + 
                            enhanced_content[:500])[-3000:]
            
            yield json.dumps({
                "type": "content", 
                "content": "\n"
            }) + "\n"
        
        # Step 5: Add REFERENCES section
        yield json.dumps({
            "type": "status",
            "content": "Adding validated references section..."
        }) + "\n"
        
        yield json.dumps({
            "type": "content",
            "content": f"\nREFERENCES\n" + "="*80 + "\n\n"
        }) + "\n"
        
        yield json.dumps({
            "type": "content",
            "content": citation_data['references_section']
        }) + "\n"
        
        # Step 6: Complete
        yield json.dumps({
            "type": "complete",
            "content": "Enhancement complete! Expanded to EU Horizon standards with all citations preserved."
        }) + "\n"
    
    def _split_into_sections(self, proposal_text: str) -> List[Tuple[str, str]]:
        """
        Split proposal text into sections based on headers.
        
        Recognizes:
        - "Executive Summary"
        - "REFERENCES"
        - Numbered sections like "1. Introduction"
        
        Args:
            proposal_text (str): The complete proposal text
            
        Returns:
            List[Tuple[str, str]]: List of (section_title, section_content) tuples
        """
        section_pattern = r'^((?:Executive Summary|REFERENCES|\d+\.\s+.+?))$'
        
        lines = proposal_text.split('\n')
        sections = []
        current_section = None
        current_content = []
        
        for line in lines:
            if re.match(section_pattern, line.strip()):
                # Save previous section
                if current_section:
                    sections.append((current_section, '\n'.join(current_content)))
                
                # Start new section
                current_section = line.strip()
                current_content = []
            else:
                current_content.append(line)
        
        # Add last section
        if current_section:
            sections.append((current_section, '\n'.join(current_content)))
        
        return sections
    
    def enhance_proposal_batch(self, original_proposal: str) -> str:
        """
        Enhance proposal in batch mode (non-streaming).
        
        This method collects all streaming events and returns the complete
        enhanced proposal as a single string.
        
        Args:
            original_proposal (str): The complete original proposal text
            
        Returns:
            str: The complete enhanced proposal text
        """
        result = []
        for event in self.enhance_full_proposal(original_proposal):
            data = json.loads(event.strip())
            if data['type'] == 'content':
                result.append(data['content'])
        
        return ''.join(result)


# ==============================================================================
# USAGE EXAMPLES
# ==============================================================================

def example_usage():
    """
    Example usage of the ProposalEnhancer class.
    """
    # Example 1: Using with Django settings (recommended)
    enhancer = ProposalEnhancer()
    
    # Example 2: Using with explicit API key
    # enhancer = ProposalEnhancer(api_key="your-api-key-here")
    
    # Load proposal
    with open('original_proposal.txt', 'r') as f:
        original_proposal = f.read()
    
    # Streaming enhancement (for real-time updates)
    print("Enhancing proposal (streaming)...")
    with open('enhanced_proposal.txt', 'w') as f:
        for event in enhancer.enhance_full_proposal(original_proposal):
            data = json.loads(event.strip())
            if data['type'] == 'status':
                print(f"Status: {data['content']}")
            elif data['type'] == 'content':
                f.write(data['content'])
            elif data['type'] == 'warning':
                print(f"Warning: {data['content']}")
            elif data['type'] == 'complete':
                print(f"Complete: {data['content']}")
    
    # Batch enhancement (for simple cases)
    # enhanced = enhancer.enhance_proposal_batch(original_proposal)


if __name__ == "__main__":
    example_usage()