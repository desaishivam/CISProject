"""
Constants and configuration for the task management system.
"""

# Task Types Configuration
TASK_TYPES = (
    ('memory_questionnaire', 'Memory Questionnaire'),
    ('checklist', 'Daily Checklist'),
    ('puzzle', 'Memory Puzzle'),
    ('color', 'Color Game'),
    ('pairs', 'Pairs Game'),
)

# Task Categories
GAME_TYPES = ('puzzle', 'pairs')
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
)

# Task Templates Configuration - Updated for games/non-games structure
TASK_TEMPLATES = {
    'checklist': {
        'template_name': 'tasks/checklist/take.html',
        'results_template': 'tasks/checklist/results.html',
        'icon': '📋',
        'description': 'Daily tasks and activities checklist',
        'templates': {
            'mild': 'tasks/checklist/mild/take.html',
            'moderate': 'tasks/checklist/moderate/take.html',
            'major': 'tasks/checklist/major/take.html',
        },
        'results_templates': {
            'mild': 'tasks/checklist/mild/results.html',
            'moderate': 'tasks/checklist/moderate/results.html',
            'major': 'tasks/checklist/major/results.html',
        }
    },
    'puzzle': {
        'template_name': 'tasks/games/puzzle/{difficulty}/take.html',
        'results_template': 'tasks/games/puzzle/{difficulty}/results.html',
        'icon': '🧩',
        'description': 'Memory puzzle game',
        'templates': {
            'mild': 'tasks/games/puzzle/mild/take.html',
            'moderate': 'tasks/games/puzzle/moderate/take.html',
            'major': 'tasks/games/puzzle/major/take.html',
        },
        'results_templates': {
            'mild': 'tasks/games/puzzle/mild/results.html',
            'moderate': 'tasks/games/puzzle/moderate/results.html',
            'major': 'tasks/games/puzzle/major/results.html',
        }
    },
    'pairs': {
        'template_name': 'tasks/games/pairs/{difficulty}/take.html',
        'results_template': 'tasks/games/pairs/{difficulty}/results.html',
        'icon': '🎮',
        'description': 'Memory pairs matching game',
        'templates': {
            'mild': 'tasks/games/pairs/mild/take.html',
            'moderate': 'tasks/games/pairs/moderate/take.html',
            'major': 'tasks/games/pairs/major/take.html',
        },
        'results_templates': {
            'mild': 'tasks/games/pairs/mild/results.html',
            'moderate': 'tasks/games/pairs/moderate/results.html',
            'major': 'tasks/games/pairs/major/results.html',
        }
    }
}

# Difficulty Configurations for Future Development
DIFFICULTY_CONFIGS = {
    'checklist': {
        'mild': {
            'tasks': 5,
            'time_limit': None,
            'description': 'Basic daily tasks'
        },
        'moderate': {
            'tasks': 7,
            'time_limit': None,
            'description': 'Extended daily tasks'
        },
        'major': {
            'tasks': 10,
            'time_limit': None,
            'description': 'Comprehensive daily tasks'
        }
    },
    'puzzle': {
        'mild': {
            'grid': '3x3',
            'time_limit': 300,
            'description': 'Simple 3x3 grid puzzle'
        },
        'moderate': {
            'grid': '4x4',
            'time_limit': 600,
            'description': 'Medium 4x4 grid puzzle'
        },
        'major': {
            'grid': '5x5',
            'time_limit': 900,
            'description': 'Complex 5x5 grid puzzle'
        }
    },
    'pairs': {
        'mild': {
            'pairs': 6,
            'time_limit': None,
            'description': 'Basic pairs matching'
        },
        'moderate': {
            'pairs': 8,
            'time_limit': None,
            'description': 'Extended pairs matching'
        },
        'major': {
            'pairs': 10,
            'time_limit': None,
            'description': 'Complex pairs matching'
        }
    }
} 