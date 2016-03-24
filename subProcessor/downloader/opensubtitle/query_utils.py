from logging import getLogger

logger = getLogger()


def query_num(input_message, min_, max_):
    while True:
        try:
            print input_message
            number_input = int(raw_input())
            if min_ <= number_input <= max_:
                return number_input
        except KeyboardInterrupt:
            raise SystemExit("Aborted")
        except ValueError:
            logger.warning('Failure on processing number')


def query_yn(input_message):
    while True:
        print input_message
        try:
            input_message = raw_input().lower()
            if input_message.startswith('y'):
                return True
            elif input_message.startswith('n'):
                return False
        except KeyboardInterrupt:
            raise SystemExit("Aborted")
