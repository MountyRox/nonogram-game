TIME_DURATION_UNITS = (
    ('week', 60*60*24*7),
    ('day', 60*60*24),
    ('hour', 60*60),
    ('min', 60),
    ('sec', 1)
)


def human_time_duration(seconds):
    if seconds == 0:
        return '0 s'
    if seconds <= 10.0:
        if seconds < 0.01:
            return f'{seconds*1000: .3f} ms'
        return f'{seconds: .3f} sec'
    parts = []
    for unit, div in TIME_DURATION_UNITS:
        amount, seconds = divmod(int(seconds), div)
        if amount > 0:
            parts.append('{} {}{}'.format(amount, unit, "" if amount == 1 else "s"))
    return ', '.join(parts)


if __name__ == "__main__":

    num = 3.14159
    print(f"The valueof pi is: {num:{1}.{3}}")

    print (human_time_duration (num*10))
    print (f'{2:>3}. Row')    
    print (f'{12:>3}. Row')