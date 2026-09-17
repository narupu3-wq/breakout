import argparse
import json
import sys

from jev import parse_decision


def main():
    parser = argparse.ArgumentParser(description='Parse a supplied Jev response without API calls.')
    parser.add_argument('response', nargs='?', default='-', help='JSON file, or - for stdin')
    args = parser.parse_args()
    try:
        if args.response == '-':
            response = json.load(sys.stdin)
        else:
            with open(args.response, encoding='utf-8') as source:
                response = json.load(source)
        allowed = parse_decision(response)
    except (OSError, ValueError, TypeError) as exc:
        parser.exit(2, 'Invalid response: {}\n'.format(exc))
    print(json.dumps({'decision': 'allow' if allowed else 'skip'}))


if __name__ == '__main__':
    main()
