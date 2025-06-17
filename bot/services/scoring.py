# bot/services/scoring.py

from collections import defaultdict
from typing import List, Dict, Optional, Tuple

def calculate_scores(answers: List[List[str]]) -> Dict[str, int]:
    """
    Принимает список списков весов (каждый внутренний список —
    ключи животных для одного ответа) и возвращает словарь
    animal -> total_score.
    """
    score = defaultdict(int)
    for weight_list in answers:
        for animal in weight_list:
            score[animal] += 1
    return dict(score)

def get_top_animal(scores: Dict[str, int]) -> Optional[Tuple[str, int]]:
    """
    Из словаря scores выбирает первую пару (animal, score) с максимальным значением.
    Возвращает кортеж (animal, score) или None, если scores пуст.
    """
    if not scores:
        return None
    top_animal = max(scores.items(), key=lambda x: x[1])
    return top_animal
