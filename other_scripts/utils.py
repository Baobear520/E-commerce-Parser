import time


def runtime_counter(func):
    """A decorator for checking script's runtime"""

    def wrapper(*args, **kwargs):
        start_time = time.time()
        func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time

        # Convert to hours, minutes, seconds, and milliseconds
        hours = int(elapsed_time // 3600)
        minutes = int((elapsed_time % 3600) // 60)
        seconds = int(elapsed_time % 60)
        milliseconds = int((elapsed_time % 1) * 1000)

        # Display runtime
        print(f"Runtime: {hours:02}:{minutes:02}:{seconds:02}:{milliseconds:03}")
    return wrapper
