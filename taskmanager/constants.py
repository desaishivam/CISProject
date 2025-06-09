"""
Constants and configuration for the task management system.
"""

# Task Types Configuration
TASK_TYPES = (
    ('memory_questionnaire', 'Memory Questionnaire'),
    ('checklist', 'Checklist'),
    ('puzzle', 'Memory Puzzle'),
    ('color', 'Color Matching'),
    ('pairs', 'Pairs Game'),
)

# Task Categories
GAME_TYPES = ('puzzle', 'color', 'pairs')
ASSESSMENT_TYPES = ('memory_questionnaire', 'checklist')

# Difficulty Levels for Games
DIFFICULTY_LEVELS = (
    ('mild', 'Mild'),
    ('moderate', 'Moderate'), 
    ('major', 'Major'),
)

# Task Status Configuration
TASK_STATUS = (
    ('assigned', 'Assigned'),
    ('in_progress', 'In Progress'),
    ('completed', 'Completed'),
    ('overdue', 'Overdue'),
)

# Task Templates Configuration - Updated for games/non-games structure
TASK_TEMPLATES = {
    # Non-game assessments (no difficulty levels)
    'memory_questionnaire': {
        'template_name': 'tasks/non-games/questionnaires/take.html',
        'results_template': 'tasks/non-games/questionnaires/results.html',
        'has_difficulty': False,
    },
    'checklist': {
        'template_name': 'tasks/non-games/checklists/take.html',
        'results_template': 'tasks/non-games/checklists/results.html',
        'has_difficulty': False,
    },
    
    # Cognitive training games (with difficulty levels)
    'puzzle': {
        'template_name': 'tasks/games/puzzle/take.html',
        'results_template': 'tasks/games/puzzle/results.html',
        'has_difficulty': True,
        'default_difficulty': 'mild',
        'description': 'Memory categorization puzzle game',
    },
    'color': {
        'template_name': 'tasks/games/color/{difficulty}/take.html',
        'results_template': 'tasks/games/color/{difficulty}/results.html',
        'has_difficulty': True,
        'default_difficulty': 'mild',
        'description': 'Color sequence matching game',
        'difficulty_templates': {
            'mild': 'tasks/games/color/mild/take.html',
            'moderate': 'tasks/games/color/moderate/take.html',
            'major': 'tasks/games/color/major/take.html',
        },
        'difficulty_results': {
            'mild': 'tasks/games/color/mild/results.html',
            'moderate': 'tasks/games/color/moderate/results.html',
            'major': 'tasks/games/color/major/results.html',
        }
    },
    'pairs': {
        'template_name': 'tasks/games/pairs/take.html',
        'results_template': 'tasks/games/pairs/results.html',
        'has_difficulty': True,
        'default_difficulty': 'mild',
        'description': 'Memory pairs matching game',
    },
}

# Difficulty Configurations for Future Development
DIFFICULTY_CONFIGS = {
    'puzzle': {
        'mild': {
            'word_count': 10,
            'categories': 3,
            'time_limit': None,
            'description': 'Basic categorization with familiar words'
        },
        'moderate': {
            'word_count': 15,
            'categories': 4,
            'time_limit': 300,  # 5 minutes
            'description': 'More words and categories with time pressure'
        },
        'major': {
            'word_count': 20,
            'categories': 5,
            'time_limit': 180,  # 3 minutes
            'description': 'Advanced categorization with complex words'
        }
    },
    'color': {
        'mild': {
            'sequence_length': 3,
            'colors': 4,
            'speed': 'slow',
            'description': 'Short sequences with basic colors'
        },
        'moderate': {
            'sequence_length': 5,
            'colors': 6,
            'speed': 'medium',
            'description': 'Longer sequences with more colors'
        },
        'major': {
            'sequence_length': 8,
            'colors': 8,
            'speed': 'fast',
            'description': 'Complex sequences requiring sustained attention'
        }
    },
    'pairs': {
        'mild': {
            'pairs_count': 6,
            'flip_time': 2000,  # 2 seconds
            'description': 'Basic memory matching with longer view time'
        },
        'moderate': {
            'pairs_count': 8,
            'flip_time': 1500,  # 1.5 seconds
            'description': 'More pairs with moderate timing'
        },
        'major': {
            'pairs_count': 12,
            'flip_time': 1000,  # 1 second
            'description': 'Challenging memory test with quick timing'
        }
    }
} 