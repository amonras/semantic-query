import line_profiler


@line_profiler.profile
def execute():
    import jurisprudencia


if __name__ == "__main__":
    execute()
