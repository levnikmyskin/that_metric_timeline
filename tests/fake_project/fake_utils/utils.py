import random


def some_random_util(a: int, b: int):
    random.seed(42)
    return random.sample(range(a), b)
