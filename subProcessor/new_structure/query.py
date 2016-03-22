def query_num(s, min_, max_):
    while True:
        print s
        try:
            n = raw_input()
        except KeyboardInterrupt:
            raise SystemExit("Aborted")
        try:
            n = int(n)
            if min_ <= n <= max_:
                return n
        except ValueError:
            pass


def query_yn(s):
    while True:
        print s
        try:
            s = raw_input().lower()
        except KeyboardInterrupt:
            raise SystemExit("Aborted")
        if s.startswith('y'):
            return True
        elif s.startswith('n'):
            return False
