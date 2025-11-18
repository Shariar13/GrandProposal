from typing import List, Dict
import re


class CitationManager:
    def __init__(self):
        self.citations = []
        self.citation_map = {}
        
    def add_citation(self, paper: Dict) -> int:
        citation_key = paper.get('doi', '') or paper.get('title', '')
        
        if citation_key in self.citation_map:
            return self.citation_map[citation_key]
        
        citation_num = len(self.citations) + 1
        self.citations.append(paper)
        self.citation_map[citation_key] = citation_num
        return citation_num
    
    def get_citation_text(self, citation_nums: List[int]) -> str:
        return f"[{', '.join(map(str, citation_nums))}]"
    
    def format_citation_apa(self, paper: Dict, number: int) -> str:
        authors = paper.get('authors', [])
        
        if len(authors) == 0:
            author_str = "Unknown Author"
        elif len(authors) == 1:
            author_str = authors[0]
        elif len(authors) == 2:
            author_str = f"{authors[0]} & {authors[1]}"
        elif len(authors) <= 7:
            author_str = ', '.join(authors[:-1]) + f", & {authors[-1]}"
        else:
            author_str = ', '.join(authors[:6]) + ", ... " + authors[-1]
        
        year = paper.get('year', 'n.d.')
        title = paper.get('title', 'Untitled')
        venue = paper.get('venue', 'Unknown venue')
        doi = paper.get('doi', '')
        url = paper.get('url', '')
        
        citation = f"[{number}] {authors[0]} et al. ({year}). {title[:80]}... {venue or 'arXiv'}."
        
        if doi:
            citation += f" DOI:{doi}"
        elif url and "arxiv" in url.lower():
            citation += f" {url}"
        return citation
    
    def generate_bibliography(self) -> str:
        bib_lines = ["REFERENCES", "=" * 80, ""]
        for i, paper in enumerate(self.citations, 1):
            bib_lines.append(self.format_citation_apa(paper, i))
            bib_lines.append("")
        return "\n".join(bib_lines)


class FactExtractor:
    @staticmethod
    def extract_facts(paper: Dict) -> Dict:
        abstract = paper.get('abstract', '')
        title = paper.get('title', '')
        
        facts = {
            'method': FactExtractor._extract_methods(abstract, title),
            'finding': FactExtractor._extract_findings(abstract),
            'result': FactExtractor._extract_results(abstract),
            'challenge': FactExtractor._extract_challenges(abstract),
            'application': FactExtractor._extract_applications(abstract, title),
            'contribution': FactExtractor._extract_contributions(abstract),
            'architecture_details': FactExtractor._extract_architecture_details(abstract, title),
            'dataset_info': FactExtractor._extract_dataset_info(abstract),
            'training_details': FactExtractor._extract_training_details(abstract),
            'metrics_detailed': FactExtractor._extract_detailed_metrics(abstract),
            'baseline_comparison': FactExtractor._extract_baseline_comparison(abstract),
            'specific_contributions': FactExtractor._extract_specific_contributions(abstract)
        }
        return facts
    
    @staticmethod
    def _extract_methods(text: str, title: str) -> str:
        method_keywords = [
            'resnet50', 'resnet101', 'resnet152', 'resnet', 
            'vgg16', 'vgg19', 'vgg',
            'xception', 'xceptionnet',
            'efficientnet-b0', 'efficientnet-b4', 'efficientnet',
            'inception-v3', 'inceptionv3', 'inception',
            'densenet', 'mobilenet', 'squeezenet',
            'clip model', 'clip',
            'bert', 'gpt', 'transformer',
            'lstm', 'gru', 'bilstm', 'bi-lstm',
            'convolutional neural network', 'cnn',
            'recurrent neural network', 'rnn',
            'generative adversarial network', 'gan',
            'autoencoder', 'variational autoencoder', 'vae',
            'attention mechanism', 'self-attention', 'multi-head attention',
            'vision transformer', 'vit',
            'swin transformer',
            'capsule network',
            'graph neural network', 'gnn',
            'support vector machine', 'svm',
            'random forest',
            'ensemble learning', 'ensemble method',
            'transfer learning',
            'federated learning',
            'reinforcement learning',
            'contrastive learning',
            'meta-learning',
            'few-shot learning',
            'zero-shot learning',
            'supervised learning',
            'unsupervised learning',
            'semi-supervised learning',
            'active learning'
        ]
        
        text_lower = (text + ' ' + title).lower()
        found = []
        
        for kw in method_keywords:
            if kw in text_lower:
                found.append(kw)
                if len(found) >= 3:
                    break
        
        if found:
            return ', '.join(found)
        
        generic_keywords = ['deep learning', 'machine learning', 'neural network', 'algorithm']
        for kw in generic_keywords:
            if kw in text_lower:
                return kw
        
        return 'computational methodology'
    
    @staticmethod
    def _extract_architecture_details(text: str, title: str) -> str:
        combined_text = (text + ' ' + title).lower()
        details = []
        
        architectures = {
            'resnet50': 'ResNet50',
            'resnet101': 'ResNet101',
            'resnet152': 'ResNet152',
            'resnet': 'ResNet',
            'vgg16': 'VGG16',
            'vgg19': 'VGG19',
            'xception': 'Xception',
            'efficientnet': 'EfficientNet',
            'inception': 'Inception',
            'densenet': 'DenseNet',
            'mobilenet': 'MobileNet',
            'clip': 'CLIP',
            'bert': 'BERT',
            'transformer': 'Transformer',
            'lstm': 'LSTM',
            'gru': 'GRU',
            'vision transformer': 'Vision Transformer',
            'vit': 'ViT',
            'swin transformer': 'Swin Transformer'
        }
        
        found_architectures = []
        for key, name in architectures.items():
            if key in combined_text:
                found_architectures.append(name)
        
        if found_architectures:
            details.append(f"architecture: {', '.join(found_architectures[:3])}")
        
        components = {
            'attention mechanism': 'attention',
            'self-attention': 'self-attention',
            'multi-head attention': 'multi-head attention',
            'residual connection': 'residual connections',
            'skip connection': 'skip connections',
            'batch normalization': 'batch normalization',
            'dropout': 'dropout',
            'pooling': 'pooling layers',
            'max pooling': 'max pooling',
            'average pooling': 'average pooling',
            'global average pooling': 'global average pooling',
            'bottleneck': 'bottleneck layers',
            'depthwise separable': 'depthwise separable convolutions',
            'dilated convolution': 'dilated convolutions'
        }
        
        found_components = []
        for key, name in components.items():
            if key in combined_text:
                found_components.append(name)
        
        if found_components:
            details.append(f"components: {', '.join(found_components[:3])}")
        
        losses = {
            'cross-entropy': 'cross-entropy loss',
            'binary cross-entropy': 'binary cross-entropy',
            'categorical cross-entropy': 'categorical cross-entropy',
            'triplet loss': 'triplet loss',
            'contrastive loss': 'contrastive loss',
            'focal loss': 'focal loss',
            'hinge loss': 'hinge loss',
            'mean squared error': 'MSE',
            'mean absolute error': 'MAE',
            'huber loss': 'Huber loss'
        }
        
        found_losses = []
        for key, name in losses.items():
            if key in combined_text:
                found_losses.append(name)
        
        if found_losses:
            details.append(f"loss: {found_losses[0]}")
        
        optimizers = ['adam', 'sgd', 'rmsprop', 'adagrad', 'adamw']
        found_optimizers = [opt for opt in optimizers if opt in combined_text]
        if found_optimizers:
            details.append(f"optimizer: {found_optimizers[0].upper()}")
        
        if 'pre-trained' in combined_text or 'pretrained' in combined_text:
            details.append('pre-trained on ImageNet')
        
        if 'fine-tun' in combined_text:
            details.append('fine-tuned')
        
        if 'transfer learning' in combined_text:
            details.append('transfer learning')
        
        return '; '.join(details) if details else 'deep neural network architecture'
    
    @staticmethod
    def _extract_dataset_info(text: str) -> str:
        text_lower = text.lower()
        
        datasets = {
            'faceforensics++': 'FaceForensics++',
            'faceforensics': 'FaceForensics',
            'celeb-df': 'Celeb-DF',
            'celebdf': 'Celeb-DF',
            'dfdc': 'DFDC',
            'deepfake detection challenge': 'DFDC',
            'facebook deepfake detection': 'DFDC',
            'wild deepfake': 'WildDeepfake',
            'deepfake in the wild': 'DFITW',
            'imagenet': 'ImageNet',
            'coco': 'COCO',
            'cifar-10': 'CIFAR-10',
            'cifar-100': 'CIFAR-100',
            'mnist': 'MNIST',
            'fashionmnist': 'FashionMNIST',
            'vggface': 'VGGFace',
            'vggface2': 'VGGFace2',
            'lfw': 'LFW',
            'youtube faces': 'YouTube Faces',
            'kinetics': 'Kinetics',
            'ucf-101': 'UCF-101',
            'hmdb-51': 'HMDB-51'
        }
        
        found_datasets = []
        for key, name in datasets.items():
            if key in text_lower:
                found_datasets.append(name)
        
        size_info = ''
        size_patterns = [
            r'(\d+[,\s]*\d*k?\s*(?:images?|videos?|samples?|frames?|examples?))',
            r'(\d+[,\s]*\d*\s*thousand\s*(?:images?|videos?|samples?))',
            r'(\d+[,\s]*\d*\s*million\s*(?:images?|videos?|samples?))',
            r'dataset\s+(?:of|with|containing)\s+(\d+[,\s]*\d*k?\s*(?:images?|videos?|samples?))'
        ]
        
        for pattern in size_patterns:
            match = re.search(pattern, text_lower)
            if match:
                size_info = match.group(1)
                break
        
        result_parts = []
        if found_datasets:
            result_parts.append(', '.join(found_datasets[:3]))
        
        if size_info:
            result_parts.append(f"({size_info})")
        
        if result_parts:
            return ' '.join(result_parts)
        
        if 'dataset' in text_lower:
            return 'custom dataset'
        
        return 'benchmark datasets'
    
    @staticmethod
    def _extract_training_details(text: str) -> str:
        text_lower = text.lower()
        details = []
        
        epoch_match = re.search(r'(\d+)\s*epochs?', text_lower)
        if epoch_match:
            details.append(f"{epoch_match.group(1)} epochs")
        
        batch_match = re.search(r'batch\s+size\s+(?:of\s+)?(\d+)', text_lower)
        if batch_match:
            details.append(f"batch size {batch_match.group(1)}")
        
        lr_patterns = [
            r'learning\s+rate\s+(?:of\s+)?(\d+\.?\d*e?-?\d*)',
            r'lr\s*=\s*(\d+\.?\d*e?-?\d*)'
        ]
        for pattern in lr_patterns:
            lr_match = re.search(pattern, text_lower)
            if lr_match:
                details.append(f"learning rate {lr_match.group(1)}")
                break
        
        augmentation_keywords = [
            'data augmentation',
            'random crop',
            'random flip',
            'rotation',
            'color jittering',
            'mixup',
            'cutmix',
            'randaugment'
        ]
        
        found_aug = [aug for aug in augmentation_keywords if aug in text_lower]
        if found_aug:
            details.append(f"augmentation: {found_aug[0]}")
        
        if 'early stopping' in text_lower:
            details.append('early stopping')
        
        if 'learning rate schedule' in text_lower or 'lr schedule' in text_lower:
            details.append('learning rate scheduling')
        
        if 'weight decay' in text_lower:
            decay_match = re.search(r'weight\s+decay\s+(?:of\s+)?(\d+\.?\d*e?-?\d*)', text_lower)
            if decay_match:
                details.append(f"weight decay {decay_match.group(1)}")
        
        return '; '.join(details) if details else 'standard training procedure'
    
    @staticmethod
    def _extract_detailed_metrics(text: str) -> Dict[str, str]:
        metrics = {}
        
        accuracy_patterns = [
            r'accuracy\s+(?:of\s+|:\s*)?(\d+\.?\d*%?)',
            r'acc\s+(?:of\s+|:\s*)?(\d+\.?\d*%?)',
            r'achieves?\s+(\d+\.?\d*%?)\s+accuracy',
            r'(\d+\.?\d*%?)\s+accuracy'
        ]
        for pattern in accuracy_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1)
                if '%' not in value and float(value.replace('%', '')) <= 1.0:
                    value = f"{float(value) * 100:.1f}%"
                elif '%' not in value:
                    value = f"{value}%"
                metrics['accuracy'] = value
                break
        
        auc_patterns = [
            r'auc\s+(?:of\s+|:\s*)?(\d+\.?\d*)',
            r'area\s+under\s+(?:the\s+)?curve\s+(?:of\s+)?(\d+\.?\d*)',
            r'roc[-\s]auc\s+(?:of\s+)?(\d+\.?\d*)'
        ]
        for pattern in auc_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                metrics['auc'] = match.group(1)
                break
        
        f1_patterns = [
            r'f1[-\s]score\s+(?:of\s+|:\s*)?(\d+\.?\d*%?)',
            r'f1\s+(?:of\s+|:\s*)?(\d+\.?\d*%?)'
        ]
        for pattern in f1_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                metrics['f1_score'] = match.group(1)
                break
        
        precision_match = re.search(r'precision\s+(?:of\s+|:\s*)?(\d+\.?\d*%?)', text, re.IGNORECASE)
        if precision_match:
            metrics['precision'] = precision_match.group(1)
        
        recall_match = re.search(r'recall\s+(?:of\s+|:\s*)?(\d+\.?\d*%?)', text, re.IGNORECASE)
        if recall_match:
            metrics['recall'] = recall_match.group(1)
        
        return metrics
    
    @staticmethod
    def _extract_baseline_comparison(text: str) -> str:
        baselines = set()
        
        comparison_patterns = [
            r'outperform(?:s|ed|ing)?\s+([A-Z][a-zA-Z0-9-]+(?:\s+[A-Z][a-zA-Z0-9-]+)?)',
            r'compared?\s+(?:to|with|against)\s+([A-Z][a-zA-Z0-9-]+(?:\s+[A-Z][a-zA-Z0-9-]+)?)',
            r'baseline[s]?\s+(?:such as|including|like)?\s*:?\s*([A-Z][a-zA-Z0-9-]+)',
            r'(?:better|superior)\s+than\s+([A-Z][a-zA-Z0-9-]+)',
            r'vs\.?\s+([A-Z][a-zA-Z0-9-]+)',
            r'than\s+([A-Z][a-zA-Z0-9-]+(?:\s+[A-Z][a-zA-Z0-9-]+)?)\s+\(',
        ]
        
        for pattern in comparison_patterns:
            matches = re.findall(pattern, text)
            for match in matches[:5]:
                if len(match) > 2 and len(match) < 30:
                    baselines.add(match.strip())
        
        known_models = [
            'ResNet', 'ResNet50', 'ResNet101', 'VGG', 'VGG16', 'VGG19', 
            'Xception', 'XceptionNet', 'EfficientNet', 'Inception', 
            'MobileNet', 'DenseNet', 'AlexNet', 'GoogleNet',
            'LSTM', 'GRU', 'Transformer', 'BERT', 'CNN'
        ]
        
        text_context_lower = text.lower()
        if any(keyword in text_context_lower for keyword in ['compared', 'baseline', 'outperform', 'versus', 'vs']):
            for model in known_models:
                if model.lower() in text_context_lower:
                    baselines.add(model)
        
        baselines_list = list(baselines)[:5]
        
        if baselines_list:
            return ', '.join(baselines_list)
        
        if 'baseline' in text.lower() or 'compared' in text.lower():
            return 'baseline methods'
        
        return 'state-of-the-art approaches'
    
    @staticmethod
    def _extract_specific_contributions(text: str) -> str:
        text_lower = text.lower()
        contributions = []
        
        contribution_patterns = [
            r'(?:we|this paper|this work|our)\s+(?:propose|present|introduce|develop)(?:s|ed)?\s+([\w\s]{15,100})',
            r'(?:novel|new)\s+([\w\s]{10,80})\s+(?:for|to|that)',
            r'contribut(?:e|ion)[s]?\s+(?:is|are|include[s]?)?\s*([\w\s]{15,100})',
            r'main\s+contribution[s]?\s+(?:is|are|include[s]?)?\s*([\w\s]{15,100})'
        ]
        
        for pattern in contribution_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches[:2]:
                cleaned = match.strip()
                if 10 < len(cleaned) < 150:
                    contributions.append(cleaned)
        
        if not contributions:
            keywords = [
                'novel architecture', 'improved performance', 'new method',
                'enhanced accuracy', 'better generalization', 'robust detection',
                'efficient approach', 'scalable solution', 'comprehensive evaluation'
            ]
            found_keywords = [kw for kw in keywords if kw in text_lower]
            if found_keywords:
                contributions.extend(found_keywords[:2])
        
        if contributions:
            return '; '.join(contributions[:3])
        
        return 'methodological advances in the domain'
    
    @staticmethod
    def _extract_findings(text: str) -> str:
        finding_patterns = [
            r'achieve[ds]?\s+(\d+\.?\d*%)',
            r'(\d+\.?\d*%)\s+accuracy',
            r'(\d+\.?\d*%)\s+precision',
            r'improve[ds]?\s+(?:by\s+)?(\d+\.?\d*%)',
            r'outperform[s]?\s+([\w\s]{5,60})',
            r'demonstrate[ds]?\s+([\w\s]{10,80})',
            r'show[ns]?\s+that\s+([\w\s]{10,100})',
            r'found\s+that\s+([\w\s]{10,100})',
            r'reveal[s]?\s+([\w\s]{10,80})',
            r'confirm[s]?\s+([\w\s]{10,80})',
            r'(?:results?|findings?)\s+(?:show|indicate|suggest|demonstrate)\s+([\w\s]{10,100})'
        ]
        
        for pattern in finding_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                finding = match.group(0)
                if 10 < len(finding) < 200:
                    return finding[:150]
        
        if 'significant' in text.lower():
            context_match = re.search(r'significant\s+([\w\s]{10,80})', text, re.IGNORECASE)
            if context_match:
                return f"significant {context_match.group(1)}"
            return 'significant improvements in performance metrics'
        
        return 'promising results on benchmark datasets'
    
    @staticmethod
    def _extract_results(text: str) -> str:
        result_keywords = ['accuracy', 'precision', 'recall', 'f1-score', 'f1 score', 'performance', 
                          'efficiency', 'effectiveness', 'improvement', 'reduction', 'increase',
                          'throughput', 'latency', 'speed', 'scalability', 'robustness', 'auc',
                          'error rate', 'success rate']
        
        for keyword in result_keywords:
            if keyword in text.lower():
                context_start = max(0, text.lower().find(keyword) - 80)
                context_end = min(len(text), text.lower().find(keyword) + 150)
                context = text[context_start:context_end]
                
                numbers = re.findall(r'\d+\.?\d*%?', context)
                if numbers:
                    num = numbers[0]
                    if '%' not in num:
                        try:
                            float_val = float(num)
                            if float_val <= 1.0:
                                num = f"{float_val * 100:.1f}%"
                            elif float_val > 10:
                                num = f"{num}%"
                        except:
                            pass
                    
                    return f"{keyword} of {num}"
        
        general_perf = re.search(r'achiev(?:e|ed|es|ing)\s+(\d+\.?\d*%?)', text, re.IGNORECASE)
        if general_perf:
            return f"achieved {general_perf.group(1)}"
        
        return 'competitive performance on evaluation metrics'
    
    @staticmethod
    def _extract_challenges(text: str) -> str:
        challenge_keywords = ['challenge', 'limitation', 'difficulty', 'problem', 'issue', 
                             'constraint', 'bottleneck', 'gap', 'barrier', 'obstacle',
                             'drawback', 'weakness', 'shortcoming', 'fails to', 'unable to',
                             'however', 'but', 'unfortunately', 'despite']
        
        text_lower = text.lower()
        for keyword in challenge_keywords:
            if keyword in text_lower:
                idx = text_lower.find(keyword)
                context_start = max(0, idx - 20)
                context_end = min(len(text), idx + 150)
                context = text[context_start:context_end]
                
                if len(context.strip()) > 30:
                    sentences = re.split(r'[.!?]', context)
                    for sentence in sentences:
                        if keyword in sentence.lower() and len(sentence.strip()) > 20:
                            return sentence.strip()
        
        return 'challenges in generalization and robustness across diverse conditions'
    
    @staticmethod
    def _extract_applications(text: str, title: str) -> str:
        app_keywords = [
            'deepfake detection', 'face manipulation', 'face forgery',
            'healthcare', 'medical', 'clinical', 'diagnosis', 'treatment',
            'finance', 'financial', 'banking', 'trading', 'investment',
            'security', 'cybersecurity', 'privacy', 'encryption', 'authentication',
            'network', 'networking', 'communication', 'protocol',
            'iot', 'internet of things', 'sensor', 'embedded',
            'cloud', 'cloud computing', 'distributed', 'edge computing',
            '5g', '6g', 'wireless', 'mobile', 'cellular',
            'autonomous', 'robotics', 'control', 'navigation',
            'detection', 'prediction', 'classification', 'recognition',
            'manufacturing', 'industrial', 'production', 'quality control',
            'smart city', 'smart cities', 'urban', 'infrastructure',
            'transportation', 'traffic', 'vehicle', 'driving',
            'energy', 'power', 'grid', 'renewable',
            'agriculture', 'farming', 'crop', 'precision agriculture',
            'education', 'learning', 'teaching', 'e-learning',
            'social media', 'recommendation', 'personalization'
        ]
        
        combined = (text + ' ' + title).lower()
        found = []
        
        for kw in app_keywords:
            if kw in combined:
                found.append(kw)
                if len(found) >= 2:
                    break
        
        if found:
            return ', '.join(found)
        
        return 'various application domains'
    
    @staticmethod
    def _extract_contributions(text: str) -> str:
        contrib_patterns = [
            r'contribut(?:e|ion)[s]?\s+([\w\s]{15,100})',
            r'novelty\s+([\w\s]{15,100})',
            r'innovation\s+([\w\s]{15,100})',
            r'advance[s]?\s+([\w\s]{15,100})',
            r'propose[d]?\s+([\w\s]{15,100})',
            r'(?:we|this)\s+(?:present|introduce|develop)\s+([\w\s]{15,100})'
        ]
        
        for pattern in contrib_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                contrib = match.group(0)
                if 20 < len(contrib) < 150:
                    return contrib[:120]
        
        return 'novel contributions advancing the state-of-the-art'