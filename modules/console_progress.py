from pandas import DataFrame


def progress_bar(iterable, prefix='Progress: ', suffix='Complete', decimals=1, length=50, fill='█', print_end='\r'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        print_end    - Optional  : end character (e.g. '\r', '\r\n') (Str)
    """
    total = len(iterable)

    # Progress Bar Printing Function
    def print_progress_bar(iteration):
        percent = ('{0:.' + str(decimals) + 'f}').format(100 * (iteration / float(total)))
        filled_length = int(length * iteration // total)
        bar = fill * filled_length + '-' * (length - filled_length)
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=print_end)

    # Initial Call
    print_progress_bar(0)
    # Update Progress Bar
    if isinstance(iterable, DataFrame):
        for i, item in enumerate(iterable.itertuples()):
            yield item
            print_progress_bar(i + 1)
        # Print New Line on Complete
    else:
        for i, item in enumerate(iterable):
            yield item
            print_progress_bar(i + 1)
        # Print New Line on Complete
    print()
