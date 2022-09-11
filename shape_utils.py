import random


def generate_random_html_color() -> str:
    return '#%02X%02X%02X' % (__rand_channel_val(), __rand_channel_val(), __rand_channel_val())


def __rand_channel_val():
    return random.randint(0, 255)
