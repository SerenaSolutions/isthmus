# -*- coding: utf-8 -*-
"""CLI da STH: seal, verify e chain."""
import argparse, json, sys
from . import sth
from .errors import Refusal


def main(argv=None):
    ap = argparse.ArgumentParser(prog="sth")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("seal"); s.add_argument("path")
    v = sub.add_parser("verify"); v.add_argument("path")
    c = sub.add_parser("chain"); c.add_argument("paths", nargs="+")
    d = sub.add_parser("decide")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "seal":
            payload = json.load(open(a.path, encoding="utf-8"))
            print(json.dumps(sth.seal(payload), ensure_ascii=False)); return 0
        if a.cmd == "verify":
            print(json.dumps(sth.verify(json.load(open(a.path, encoding="utf-8"))), ensure_ascii=False)); return 0
        if a.cmd == "chain":
            recs = [json.load(open(p, encoding="utf-8")) for p in a.paths]
            print(json.dumps(sth.chain(recs), ensure_ascii=False)); return 0
        sth.decide()
    except Refusal as e:
        print(json.dumps({"state": "refused", "code": e.code, "detail": e.detail}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    sys.exit(main())
