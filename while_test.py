import timeout

@timeout.timeout(10)
def test():
    while True:
        pass

test()