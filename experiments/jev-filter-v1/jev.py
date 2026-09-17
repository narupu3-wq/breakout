import math


def parse_decision(response, threshold=0.6):
    if not isinstance(response, dict):
        raise ValueError('Response must be an object')
    answers = response.get('answers')
    if not isinstance(answers, dict) or not isinstance(answers.get('entry'), dict):
        raise ValueError('Missing entry answer')
    answer = answers['entry']
    if answer.get('type') != 'choice':
        raise ValueError('Expected choice answer')
    probabilities = answer.get('probabilities')
    if not isinstance(probabilities, dict) or set(probabilities) != {'allow', 'skip'}:
        raise ValueError('Expected allow/skip probabilities')
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or
           not math.isfinite(v) or not 0 <= v <= 1 for v in probabilities.values()):
        raise ValueError('Invalid probability')
    if not math.isclose(sum(probabilities.values()), 1.0, abs_tol=1e-6):
        raise ValueError('Probabilities must sum to one')
    choice = answer.get('choice')
    if not isinstance(choice, str) or choice not in probabilities:
        raise ValueError('Invalid choice')
    if probabilities[choice] < max(probabilities.values()):
        raise ValueError('Invalid choice')
    return choice == 'allow' and probabilities['allow'] >= threshold
