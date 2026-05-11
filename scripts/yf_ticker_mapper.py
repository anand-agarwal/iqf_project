# """
# Yahoo Finance Screener — Indian MF Ticker Scraper (Fixed)
# ==========================================================
# Fixes:
#   - Proper browser headers + cookie consent handling
#   - Retry logic with backoff for rate limits
#   - Longer delays between requests
#   - Uses query1 fallback if query2 fails

# Usage:
#     pip install requests
#     python yf_screener_raw.py
# """

# import requests
# import json
# import time
# import re
# import random
# from datetime import datetime

# OUTPUT_FILE = "indian_mf_tickers.json"
# BATCH_SIZE  = 250
# INDIAN_MF_PATTERN = re.compile(r'^0P[0-9A-Z]+\.(BO|NS)$')

# SESSION = requests.Session()
# SESSION.headers.update({
#     "User-Agent": (
#         "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
#         "AppleWebKit/537.36 (KHTML, like Gecko) "
#         "Chrome/124.0.0.0 Safari/537.36"
#     ),
#     "Accept": "*/*",
#     "Accept-Language": "en-US,en;q=0.9",
#     "Accept-Encoding": "gzip, deflate, br",
#     "Connection": "keep-alive",
#     "Sec-Fetch-Dest": "empty",
#     "Sec-Fetch-Mode": "cors",
#     "Sec-Fetch-Site": "same-site",
# })


# def warm_up_session():
#     """Visit Yahoo Finance pages to build a proper session with cookies."""
#     print("  Warming up session (visiting Yahoo Finance)...")
#     urls = [
#         "https://finance.yahoo.com/",
#         "https://finance.yahoo.com/research-hub/screener/mutualfunds/",
#     ]
#     for url in urls:
#         try:
#             r = SESSION.get(url, timeout=20)
#             print(f"  GET {url[:55]} -> {r.status_code}")
#             time.sleep(random.uniform(2, 4))
#         except Exception as e:
#             print(f"  Warning: {e}")

#     cookies = {c.name: c.value for c in SESSION.cookies}
#     print(f"  Cookies acquired: {list(cookies.keys())}")


# def get_crumb(max_retries=5) -> str:
#     """Get Yahoo Finance API crumb with retries."""
#     crumb_urls = [
#         "https://query1.finance.yahoo.com/v1/test/getcrumb",
#         "https://query2.finance.yahoo.com/v1/test/getcrumb",
#     ]

#     for attempt in range(max_retries):
#         for url in crumb_urls:
#             try:
#                 r = SESSION.get(url, timeout=15)
#                 if r.status_code == 429:
#                     wait = (2 ** attempt) + random.uniform(1, 3)
#                     print(f"  Rate limited on crumb. Waiting {wait:.0f}s...")
#                     time.sleep(wait)
#                     continue
#                 if r.status_code == 200:
#                     crumb = r.text.strip()
#                     if crumb and "<" not in crumb and len(crumb) < 50:
#                         print(f"  Crumb: {crumb!r}")
#                         return crumb
#                     print(f"  Bad crumb response: {crumb[:80]!r}")
#             except Exception as e:
#                 print(f"  Error on {url}: {e}")

#         wait = (2 ** attempt) + random.uniform(2, 5)
#         print(f"  Attempt {attempt+1}/{max_retries} failed. Retrying in {wait:.0f}s...")
#         time.sleep(wait)

#     raise RuntimeError("Could not get crumb after all retries.")


# def fetch_batch(crumb: str, offset: int, max_retries=4) -> dict:
#     """Fetch one page with retry on rate limit."""
#     hosts = ["query1.finance.yahoo.com", "query2.finance.yahoo.com"]

#     for attempt in range(max_retries):
#         host = hosts[attempt % 2]
#         url = f"https://{host}/v1/finance/screener"
#         params = {
#             "crumb": crumb,
#             "lang": "en-US",
#             "region": "US",
#             "formatted": "false",
#         }
#         payload = {
#             "offset": offset,
#             "size": BATCH_SIZE,
#             "sortField": "fundnetassets",
#             "sortType": "DESC",
#             "quoteType": "MUTUALFUND",
#             "topOperator": "AND",
#             "query": {"operator": "AND", "operands": []},
#             "userId": "",
#             "userIdType": "guid",
#         }

#         try:
#             r = SESSION.post(url, params=params, json=payload, timeout=30)
#             if r.status_code == 429:
#                 wait = (2 ** attempt) * 5 + random.uniform(2, 5)
#                 print(f"\n  Rate limited at offset {offset}. Waiting {wait:.0f}s...")
#                 time.sleep(wait)
#                 continue
#             r.raise_for_status()
#             return r.json()
#         except requests.HTTPError as e:
#             if attempt == max_retries - 1:
#                 raise
#             wait = (2 ** attempt) * 3
#             print(f"\n  HTTP {e.response.status_code} at offset {offset}. Retry in {wait}s...")
#             time.sleep(wait)
#         except Exception as e:
#             if attempt == max_retries - 1:
#                 raise
#             time.sleep(5)

#     raise RuntimeError(f"Failed to fetch offset {offset}")


# def scrape_all(crumb: str) -> list[dict]:
#     all_quotes = []
#     offset = 0
#     total = None

#     while True:
#         print(f"  Batch offset={offset:5d}", end="  ", flush=True)
#         data = fetch_batch(crumb, offset)

#         result = data.get("finance", {}).get("result") or []
#         if not result:
#             error = data.get("finance", {}).get("error")
#             print(f"No result. Error: {error}")
#             break

#         sr = result[0]
#         if total is None:
#             total = sr.get("total", 0)
#             print(f"(Total in screener: {total})")

#         quotes = sr.get("quotes", [])
#         print(f"-> {len(quotes)} funds | cumulative: {len(all_quotes) + len(quotes)}")

#         if not quotes:
#             break

#         all_quotes.extend(quotes)
#         offset += len(quotes)

#         if offset >= total:
#             break

#         time.sleep(random.uniform(1.5, 3.0))

#     return all_quotes


# def main():
#     print("=" * 60)
#     print("Yahoo Finance Screener - Indian MF Ticker Scraper")
#     print("=" * 60)

#     print("\n[1/4] Building browser session...")
#     warm_up_session()

#     print("\n[2/4] Getting API crumb...")
#     try:
#         crumb = get_crumb()
#     except RuntimeError as e:
#         print(f"\nFAILED: {e}")
#         print("\nYahoo Finance is rate-limiting your IP.")
#         print("Wait 15-30 minutes, or try on a different network/VPN.")
#         return

#     print("\n[3/4] Fetching all mutual funds from screener...")
#     try:
#         all_quotes = scrape_all(crumb)
#     except Exception as e:
#         print(f"\nError during scraping: {e}")
#         return

#     print(f"\n  Total fetched: {len(all_quotes)}")

#     print("\n[4/4] Filtering to Indian funds (0P*.BO / 0P*.NS)...")
#     indian = []
#     for q in all_quotes:
#         sym = q.get("symbol", "")
#         if INDIAN_MF_PATTERN.match(sym):
#             indian.append({
#                 "yahooTicker":        sym,
#                 "name":               q.get("longName") or q.get("shortName", ""),
#                 "exchange":           q.get("exchange", ""),
#                 "currency":           q.get("currency", ""),
#                 "category":           q.get("category", ""),
#                 "fundFamily":         q.get("fundFamily", ""),
#                 "netAssets":          q.get("netAssets"),
#                 "ytdReturn":          q.get("ytdReturn"),
#                 "threeYearAvgReturn": q.get("threeYearAverageReturn"),
#                 "fiveYearAvgReturn":  q.get("fiveYearAverageReturn"),
#             })

#     print(f"  Indian MFs: {len(indian)} / {len(all_quotes)} total")

#     output = {
#         "generated_at": datetime.now().isoformat(),
#         "total_indian_funds": len(indian),
#         "funds": sorted(indian, key=lambda x: x["name"]),
#     }
#     with open(OUTPUT_FILE, "w") as f:
#         json.dump(output, f, indent=2)

#     print(f"\n  Saved -> {OUTPUT_FILE}")
#     print("\nSample:")
#     for f in indian[:10]:
#         print(f"  {f['yahooTicker']:25} {f['name']}")
#     print("=" * 60)


# if __name__ == "__main__":
#     main()



import