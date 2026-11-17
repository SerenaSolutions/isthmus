# -*- coding: utf-8 -*-
"""CLI minima: decide e verify, com recibo selado."""
import argparse, json, sys
from . import receipt as R
from .errors import Refusal


def _decide(args):
    p0 = args.p0
    verdict = 1 if abs(p0 - 0.5) > args.error_bound else 0
    rec = R.build(p0=p0, n=args.n, shots=args.shots, seed=args.seed, mode="sim",
                  error_bound=args.error_bound, verdict=verdict)
    print(json.dumps(rec, indent=2, ensure_ascii=False))
    return 0


def _verify(args):
    with open(args.path, encoding="utf-8") as fh:
        rec = json.load(fh)
    try:
        print(json.dumps(R.verify(rec), ensure_ascii=False))
        return 0
    except Refusal as e:
        print(json.dumps({"state": "refused", "code": e.code, "detail": e.detail}, ensure_ascii=False))
        return 1


def main(argv=None):
    ap = argparse.ArgumentParser(prog="isthmus")
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("decide")
    d.add_argument("--p0", type=float, default=0.9)
    d.add_argument("--n", type=int, default=4)
    d.add_argument("--shots", type=int, default=512)
    d.add_argument("--seed", type=int, default=1)
    d.add_argument("--error-bound", type=float, default=0.05)
    v = sub.add_parser("verify")
    v.add_argument("path")
    a = ap.parse_args(argv)
    return _decide(a) if a.cmd == "decide" else _verify(a)


if __name__ == "__main__":
    sys.exit(main())
