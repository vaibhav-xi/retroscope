"""
RetroScope

Profiler

Measures execution time of engine systems.

Initially intended for development.

Later this can become an on-screen profiler.
"""

from time import perf_counter

class Profiler:

    def __init__(self):

        self.samples = {}
        
        self.last_report = perf_counter()

    # ---------------------------------------------------------

    def begin(self, name):

        self.samples[name] = -perf_counter()

    # ---------------------------------------------------------

    def end(self, name):

        self.samples[name] += perf_counter()

    # ---------------------------------------------------------

    def report(self):

        now = perf_counter()

        if now - self.last_report < 1.0:
            return

        self.last_report = now

        print()

        total = 0.0

        for name, value in self.samples.items():

            ms = value * 1000.0

            total += ms

            print(
                f"{name:<20} {ms:7.2f} ms"
            )

        print("-" * 32)

        print(
            f"{'Total':<20} {total:7.2f} ms"
        )