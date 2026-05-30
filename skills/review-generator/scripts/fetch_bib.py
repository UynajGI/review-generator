#!/usr/bin/env python3
"""
Fetch BibTeX entries from Crossref by DOI or arXiv ID.

Usage:
  # From a list of citation keys with known DOIs
  python scripts/fetch_bib.py --doi 10.1038/nature14539 10.1103/PhysRevLett.69.2863

  # From arXiv IDs (auto-converts to arXiv DOI)
  python scripts/fetch_bib.py --arxiv 1706.03762 1810.04805 1606.02318

  # From a file with one identifier per line (mixed DOI/arXiv)
  python scripts/fetch_bib.py --file ids.txt

  # Output to file instead of stdout
  python scripts/fetch_bib.py --file ids.txt -o refs.bib

Each fetched entry includes: author, title, journal/booktitle, year,
volume, pages, and DOI. Entries already in the output file are skipped.
"""

import argparse, json, re, sys, time, urllib.request, urllib.parse


def fetch_crossref(doi: str) -> str | None:
    """Fetch BibTeX from Crossref by DOI. Returns None on failure."""
    url = f'https://api.crossref.org/works/{doi}/transform/application/x-bibtex'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'LitReview/1.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode('utf-8')
    except Exception as e:
        print(f"  Crossref fetch failed for {doi}: {e}", file=sys.stderr)
        return None


def search_crossref(title: str, author: str = "", year: str = "") -> list[dict]:
    """Search Crossref by title+author+year. Returns list of hits."""
    query = title[:300]
    if author:
        query += f" {author}"
    url = f'https://api.crossref.org/works?query={urllib.parse.quote(query)}&rows=3'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'LitReview/1.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            return data.get('message', {}).get('items', [])
    except Exception as e:
        print(f"  Crossref search failed: {e}", file=sys.stderr)
        return []


def arxiv_bibtex(arxiv_id: str, key: str = "") -> str:
    """Build a minimal BibTeX entry for an arXiv-only paper."""
    k = key or f"arxiv_{arxiv_id.replace('.','_')}"
    doi = f"10.48550/arXiv.{arxiv_id}"
    return f"""@misc{{{k},
  author = {{}},
  title = {{}},
  year = {{}},
  doi = {{{doi}}},
  eprint = {{{arxiv_id}}},
  archivePrefix = {{arXiv}},
  note = {{Metadata incomplete — verify author/title manually}},
}}"""


def extract_key(bibtex: str) -> str:
    """Extract the citation key from a BibTeX entry."""
    m = re.search(r'@\w+\{([^,]+)', bibtex)
    return m.group(1) if m else "unknown"


def load_existing_keys(path: str) -> set[str]:
    """Load all existing citation keys from a .bib file."""
    try:
        with open(path) as f:
            return set(re.findall(r'@\w+\{([^,]+)', f.read()))
    except FileNotFoundError:
        return set()


def main():
    p = argparse.ArgumentParser(description='Fetch BibTeX from Crossref')
    p.add_argument('--doi', nargs='*', help='DOI(s) to fetch')
    p.add_argument('--arxiv', nargs='*', help='arXiv ID(s) to fetch')
    p.add_argument('--file', help='File with one DOI/arXiv per line')
    p.add_argument('-o', '--output', help='Output file (append mode, skips dupes)')
    p.add_argument('--key-prefix', default='', help='Prefix for auto-generated keys')
    args = p.parse_args()

    ids = []
    if args.doi:
        ids.extend(('doi', d) for d in args.doi)
    if args.arxiv:
        ids.extend(('arxiv', a) for a in args.arxiv)
    if args.file:
        with open(args.file) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                # Auto-detect: if it looks like an arXiv ID (digits.digits)
                if re.match(r'^\d{4}\.\d{4,5}(v\d+)?$', line):
                    ids.append(('arxiv', line))
                else:
                    ids.append(('doi', line))

    if not ids:
        p.print_help()
        return

    existing = load_existing_keys(args.output) if args.output else set()
    results = []

    for id_type, id_val in ids:
        if id_type == 'doi':
            print(f"Fetching DOI: {id_val}", file=sys.stderr)
            bib = fetch_crossref(id_val)
            if bib:
                key = extract_key(bib)
                if key in existing:
                    print(f"  Skipped (already in {args.output}): {key}", file=sys.stderr)
                    continue
                results.append(bib)
                print(f"  OK: {key}", file=sys.stderr)
            time.sleep(0.3)  # rate limit
        else:
            print(f"Building arXiv entry: {id_val}", file=sys.stderr)
            key = f"{args.key_prefix}arxiv_{id_val.replace('.','_').replace('/','_')}"
            if key in existing:
                print(f"  Skipped (already in {args.output}): {key}", file=sys.stderr)
                continue
            results.append(arxiv_bibtex(id_val, key))
            print(f"  OK (needs manual author/title): {key}", file=sys.stderr)

    if args.output:
        with open(args.output, 'a') as f:
            f.write('\n'.join(results) + '\n')
        print(f"Appended {len(results)} entries to {args.output}", file=sys.stderr)
    else:
        print('\n'.join(results))


if __name__ == '__main__':
    main()
