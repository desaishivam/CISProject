"""
Constants and configuration for the task management system.
"""

# Task Types Configuration
TASK_TYPES = (
    ('memory_questionnaire', 'Memory Questionnaire'),
    ('checklist', 'Routine Checklist'),
    ('puzzle', 'Drag & Drop Puzzle'),
    ('color', 'Color Matching'),
    ('pairs', 'Related Pairing'),
)

# Task Categories
GAME_TYPES = ('puzzle', 'pairs', 'color')
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
        'template_name': 'tasks/non-games/checklists/take.html',
        'results_template': 'tasks/non-games/checklists/results.html',
        'icon': '📋',
        'description': 'Routine checklist of daily tasks and activities',
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
        'description': 'Drag & Drop Puzzle game',
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
    'color': {
        'template_name': 'tasks/games/color/{difficulty}/take.html',
        'results_template': 'tasks/games/color/{difficulty}/results.html',
        'icon': '🎨',
        'description': 'Color Matching game',
        'templates': {
            'mild': 'tasks/games/color/mild/take.html',
            'moderate': 'tasks/games/color/moderate/take.html',
            'major': 'tasks/games/color/major/take.html',
        },
        'results_templates': {
            'mild': 'tasks/games/color/mild/results.html',
            'moderate': 'tasks/games/color/moderate/results.html',
            'major': 'tasks/games/color/major/results.html',
        }
    },
    'pairs': {
        'template_name': 'tasks/games/pairs/{difficulty}/take.html',
        'results_template': 'tasks/games/pairs/{difficulty}/results.html',
        'icon': '🎮',
        'description': 'Related Pairing game',
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
    },
    'memory_questionnaire': {
        'template_name': 'tasks/non-games/questionnaires/take.html',
        'results_template': 'tasks/non-games/questionnaires/results.html',
        'icon': '📝',
        'description': 'Memory Questionnaire',
        'templates': {
            'default': 'tasks/non-games/questionnaires/take.html',
        },
        'results_templates': {
            'default': 'tasks/non-games/questionnaires/results.html',
        }
    },
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
    },
    'color': {
        'mild': {
            'rounds': 5,
            'time_limit': 60,
            'description': 'Basic color matching'
        },
        'moderate': {
            'rounds': 8,
            'time_limit': 90,
            'description': 'Intermediate color matching'
        },
        'major': {
            'rounds': 12,
            'time_limit': 120,
            'description': 'Advanced color matching'
        }
    },
    'memory_questionnaire': {
        'default': {
            'description': 'Memory questionnaire assessment'
        }
    },
} 