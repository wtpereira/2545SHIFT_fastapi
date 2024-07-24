import __main__

def f(x):
    print(__main__)
    print("Ah não, você não vai!")

__main__.sys.exit = f