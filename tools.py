import pstats
from cProfile import Profile


def profile(func):

    def inner(*args, **wargs):
        profiler = Profile()

        profiler.enable()
        result = func(*args, **wargs)
        profiler.disable()

        stats = pstats.Stats(profiler).sort_stats('cumulative')
        stats.print_stats()

        return result

    return inner
