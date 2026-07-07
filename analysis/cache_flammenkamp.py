"""
One-shot downloader: pull ALL Flammenkamp configurations to local cache.
Run once. Then all analysis reads from cache/ — zero network, zero IP block.

Cache layout: flammenkamp_cache/n{n}_{symm_name}  (plain text, one line per solution)
"""
import urllib.request, os, time, sys

CACHE = os.path.join(os.path.dirname(__file__), 'flammenkamp_cache')
PROXY = os.environ.get('http_proxy') or os.environ.get('HTTP_PROXY')

SYMM_NAMES = ['.', ':', '/', '-', 'o', 'c', 'x', '+', '*']
URL_NAMES  = {'.': 'iden', ':': 'rot2', '/': 'dia1', '-': 'ort1',
              'o': 'rot4', 'c': 'rct4', 'x': 'dia2', '+': 'ort2', '*': 'full'}

def download(n, symm):
    fname = f'n{n}_{URL_NAMES[symm]}'
    path = os.path.join(CACHE, fname)
    if os.path.exists(path):
        with open(path) as f:
            lines = [l.strip() for l in f if l.strip()]
            return lines, 'cached'
    
    url = f'http://wwwhomes.uni-bielefeld.de/achim/no3in/download/configurations/{fname}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    proxy = urllib.request.ProxyHandler({'http': PROXY, 'https': PROXY})
    opener = urllib.request.build_opener(proxy)
    
    try:
        with opener.open(req, timeout=15) as f:
            data = f.read().decode()
            lines = [l.strip() for l in data.split('\n') if l.strip()]
            if lines and '<html' not in lines[0].lower():
                with open(path, 'w') as out:
                    out.write('\n'.join(lines) + '\n')
                return lines, 'ok'
            return [], 'bad-html'
    except urllib.request.HTTPError as e:
        return [], f'HTTP {e.code}'
    except Exception as e:
        return [], str(e).split('\n')[0][:50]

# ---- MAIN ----
os.makedirs(CACHE, exist_ok=True)
ns = list(range(7, 46))

total = 0
for n in ns:
    for s in SYMM_NAMES:
        lines, status = download(n, s)
        cnt = len(lines)
        tag = f'{cnt:>5} sol' if cnt else f'{status:>12}'
        sym = URL_NAMES[s]
        print(f'n={n:>2} {sym:<5} {tag}')
        if status in ('ok', 'cached'):
            total += cnt
        if status == 'ok':
            time.sleep(0.5)  # be gentle to the server
        sys.stdout.flush()

print(f'\nDone. Total cached solutions: {total}')
