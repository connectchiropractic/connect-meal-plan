#!/usr/bin/env python3
"""Weekly flyer check: find every regional version of each chain's flyer.

Chains like No Frills, Zehrs and Walmart print different versions of their
weekly flyer for different towns. The app shows one flyer per chain in every
town, so a deal only goes in the app if it is in EVERY version, at the same
price. This script does that check.

Usage:  python3 tools/flyer_versions.py [out.json]

It prints, per chain, which towns get which version and what was left out,
and writes the deals found in every version (with full item details) to
out.json (default: flyer_common.json in the current folder) for picking
this week's deals into data/stores.json.
"""
import json, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor

# One postal code inside each town the app offers.
TOWNS = {
    'windsor': 'N9A1A1', 'south-windsor': 'N9E3M8', 'east-windsor': 'N8T1A1',
    'lasalle': 'N9J1A1', 'tecumseh': 'N8N1A1', 'amherstburg': 'N9V1A1',
    'harrow': 'N0R1G0', 'kingsville': 'N9Y1A1', 'leamington': 'N8H1A1',
    'essex': 'N8M1A1', 'belle-river': 'N0R1A0', 'puce': 'N0R1A0',
}
# Store id in data/stores.json -> (Flipp merchant name, words in the name of
# the main weekly flyer). Side flyers (Diwali, Halloween, beauty) are ignored.
CHAINS = {
    'zehrs': ('Zehrs', 'weekly flyer'),
    'superstore': ('Real Canadian Superstore', 'weekly flyer'),
    'no-frills': ('No Frills', 'weekly flyer'),
    'food-basics': ('Food Basics', 'weekly ad'),
    'freshco': ('FreshCo', 'weekly eflyer'),
    'walmart': ('Walmart', 'flyer'),
    'metro': ('Metro', 'ontario'),
    'sobeys': ('Sobeys', 'weekly eflyer'),
    'foodland': ('Foodland', 'weekly eflyer'),
    'yig': ('Your Independent Grocer', 'weekly flyer'),
}
UA = {'User-Agent': 'Mozilla/5.0'}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        return json.load(r)


def key(it):
    return ((it.get('name') or '').strip().lower(), str(it.get('price') or ''))


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else 'flyer_common.json'
    # chain -> flyer id -> towns that get it
    versions = {c: {} for c in CHAINS}
    for town, pc in TOWNS.items():
        flyers = get(f'https://backflipp.wishabi.com/flipp/flyers?locale=en-ca&postal_code={pc}')
        flyers = flyers.get('flyers', flyers) if isinstance(flyers, dict) else flyers
        for f in flyers:
            for cid, (merchant, word) in CHAINS.items():
                m = (f.get('merchant') or '').lower()
                if m == merchant.lower() and word in (f.get('name') or '').lower():
                    versions[cid].setdefault(f['id'], {'towns': [], 'name': f.get('name'),
                                                       'valid_from': f.get('valid_from', '')[:10],
                                                       'valid_to': f.get('valid_to', '')[:10]})['towns'].append(town)
    result = {}
    for cid, vers in versions.items():
        print(f'\n== {CHAINS[cid][0]}')
        if not vers:
            print('   no weekly flyer found near any town')
            continue
        items = {fid: get(f'https://backflipp.wishabi.com/flipp/flyers/{fid}?locale=en-ca')['items'] for fid in vers}
        keysets = {fid: {key(i) for i in its if i.get('name')} for fid, its in items.items()}
        common = set.intersection(*keysets.values())
        for fid, v in vers.items():
            print(f'   version {fid} ({v["valid_from"]} to {v["valid_to"]}): {", ".join(v["towns"])}')
        if len(vers) > 1:
            for fid in vers:
                extra = sorted(n for n, p in keysets[fid] - common)
                if extra:
                    print(f'   left out, only in {fid}: ' + ' | '.join(e[:40] for e in extra))
        base = next(iter(vers))
        keep = [i for i in items[base] if i.get('name') and key(i) in common and i.get('price')]
        with ThreadPoolExecutor(6) as ex:
            details = list(ex.map(lambda i: get(f'https://backflipp.wishabi.com/flipp/items/{i["id"]}')['item'], keep))
        result[cid] = {
            'versions': vers, 'source': f'https://backflipp.wishabi.com/flipp/flyers/{base}?locale=en-ca',
            'items': [{k: d.get(k) for k in ('name', 'current_price', 'pre_price_text', 'price_text', 'description',
                                             'sale_story', 'valid_from', 'valid_to', 'in_store_only')} for d in details],
        }
        print(f'   {len(keep)} priced deals are in every version')
    json.dump(result, open(out, 'w'), indent=1)
    print(f'\nWrote {out}')


if __name__ == '__main__':
    main()
