def random_string():
    import random, string
    length = 32
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))
