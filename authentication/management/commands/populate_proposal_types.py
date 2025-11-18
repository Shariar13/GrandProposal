"""
Management command to populate initial proposal types with templates
"""
from django.core.management.base import BaseCommand
from authentication.models import ProposalType, ProposalTemplate


class Command(BaseCommand):
    help = 'Populate database with initial proposal types and templates'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to populate proposal types...'))

        # Horizon Europe
        horizon_europe, created = ProposalType.objects.get_or_create(
            code='horizon_europe',
            defaults={
                'name': 'Horizon Europe',
                'description': 'EU\'s key funding programme for research and innovation. Tackles climate change, helps achieve UN Sustainable Development Goals and boosts EU competitiveness and growth.',
                'min_pages': 30,
                'max_pages': 70,
                'required_sections': [
                    'Excellence', 'Impact', 'Implementation', 'Consortium', 'Budget',
                    'Ethics and Security', 'Work Plan', 'Risk Management'
                ],
                'optional_sections': ['Letters of Support', 'Additional Documentation'],
                'template_style': {
                    'font': 'Arial or Times New Roman',
                    'font_size': '11pt',
                    'line_spacing': '1.5',
                    'margins': '2cm all sides',
                    'page_limit': '70 pages'
                },
                'is_active': True,
            }
        )
        if created:
            self._create_horizon_europe_templates(horizon_europe)
            self.stdout.write(self.style.SUCCESS('✓ Created Horizon Europe'))

        # Europol
        europol, created = ProposalType.objects.get_or_create(
            code='europol',
            defaults={
                'name': 'Europol Research Grant',
                'description': 'EU agency for law enforcement cooperation. Supports research in crime prevention, cybersecurity, counter-terrorism, and organized crime.',
                'min_pages': 15,
                'max_pages': 40,
                'required_sections': [
                    'Executive Summary', 'Background and Context', 'Research Objectives',
                    'Methodology', 'Expected Impact', 'Work Plan', 'Budget', 'Risk Assessment'
                ],
                'optional_sections': ['Data Protection', 'Stakeholder Engagement'],
                'template_style': {
                    'font': 'Arial',
                    'font_size': '11pt',
                    'line_spacing': '1.15',
                    'margins': '2.5cm all sides',
                    'page_limit': '40 pages'
                },
                'is_active': True,
            }
        )
        if created:
            self._create_europol_templates(europol)
            self.stdout.write(self.style.SUCCESS('✓ Created Europol'))

        # NSF (National Science Foundation)
        nsf, created = ProposalType.objects.get_or_create(
            code='nsf',
            defaults={
                'name': 'National Science Foundation (NSF)',
                'description': 'US federal agency supporting fundamental research and education in all non-medical fields of science and engineering.',
                'min_pages': 10,
                'max_pages': 15,
                'required_sections': [
                    'Project Summary', 'Project Description', 'References Cited',
                    'Biographical Sketches', 'Budget and Budget Justification',
                    'Current and Pending Support', 'Facilities and Equipment'
                ],
                'optional_sections': ['Data Management Plan', 'Postdoctoral Mentoring Plan'],
                'template_style': {
                    'font': 'Times Roman, Palatino, Computer Modern',
                    'font_size': '11pt',
                    'line_spacing': 'single',
                    'margins': '2.5cm all sides',
                    'page_limit': '15 pages for Project Description'
                },
                'is_active': True,
            }
        )
        if created:
            self._create_nsf_templates(nsf)
            self.stdout.write(self.style.SUCCESS('✓ Created NSF'))

        # NIH (National Institutes of Health)
        nih, created = ProposalType.objects.get_or_create(
            code='nih',
            defaults={
                'name': 'National Institutes of Health (NIH)',
                'description': 'US federal agency for medical and behavioral research. Primary agency of US government responsible for biomedical and public health research.',
                'min_pages': 12,
                'max_pages': 12,
                'required_sections': [
                    'Specific Aims', 'Research Strategy', 'Significance', 'Innovation',
                    'Approach', 'Bibliography', 'Budget and Justification'
                ],
                'optional_sections': ['Letters of Support', 'Resource Sharing Plan'],
                'template_style': {
                    'font': 'Arial, Georgia, Helvetica, Palatino',
                    'font_size': '11pt or larger',
                    'line_spacing': 'single',
                    'margins': '1.27cm (0.5 inch) all sides',
                    'page_limit': '12 pages for Research Strategy'
                },
                'is_active': True,
            }
        )
        if created:
            self._create_nih_templates(nih)
            self.stdout.write(self.style.SUCCESS('✓ Created NIH'))

        # ERC (European Research Council)
        erc, created = ProposalType.objects.get_or_create(
            code='erc',
            defaults={
                'name': 'European Research Council (ERC)',
                'description': 'Premier European funding organization for excellent frontier research. Funds creative researchers of any nationality and age to run projects across Europe.',
                'min_pages': 15,
                'max_pages': 15,
                'required_sections': [
                    'Extended Synopsis', 'State of the Art', 'Methodology',
                    'Resources', 'Track Record', 'Ethics'
                ],
                'optional_sections': ['Supplementary Documentation'],
                'template_style': {
                    'font': 'Arial, Verdana, Calibri, Times New Roman',
                    'font_size': '11pt minimum',
                    'line_spacing': 'single',
                    'margins': '2cm all sides',
                    'page_limit': '15 pages for Part B'
                },
                'is_active': True,
            }
        )
        if created:
            self._create_erc_templates(erc)
            self.stdout.write(self.style.SUCCESS('✓ Created ERC'))

        # Marie Curie Actions
        marie_curie, created = ProposalType.objects.get_or_create(
            code='marie_curie',
            defaults={
                'name': 'Marie Skłodowska-Curie Actions',
                'description': 'EU programme to support research careers and foster excellence in training. Promotes international mobility and interdisciplinary collaboration.',
                'min_pages': 10,
                'max_pages': 10,
                'required_sections': [
                    'Excellence', 'Impact', 'Implementation',
                    'CV of Researcher', 'Capacity of Host Institution'
                ],
                'optional_sections': ['Letters of Commitment'],
                'template_style': {
                    'font': 'Arial, Times New Roman',
                    'font_size': '11pt',
                    'line_spacing': 'single',
                    'margins': '2cm all sides',
                    'page_limit': '10 pages for Part B'
                },
                'is_active': True,
            }
        )
        if created:
            self._create_marie_curie_templates(marie_curie)
            self.stdout.write(self.style.SUCCESS('✓ Created Marie Curie'))

        # Wellcome Trust
        wellcome, created = ProposalType.objects.get_or_create(
            code='wellcome_trust',
            defaults={
                'name': 'Wellcome Trust',
                'description': 'UK-based charitable foundation focused on health research. One of the world\'s largest funders of scientific and medical research.',
                'min_pages': 8,
                'max_pages': 20,
                'required_sections': [
                    'Research Proposal', 'Track Record', 'Resources and Management',
                    'Value for Money', 'Public Engagement'
                ],
                'optional_sections': ['Applicant Details', 'Costings'],
                'template_style': {
                    'font': 'Arial',
                    'font_size': '11pt',
                    'line_spacing': 'single or 1.5',
                    'margins': '2cm all sides',
                    'page_limit': 'Varies by scheme'
                },
                'is_active': True,
            }
        )
        if created:
            self._create_wellcome_templates(wellcome)
            self.stdout.write(self.style.SUCCESS('✓ Created Wellcome Trust'))

        # Gates Foundation
        gates, created = ProposalType.objects.get_or_create(
            code='gates_foundation',
            defaults={
                'name': 'Gates Foundation',
                'description': 'Private foundation focused on enhancing healthcare and reducing extreme poverty globally. Major funder in global health and development.',
                'min_pages': 10,
                'max_pages': 25,
                'required_sections': [
                    'Executive Summary', 'Background and Need', 'Goals and Objectives',
                    'Activities and Methods', 'Evaluation Plan', 'Budget', 'Sustainability'
                ],
                'optional_sections': ['Theory of Change', 'Risk Mitigation'],
                'template_style': {
                    'font': 'Arial, Calibri',
                    'font_size': '11pt',
                    'line_spacing': 'single',
                    'margins': '2.5cm all sides',
                    'page_limit': '25 pages'
                },
                'is_active': True,
            }
        )
        if created:
            self._create_gates_templates(gates)
            self.stdout.write(self.style.SUCCESS('✓ Created Gates Foundation'))

        # DARPA
        darpa, created = ProposalType.objects.get_or_create(
            code='darpa',
            defaults={
                'name': 'DARPA',
                'description': 'Defense Advanced Research Projects Agency. Develops breakthrough technologies for national security.',
                'min_pages': 15,
                'max_pages': 25,
                'required_sections': [
                    'Technical Volume', 'Management Volume', 'Cost Volume',
                    'Technical Approach', 'Statement of Work', 'Schedule'
                ],
                'optional_sections': ['Appendices', 'Technical Data'],
                'template_style': {
                    'font': 'Times New Roman, Arial',
                    'font_size': '12pt',
                    'line_spacing': 'single',
                    'margins': '2.5cm all sides',
                    'page_limit': 'Varies by BAA'
                },
                'is_active': True,
            }
        )
        if created:
            self._create_darpa_templates(darpa)
            self.stdout.write(self.style.SUCCESS('✓ Created DARPA'))

        # UK Research and Innovation
        ukri, created = ProposalType.objects.get_or_create(
            code='uk_research',
            defaults={
                'name': 'UK Research and Innovation',
                'description': 'UK\'s largest public funder of research and innovation. Operates through nine councils including EPSRC, MRC, BBSRC, AHRC.',
                'min_pages': 8,
                'max_pages': 15,
                'required_sections': [
                    'Case for Support', 'Objectives', 'Methodology',
                    'Management', 'Pathways to Impact', 'Resources'
                ],
                'optional_sections': ['Data Management Plan', 'Justification of Resources'],
                'template_style': {
                    'font': 'Arial',
                    'font_size': '11pt',
                    'line_spacing': 'single',
                    'margins': '2cm all sides',
                    'page_limit': '8 pages for Case for Support'
                },
                'is_active': True,
            }
        )
        if created:
            self._create_ukri_templates(ukri)
            self.stdout.write(self.style.SUCCESS('✓ Created UKRI'))

        self.stdout.write(self.style.SUCCESS('\n✅ Successfully populated all proposal types!'))

    def _create_horizon_europe_templates(self, proposal_type):
        """Create section templates for Horizon Europe"""
        templates = [
            {
                'section_name': 'Excellence',
                'section_order': 1,
                'is_required': True,
                'min_words': 3000,
                'max_words': 6000,
                'description': 'Describe the state of the art, objectives, and methodological approach',
                'prompt_template': 'Generate Excellence section covering: state of the art, research objectives, novel methodology, and expected breakthrough results. Use retrieved papers to demonstrate knowledge gaps and innovation.'
            },
            {
                'section_name': 'Impact',
                'section_order': 2,
                'is_required': True,
                'min_words': 2500,
                'max_words': 5000,
                'description': 'Describe expected impacts and dissemination strategy',
                'prompt_template': 'Generate Impact section covering: scientific, societal, and economic impacts; dissemination and exploitation plans; communication strategy.'
            },
            {
                'section_name': 'Implementation',
                'section_order': 3,
                'is_required': True,
                'min_words': 3000,
                'max_words': 6000,
                'description': 'Describe work plan, consortium, and resources',
                'prompt_template': 'Generate Implementation section covering: work packages, deliverables, milestones, consortium composition, management structure, resources.'
            },
            {
                'section_name': 'Consortium and Resources',
                'section_order': 4,
                'is_required': True,
                'min_words': 2000,
                'max_words': 4000,
                'description': 'Describe partner qualifications and available resources',
                'prompt_template': 'Generate section on consortium partners, their expertise, roles, and available facilities/resources.'
            },
            {
                'section_name': 'Ethics and Security',
                'section_order': 5,
                'is_required': True,
                'min_words': 1000,
                'max_words': 2000,
                'description': 'Address ethical and security aspects',
                'prompt_template': 'Generate section covering ethical considerations, data protection, security measures, and compliance with EU regulations.'
            },
        ]

        for template_data in templates:
            ProposalTemplate.objects.get_or_create(
                proposal_type=proposal_type,
                section_name=template_data['section_name'],
                defaults=template_data
            )

    def _create_europol_templates(self, proposal_type):
        """Create section templates for Europol"""
        templates = [
            {
                'section_name': 'Executive Summary',
                'section_order': 1,
                'is_required': True,
                'min_words': 500,
                'max_words': 1000,
                'description': 'Concise overview of the research proposal',
                'prompt_template': 'Generate executive summary covering: research problem, objectives, methodology, expected impact on law enforcement.'
            },
            {
                'section_name': 'Background and Context',
                'section_order': 2,
                'is_required': True,
                'min_words': 1500,
                'max_words': 3000,
                'description': 'Current state of crime/security challenge',
                'prompt_template': 'Generate background section on the security challenge, current state of the art in addressing it, and research gaps. Focus on law enforcement relevance.'
            },
            {
                'section_name': 'Research Objectives',
                'section_order': 3,
                'is_required': True,
                'min_words': 1000,
                'max_words': 2000,
                'description': 'Clear research objectives and questions',
                'prompt_template': 'Generate specific, measurable research objectives addressing the security challenge and supporting Europol\'s mission.'
            },
            {
                'section_name': 'Methodology',
                'section_order': 4,
                'is_required': True,
                'min_words': 2000,
                'max_words': 4000,
                'description': 'Detailed research methodology',
                'prompt_template': 'Generate comprehensive methodology covering data collection, analysis methods, validation approach, and compliance with data protection.'
            },
            {
                'section_name': 'Expected Impact',
                'section_order': 5,
                'is_required': True,
                'min_words': 1500,
                'max_words': 3000,
                'description': 'Expected impact on law enforcement',
                'prompt_template': 'Generate section on expected operational, strategic, and policy impacts for law enforcement agencies.'
            },
        ]

        for template_data in templates:
            ProposalTemplate.objects.get_or_create(
                proposal_type=proposal_type,
                section_name=template_data['section_name'],
                defaults=template_data
            )

    def _create_nsf_templates(self, proposal_type):
        """Create section templates for NSF"""
        templates = [
            {
                'section_name': 'Project Summary',
                'section_order': 1,
                'is_required': True,
                'min_words': 200,
                'max_words': 300,
                'description': 'One-page overview of intellectual merit and broader impacts',
                'prompt_template': 'Generate 1-page project summary with Overview, Intellectual Merit, and Broader Impacts subsections.'
            },
            {
                'section_name': 'Project Description',
                'section_order': 2,
                'is_required': True,
                'min_words': 5000,
                'max_words': 7500,
                'description': '15-page detailed project description',
                'prompt_template': 'Generate comprehensive project description covering: introduction, background, research plan, intellectual merit, broader impacts, timeline.'
            },
            {
                'section_name': 'Intellectual Merit',
                'section_order': 3,
                'is_required': True,
                'min_words': 2000,
                'max_words': 3000,
                'description': 'Demonstrate advancement of knowledge',
                'prompt_template': 'Generate section demonstrating how the project advances knowledge and understanding within its field and across fields.'
            },
            {
                'section_name': 'Broader Impacts',
                'section_order': 4,
                'is_required': True,
                'min_words': 1500,
                'max_words': 2500,
                'description': 'Demonstrate benefits to society',
                'prompt_template': 'Generate section on broader impacts: societal benefits, STEM education, diversity, dissemination, infrastructure.'
            },
            {
                'section_name': 'Data Management Plan',
                'section_order': 5,
                'is_required': False,
                'min_words': 500,
                'max_words': 1000,
                'description': 'Plan for managing and sharing research data',
                'prompt_template': 'Generate data management plan covering: types of data, standards, access policies, archiving, and sharing plans.'
            },
        ]

        for template_data in templates:
            ProposalTemplate.objects.get_or_create(
                proposal_type=proposal_type,
                section_name=template_data['section_name'],
                defaults=template_data
            )

    def _create_nih_templates(self, proposal_type):
        """Create section templates for NIH"""
        templates = [
            {
                'section_name': 'Specific Aims',
                'section_order': 1,
                'is_required': True,
                'min_words': 500,
                'max_words': 600,
                'description': 'One-page statement of research goals',
                'prompt_template': 'Generate 1-page Specific Aims covering: problem/gap, long-term goal, objective, central hypothesis, rationale, aims.'
            },
            {
                'section_name': 'Significance',
                'section_order': 2,
                'is_required': True,
                'min_words': 2000,
                'max_words': 3000,
                'description': 'Explain importance of research problem',
                'prompt_template': 'Generate Significance section: importance of problem, critical barriers, address barriers, expected outcomes, impact on field.'
            },
            {
                'section_name': 'Innovation',
                'section_order': 3,
                'is_required': True,
                'min_words': 1500,
                'max_words': 2500,
                'description': 'Explain novel aspects of the project',
                'prompt_template': 'Generate Innovation section: novel concepts, approaches, methodologies, instrumentation, or interventions.'
            },
            {
                'section_name': 'Approach',
                'section_order': 4,
                'is_required': True,
                'min_words': 4000,
                'max_words': 6000,
                'description': 'Detailed research strategy and methods',
                'prompt_template': 'Generate Approach section with subsections for each Specific Aim: rationale, experimental design, methods, expected outcomes, potential problems and alternatives, timeline.'
            },
        ]

        for template_data in templates:
            ProposalTemplate.objects.get_or_create(
                proposal_type=proposal_type,
                section_name=template_data['section_name'],
                defaults=template_data
            )

    def _create_erc_templates(self, proposal_type):
        """Create section templates for ERC"""
        templates = [
            {
                'section_name': 'Extended Synopsis',
                'section_order': 1,
                'is_required': True,
                'min_words': 300,
                'max_words': 500,
                'description': 'Short overview of the project',
                'prompt_template': 'Generate 1-page synopsis: project title, objectives, key research questions, approach, breakthrough potential.'
            },
            {
                'section_name': 'State of the Art and Objectives',
                'section_order': 2,
                'is_required': True,
                'min_words': 2000,
                'max_words': 3000,
                'description': 'Current state of research and research objectives',
                'prompt_template': 'Generate section on current state of the art, limitations, research objectives, and how they go beyond state of the art.'
            },
            {
                'section_name': 'Methodology',
                'section_order': 3,
                'is_required': True,
                'min_words': 3000,
                'max_words': 5000,
                'description': 'Research methodology and work plan',
                'prompt_template': 'Generate detailed methodology: overall approach, work packages, interdisciplinary aspects, feasibility, risk management.'
            },
            {
                'section_name': 'Resources and Team',
                'section_order': 4,
                'is_required': True,
                'min_words': 1500,
                'max_words': 2500,
                'description': 'Research environment and team composition',
                'prompt_template': 'Generate section on PI track record, host institution resources, team composition, and why this is right environment.'
            },
        ]

        for template_data in templates:
            ProposalTemplate.objects.get_or_create(
                proposal_type=proposal_type,
                section_name=template_data['section_name'],
                defaults=template_data
            )

    def _create_marie_curie_templates(self, proposal_type):
        """Create section templates for Marie Curie"""
        templates = [
            {
                'section_name': 'Excellence',
                'section_order': 1,
                'is_required': True,
                'min_words': 2000,
                'max_words': 3000,
                'description': 'Quality and credibility of research',
                'prompt_template': 'Generate Excellence section: research objectives, originality, quality of training, complementarity with fellow\'s profile.'
            },
            {
                'section_name': 'Impact',
                'section_order': 2,
                'is_required': True,
                'min_words': 1500,
                'max_words': 2500,
                'description': 'Impact on fellow\'s career and research field',
                'prompt_template': 'Generate Impact section: career development, knowledge transfer, communication and dissemination.'
            },
            {
                'section_name': 'Implementation',
                'section_order': 3,
                'is_required': True,
                'min_words': 2000,
                'max_words': 3000,
                'description': 'Quality of training and supervision',
                'prompt_template': 'Generate Implementation section: work plan, supervision, training, secondments, management of IPR.'
            },
        ]

        for template_data in templates:
            ProposalTemplate.objects.get_or_create(
                proposal_type=proposal_type,
                section_name=template_data['section_name'],
                defaults=template_data
            )

    def _create_wellcome_templates(self, proposal_type):
        """Create section templates for Wellcome Trust"""
        templates = [
            {
                'section_name': 'Research Proposal',
                'section_order': 1,
                'is_required': True,
                'min_words': 3000,
                'max_words': 6000,
                'description': 'Detailed research plan',
                'prompt_template': 'Generate research proposal: background, objectives, methods, expected outcomes, significance.'
            },
            {
                'section_name': 'Track Record',
                'section_order': 2,
                'is_required': True,
                'min_words': 1000,
                'max_words': 2000,
                'description': 'Applicant and team track record',
                'prompt_template': 'Generate track record section: key publications, achievements, expertise, team composition.'
            },
            {
                'section_name': 'Public Engagement',
                'section_order': 3,
                'is_required': True,
                'min_words': 1000,
                'max_words': 1500,
                'description': 'Plans for public engagement and communication',
                'prompt_template': 'Generate public engagement plan: target audiences, activities, timeline, expected outcomes.'
            },
        ]

        for template_data in templates:
            ProposalTemplate.objects.get_or_create(
                proposal_type=proposal_type,
                section_name=template_data['section_name'],
                defaults=template_data
            )

    def _create_gates_templates(self, proposal_type):
        """Create section templates for Gates Foundation"""
        templates = [
            {
                'section_name': 'Executive Summary',
                'section_order': 1,
                'is_required': True,
                'min_words': 500,
                'max_words': 1000,
                'description': 'Brief overview of project',
                'prompt_template': 'Generate executive summary: problem statement, proposed solution, expected impact, sustainability.'
            },
            {
                'section_name': 'Background and Need',
                'section_order': 2,
                'is_required': True,
                'min_words': 2000,
                'max_words': 3000,
                'description': 'Problem description and evidence of need',
                'prompt_template': 'Generate background: global health/development challenge, current gaps, target population, evidence of need.'
            },
            {
                'section_name': 'Goals and Objectives',
                'section_order': 3,
                'is_required': True,
                'min_words': 1500,
                'max_words': 2500,
                'description': 'Clear goals and measurable objectives',
                'prompt_template': 'Generate goals and SMART objectives aligned with Foundation strategy and target outcomes.'
            },
            {
                'section_name': 'Theory of Change',
                'section_order': 4,
                'is_required': True,
                'min_words': 2000,
                'max_words': 3000,
                'description': 'How activities lead to desired outcomes',
                'prompt_template': 'Generate theory of change: inputs, activities, outputs, outcomes, impact, assumptions, risks.'
            },
        ]

        for template_data in templates:
            ProposalTemplate.objects.get_or_create(
                proposal_type=proposal_type,
                section_name=template_data['section_name'],
                defaults=template_data
            )

    def _create_darpa_templates(self, proposal_type):
        """Create section templates for DARPA"""
        templates = [
            {
                'section_name': 'Technical Volume',
                'section_order': 1,
                'is_required': True,
                'min_words': 4000,
                'max_words': 8000,
                'description': 'Detailed technical approach',
                'prompt_template': 'Generate technical volume: innovative approach, technical rationale, anticipated challenges, feasibility.'
            },
            {
                'section_name': 'Management Volume',
                'section_order': 2,
                'is_required': True,
                'min_words': 2000,
                'max_words': 4000,
                'description': 'Management plan and team',
                'prompt_template': 'Generate management plan: team organization, responsibilities, facilities, risk management.'
            },
            {
                'section_name': 'Statement of Work',
                'section_order': 3,
                'is_required': True,
                'min_words': 2000,
                'max_words': 3000,
                'description': 'Detailed work breakdown',
                'prompt_template': 'Generate SOW: tasks, subtasks, deliverables, milestones, dependencies.'
            },
        ]

        for template_data in templates:
            ProposalTemplate.objects.get_or_create(
                proposal_type=proposal_type,
                section_name=template_data['section_name'],
                defaults=template_data
            )

    def _create_ukri_templates(self, proposal_type):
        """Create section templates for UKRI"""
        templates = [
            {
                'section_name': 'Case for Support',
                'section_order': 1,
                'is_required': True,
                'min_words': 3000,
                'max_words': 4000,
                'description': 'Main research case (8 pages)',
                'prompt_template': 'Generate case for support: background, research questions, methods, timeliness, outputs and dissemination.'
            },
            {
                'section_name': 'Pathways to Impact',
                'section_order': 2,
                'is_required': True,
                'min_words': 1000,
                'max_words': 1500,
                'description': 'How research will achieve impact',
                'prompt_template': 'Generate pathways to impact: beneficiaries, impact activities, timescales, resources.'
            },
            {
                'section_name': 'Data Management Plan',
                'section_order': 3,
                'is_required': True,
                'min_words': 500,
                'max_words': 1000,
                'description': 'Plans for managing research data',
                'prompt_template': 'Generate DMP: data types, standards, sharing, preservation, ethical/legal compliance.'
            },
        ]

        for template_data in templates:
            ProposalTemplate.objects.get_or_create(
                proposal_type=proposal_type,
                section_name=template_data['section_name'],
                defaults=template_data
            )
