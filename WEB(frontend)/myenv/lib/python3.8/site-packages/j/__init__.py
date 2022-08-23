#!/usr/bin/env python3
"""
Simple pipeline json parser

It is as jq but better because you can use python syntax and you do not need
to look in documentation every time.
"""

import json
import sys

from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import JsonLexer

__version__ = '1.0.4'


def process(it, args):
    indent = None if args.is_compact else 4
    if not args.cmd:
        dump = json.dumps(it, sort_keys=True, indent=indent)
        output = highlight(dump, JsonLexer(), TerminalFormatter())
        print(output, end='')
        return

    globs = globals()
    locs = locals()
    print(
        highlight(
            json.dumps(
                eval(args.cmd, globs, locs),
                sort_keys=True,
                indent=indent
            ),
            JsonLexer(),
            TerminalFormatter()
        ),
        end=''
    )


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="""This is simple json parser.
        Just pipe valid json to it and it will print nicely.
        You can also modify json by passing expression as an argument
        (json is accessed by `it` keyword).
        """
    )
    parser.add_argument(
        '-c', dest='is_compact',
        action='store_true',
        help='output compact'
    )
    parser.add_argument(
        'cmd',
        nargs='?',
        help='expression (e.g. | j "{str(v):k for k, v in it.items()}")'
    )
    args = parser.parse_args()

    try:
        stdin = sys.stdin.read()
        it = json.loads(stdin)
        process(it, args)
    except json.decoder.JSONDecodeError:
        its = [json.loads(line.strip())
               for line in stdin.split('\n') if line.strip()]
        for it in its:
            process(it, args)


if __name__ == '__main__':
    main()
