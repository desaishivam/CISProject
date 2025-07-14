# Constants to use throughout the app

# Task Types Configuration
TASK_TYPES = (
    ('memory_questionnaire', 'Memory Questionnaire'),
    ('puzzle', 'Drag & Drop Puzzle'),
    ('color', 'Color Matching'),
    ('pairs', 'Related Pairing'),
)

# Task Categories
GAME_TYPES = ('puzzle', 'pairs', 'color')
ASSESSMENT_TYPES = ('memory_questionnaire',)

# Difficulty Levels for Games
DIFFICULTY_LEVELS = (
    ('hard', 'Hard'),
    ('medium', 'Medium'), 
    ('easy', 'Easy'),
)

# Task Status Config
TASK_STATUS = (
    ('assigned', 'Assigned'),
    ('in_progress', 'In Progress'),
    ('completed', 'Completed'),
)

# Task Templates Configuration
TASK_TEMPLATES = {
    'puzzle': {
        'template_name': 'tasks/games/puzzle/{difficulty}/take.html',
        'results_template': 'tasks/games/puzzle/{difficulty}/results.html',
        'icon': '🧩',
        'description': 'Drag & Drop Puzzle game',
        'templates': {
            'hard': 'tasks/games/puzzle/hard/take.html',
            'medium': 'tasks/games/puzzle/medium/take.html',
            'easy': 'tasks/games/puzzle/easy/take.html',
        },
        'results_templates': {
            'hard': 'tasks/games/puzzle/hard/results.html',
            'medium': 'tasks/games/puzzle/medium/results.html',
            'easy': 'tasks/games/puzzle/easy/results.html',
        }
    },
    'color': {
        'template_name': 'tasks/games/color/{difficulty}/take.html',
        'results_template': 'tasks/games/color/{difficulty}/results.html',
        'icon': '🎨',
        'description': 'Color Matching game',
        'templates': {
            'hard': 'tasks/games/color/hard/take.html',
            'medium': 'tasks/games/color/medium/take.html',
            'easy': 'tasks/games/color/easy/take.html',
        },
        'results_templates': {
            'hard': 'tasks/games/color/hard/results.html',
            'medium': 'tasks/games/color/medium/results.html',
            'easy': 'tasks/games/color/easy/results.html',
        }
    },
    'pairs': {
        'template_name': 'tasks/games/pairs/{difficulty}/take.html',
        'results_template': 'tasks/games/pairs/{difficulty}/results.html',
        'icon': '🎮',
        'description': 'Related Pairing game',
        'templates': {
            'hard': 'tasks/games/pairs/hard/take.html',
            'medium': 'tasks/games/pairs/medium/take.html',
            'easy': 'tasks/games/pairs/easy/take.html',
        },
        'results_templates': {
            'hard': 'tasks/games/pairs/hard/results.html',
            'medium': 'tasks/games/pairs/medium/results.html',
            'easy': 'tasks/games/pairs/easy/results.html',
        }
    },
    'memory_questionnaire': {
        'template_name': 'tasks/non-games/questionnaires/take.html',
        'results_template': 'tasks/non-games/questionnaires/results.html',
        'icon': '📝',
        'description': 'Memory Questionnaire'
    },
}

# Difficulty Configurations
DIFFICULTY_CONFIGS = {
    'puzzle': {
        'hard': {
            'grid': '3x3',
            'time_limit': 300,
            'description': 'Simple 3x3 grid puzzle'
        },
        'medium': {
            'grid': '4x4',
            'time_limit': 600,
            'description': 'Medium 4x4 grid puzzle'
        },
        'easy': {
            'grid': '5x5',
            'time_limit': 900,
            'description': 'Complex 5x5 grid puzzle'
        }
    },
    'pairs': {
        'hard': {
            'pairs': 6,
            'time_limit': None,
            'description': 'Basic pairs matching'
        },
        'medium': {
            'pairs': 8,
            'time_limit': None,
            'description': 'Extended pairs matching'
        },
        'easy': {
            'pairs': 10,
            'time_limit': None,
            'description': 'Complex pairs matching'
        }
    },
    'color': {
        'hard': {
            'rounds': 5,
            'time_limit': 60,
            'description': 'Basic color matching'
        },
        'medium': {
            'rounds': 8,
            'time_limit': 90,
            'description': 'Intermediate color matching'
        },
        'easy': {
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