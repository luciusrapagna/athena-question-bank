from pathlib import Path

ATHENA_ROOT = Path(__file__).resolve().parents[1]
MODULES_ROOT = ATHENA_ROOT / 'modules'

REGISTERED_MODULES = {
    'athena_question_bank': {
        'name': 'ATHENA QUESTION BANK',
        'path': MODULES_ROOT / 'athena_question_bank',
        'status': 'integrated',
        'version': 'v1.0.0-mvp'
    },
    'athena_writing': {
        'name': 'ATHENA WRITING',
        'path': MODULES_ROOT / 'athena_writing',
        'status': 'planned',
        'version': None
    },
    'athena_exam_analytics': {
        'name': 'ATHENA EXAM ANALYTICS',
        'path': MODULES_ROOT / 'athena_exam_analytics',
        'status': 'planned',
        'version': None
    },
    'athena_intelligence': {
        'name': 'ATHENA INTELLIGENCE',
        'path': MODULES_ROOT / 'athena_intelligence',
        'status': 'planned',
        'version': None
    },
    'athena_sciences': {
        'name': 'ATHENA SCIENCES',
        'path': MODULES_ROOT / 'athena_sciences',
        'status': 'planned',
        'version': None
    },
}
