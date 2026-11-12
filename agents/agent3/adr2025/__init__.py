from . import class3, class61, class8, class9

MODULES = {'3': class3.evaluate, '6.1': class61.evaluate, '8': class8.evaluate, '9': class9.evaluate}

def evaluate_class(hazard_class, evidence):
    if hazard_class not in MODULES:
        raise ValueError('Unsupported hazard class (only 3, 6.1, 8, 9)')
    if type(evidence) is not dict:
        raise TypeError('evidence must be a dict')
    return MODULES[hazard_class](evidence)