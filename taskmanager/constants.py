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

# Task Status Configuration
TASK_STATUS = (
    ('assigned', 'Assigned'),
    ('in_progress', 'In Progress'),
    ('completed', 'Completed'),
    ('overdue', 'Overdue'),
)

# Task Templates Configuration - Updated for games/non-games structure
TASK_TEMPLATES = {
    # Non-game assessments
    'memory_questionnaire': {
        'template_name': 'tasks/non-games/questionnaires/take.html',
        'results_template': 'tasks/non-games/questionnaires/results.html',
    },
    'checklist': {
        'template_name': 'tasks/non-games/checklists/take.html',
        'results_template': 'tasks/non-games/checklists/results.html',
    },
    
    # Cognitive training games
    'puzzle': {
        'template_name': 'tasks/games/puzzle/take.html',
        'results_template': 'tasks/games/puzzle/results.html',
    },
    'color': {
        'template_name': 'tasks/games/color/take.html',
        'results_template': 'tasks/games/color/results.html',
    },
    'pairs': {
        'template_name': 'tasks/games/pairs/take.html',
        'results_template': 'tasks/games/pairs/results.html',
    },
} 