from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class QuestionnaireService:
    """Service class for questionnaire-related operations"""
    
    # Memory issues list as class constant
    MEMORY_ISSUES = [
        "Where you put things",
        "Faces", 
        "Directions to places",
        "Appointments",
        "Losing the thread of thought in conversations",
        "Remembering things you have done (lock door, turn off the stove, etc.)",
        "Frequently used telephone numbers or addresses",
        "Knowing whether you have already told someone something",
        "Taking your medication at the scheduled time",
        "News items",
        "Date",
        "Personal events from the past",
        "Names of people",
        "Forgetting to take things with you or leaving things behind",
        "Keeping track of all parts of a task as you are performing it",
        "Remembering how to do a familiar task",
        "Repeating something you have already said to someone",
        "Carrying out a recipe",
        "Getting the details of what someone has told you mixed up",
        "Important details of what you did or what happened the day before",
        "Remembering what you just said (What was I just talking about?)",
        "Difficulty retrieving words you want to say (On the tip of the tongue)",
        "Remembering to do something you were supposed to do (phone calls, appointments, etc.)"
    ]
    
    @classmethod
    def process_memory_questionnaire_results(cls, responses: Dict) -> Dict:
        """Process memory questionnaire responses for analysis"""
        processor = MemoryQuestionnaireProcessor(responses)
        return processor.process()


class MemoryQuestionnaireProcessor:
    """Handles processing of memory questionnaire responses"""
    
    FREQUENCY_SCORES = {
        'not_at_all': 0,
        'occasionally': 1,
        'frequently': 2,
        'always': 3
    }
    
    SERIOUSNESS_SCORES = {
        'not_serious': 0,
        'somewhat_serious': 1,
        'very_serious': 2
    }
    
    def __init__(self, responses: Dict):
        self.responses = responses
        self.processed_issues = []
        self.frequency_total = 0
        self.seriousness_total = 0
        self.issues_count = 0
    
    def process(self) -> Dict:
        """Process the questionnaire responses and return analysis"""
        self._process_issues()
        self._calculate_averages()
        self._get_memory_techniques()
        self._identify_concern_areas()
        self._calculate_distributions()
        
        return {
            'processed_issues': self.processed_issues,
            'total_issues': self.issues_count,
            'frequency_total': self.frequency_total,
            'seriousness_total': self.seriousness_total,
            'avg_frequency': round(self.avg_frequency, 2),
            'avg_seriousness': round(self.avg_seriousness, 2),
            'overall_score': round(self.avg_frequency + self.avg_seriousness, 2),
            'techniques': self.techniques,
            'high_concern_issues': self.high_concern_issues,
            'moderate_concern_issues': self.moderate_concern_issues,
            'frequency_distribution': self.frequency_distribution,
            'seriousness_distribution': self.seriousness_distribution,
            'frequency_percentages': self.frequency_percentages,
            'seriousness_percentages': self.seriousness_percentages
        }
    
    def _process_issues(self):
        """Process each memory issue"""
        for i in range(1, 24):  # 23 issues total
            freq_key = f'freq_{i:02d}'
            serious_key = f'serious_{i:02d}'
            
            freq_response = self.responses.get(freq_key, '')
            serious_response = self.responses.get(serious_key, '')
            
            if freq_response and serious_response:
                freq_score = self.FREQUENCY_SCORES.get(freq_response, 0)
                serious_score = self.SERIOUSNESS_SCORES.get(serious_response, 0)
                
                issue_text = QuestionnaireService.MEMORY_ISSUES[i-1] if i-1 < len(QuestionnaireService.MEMORY_ISSUES) else f"Issue {i}"
                
                self.processed_issues.append({
                    'issue': issue_text,
                    'frequency': freq_response.replace('_', ' ').title(),
                    'frequency_score': freq_score,
                    'seriousness': serious_response.replace('_', ' ').title(),
                    'seriousness_score': serious_score,
                    'combined_score': freq_score + serious_score
                })
                
                self.frequency_total += freq_score
                self.seriousness_total += serious_score
                self.issues_count += 1
    
    def _calculate_averages(self):
        """Calculate average scores"""
        self.avg_frequency = self.frequency_total / self.issues_count if self.issues_count > 0 else 0
        self.avg_seriousness = self.seriousness_total / self.issues_count if self.issues_count > 0 else 0
    
    def _get_memory_techniques(self):
        """Extract memory techniques from responses"""
        self.techniques = []
        for i in range(1, 6):
            technique = self.responses.get(f'technique_{i}', '').strip()
            if technique:
                self.techniques.append(technique)
    
    def _identify_concern_areas(self):
        """Identify high and moderate concern areas"""
        self.high_concern_issues = [issue for issue in self.processed_issues if issue['combined_score'] >= 4]
        self.moderate_concern_issues = [issue for issue in self.processed_issues if 2 <= issue['combined_score'] < 4]
    
    def _calculate_distributions(self):
        """Calculate frequency and seriousness distributions"""
        self.frequency_distribution = {
            'not_at_all': sum(1 for issue in self.processed_issues if issue['frequency'] == 'Not At All'),
            'occasionally': sum(1 for issue in self.processed_issues if issue['frequency'] == 'Occasionally'),
            'frequently': sum(1 for issue in self.processed_issues if issue['frequency'] == 'Frequently'),
            'always': sum(1 for issue in self.processed_issues if issue['frequency'] == 'Always')
        }
        
        self.seriousness_distribution = {
            'not_serious': sum(1 for issue in self.processed_issues if issue['seriousness'] == 'Not Serious'),
            'somewhat_serious': sum(1 for issue in self.processed_issues if issue['seriousness'] == 'Somewhat Serious'),
            'very_serious': sum(1 for issue in self.processed_issues if issue['seriousness'] == 'Very Serious')
        }
        
        # Calculate percentages
        self.frequency_percentages = {
            'not_at_all': round((self.frequency_distribution['not_at_all'] / self.issues_count * 100) if self.issues_count > 0 else 0, 1),
            'occasionally': round((self.frequency_distribution['occasionally'] / self.issues_count * 100) if self.issues_count > 0 else 0, 1),
            'frequently': round((self.frequency_distribution['frequently'] / self.issues_count * 100) if self.issues_count > 0 else 0, 1),
            'always': round((self.frequency_distribution['always'] / self.issues_count * 100) if self.issues_count > 0 else 0, 1)
        }
        
        self.seriousness_percentages = {
            'not_serious': round((self.seriousness_distribution['not_serious'] / self.issues_count * 100) if self.issues_count > 0 else 0, 1),
            'somewhat_serious': round((self.seriousness_distribution['somewhat_serious'] / self.issues_count * 100) if self.issues_count > 0 else 0, 1),
            'very_serious': round((self.seriousness_distribution['very_serious'] / self.issues_count * 100) if self.issues_count > 0 else 0, 1)
        } 