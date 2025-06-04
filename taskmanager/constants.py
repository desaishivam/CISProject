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

# Task Status Configuration
TASK_STATUS = (
    ('assigned', 'Assigned'),
    ('in_progress', 'In Progress'),
    ('completed', 'Completed'),
    ('overdue', 'Overdue'),
)

# Task Templates Configuration
TASK_TEMPLATES = {
    'memory_questionnaire': {
        'template_name': 'tasks/questionnaires/take.html',
        'results_template': 'tasks/questionnaires/results.html',
    },
    'checklist': {
        'template_name': 'tasks/checklists/take.html',
        'results_template': 'tasks/checklists/results.html',
    },
    'puzzle': {
        'template_name': 'tasks/puzzle/take.html',
        'results_template': 'tasks/puzzle/results.html',
    },
    'color': {
        'template_name': 'tasks/color/take.html',
        'results_template': 'tasks/color/results.html',
    },
    'pairs': {
        'template_name': 'tasks/pairs/take.html',
        'results_template': 'tasks/pairs/results.html',
    },
} 