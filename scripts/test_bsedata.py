"""Small smoke test for the `bsedata` package.

Usage:
    python scripts/test_bsedata.py
    python scripts/test_bsedata.py --code 500325

This checks that:
1. `bsedata` imports
2. `BSE()` instantiates
3. A stock quote can be fetched
4. Top gainers/losers endpoints respond
5. Indices and scrip-code helpers respond
"""

from __future__ import annotations

import argparse
import sys
from pprint import pprint


def run_smoke_test(code: str) -> int:
    try:
        from bsedata.bse import BSE
    except ImportError as exc:
        print("FAIL import: `bsedata` is not installed in this environment.")
        print("Install it with: pip install bsedata")
        print(f"Import error: {exc}")
        return 1

    failures = 0

    try:
        bse = BSE()
        print("PASS init: created BSE() client")
    except Exception as exc:
        print(f"FAIL init: could not create BSE() client: {exc}")
        return 1

    try:
        quote = bse.getQuote(code)
        company = quote.get("companyName", "<missing>")
        price = quote.get("currentValue", "<missing>")
        updated = quote.get("updatedOn", "<missing>")
        print(f"PASS getQuote: {code} -> {company} | price={price} | updated={updated}")
    except Exception as exc:
        failures += 1
        print(f"FAIL getQuote({code}): {exc}")

    try:
        gainers = bse.topGainers()
        first = gainers[0] if gainers else None
        print(f"PASS topGainers: received {len(gainers)} rows")
        if first:
            pprint(first)
    except Exception as exc:
        failures += 1
        print(f"FAIL topGainers: {exc}")

    try:
        losers = bse.topLosers()
        first = losers[0] if losers else None
        print(f"PASS topLosers: received {len(losers)} rows")
        if first:
            pprint(first)
    except Exception as exc:
        failures += 1
        print(f"FAIL topLosers: {exc}")

    try:
        indices = bse.getIndices()
        sample = indices[0] if indices else None
        print(f"PASS getIndices: received {len(indices)} rows")
        if sample:
            pprint(sample)
    except Exception as exc:
        failures += 1
        print(f"FAIL getIndices: {exc}")

    try:
        verified = bse.verifyScripCode(code)
        print(f"PASS verifyScripCode: {code} -> {verified}")
    except Exception as exc:
        failures += 1
        print(f"FAIL verifyScripCode({code}): {exc}")

    try:
        scrip_codes = bse.getScripCodes()
        print(f"PASS getScripCodes: received {len(scrip_codes)} codes")
        if code in scrip_codes:
            print(f"Found {code} in scrip-code map: {scrip_codes[code]}")
    except Exception as exc:
        failures += 1
        print(f"FAIL getScripCodes: {exc}")

    if failures:
        print(f"\nCompleted with {failures} failing check(s).")
        return 1

    print("\nAll bsedata smoke checks passed.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke-test the bsedata library.")
    parser.add_argument(
        "--code",
        default="500325",
        help="BSE scrip code to test with (default: 500325).",
    )
    args = parser.parse_args()
    return run_smoke_test(args.code)


if __name__ == "__main__":
    sys.exit(main())
