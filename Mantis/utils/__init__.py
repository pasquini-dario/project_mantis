import random

def uniform_random_natural(expected_value):
    N = int(2 * expected_value - 1)
    return random.randint(1, N)


def generate_random_date(seed=None):
    if seed:
        random.seed(seed)
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    month = random.choice(months)
    day = random.randint(1, 30)
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)    
    date_string = f"{month} {day:02} {hour:02}:{minute:02}"
    return date_string