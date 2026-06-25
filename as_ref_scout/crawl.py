#!/usr/bin/env python3
"""ArtStation Ref Scout — search ArtStation API v2, generate art reference reports.

Install:
    pip install --user git+https://github.com/luser-dami/artstation-ref-scout.git

Usage:
    as-scout --kw "cyberpunk chinese" --cat environment --pages 2
    HTTPS_PROXY=http://127.0.0.1:7897 as-scout --kw "cyberpunk"
"""
import requests, json, argparse, time, os, sys, socket

SEARCH_API = "https://www.artstation.com/api/v2/search/projects.json"
BASE = "https://www.artstation.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "application/json",
}

COMMON_PROXY_PORTS = [7897, 7890, 10808, 10809, 1080, 1081, 8080, 8081]


def _detect_proxy():
    """Auto-detect local HTTP proxy by trying common ports."""
    for port in COMMON_PROXY_PORTS:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        try:
            s.connect(("127.0.0.1", port))
            proxy_url = f"http://127.0.0.1:{port}"
            try:
                r = requests.get("https://httpbin.org/ip",
                                 proxies={"http": proxy_url, "https": proxy_url},
                                 timeout=3)
                if r.status_code == 200:
                    print(f"[PROXY] Auto-detected: {proxy_url} ({r.json().get('origin','')})")
                    return proxy_url
            except:
                pass
        except:
            pass
        finally:
            s.close()
    return None


def _resolve_proxy(args):
    """Resolve proxy: CLI arg > env var > auto-detect > none."""
    if args.proxy:
        print(f"[PROXY] Using --proxy: {args.proxy}")
        return args.proxy
    for var in ["HTTPS_PROXY", "HTTP_PROXY", "https_proxy", "http_proxy"]:
        val = os.environ.get(var)
        if val:
            print(f"[PROXY] Using env ${var}: {val}")
            return val
    if args.auto_proxy:
        detected = _detect_proxy()
        if detected:
            return detected
        print("[PROXY] No proxy, trying direct...")
    return None


def _session(proxy_url=None):
    s = requests.Session()
    if proxy_url:
        s.proxies = {"http": proxy_url, "https": proxy_url}
    return s


def search(kw, cat=None, pages=2, proxy_url=None):
    """Search ArtStation via API v2. Returns list of project dicts."""
    s = _session(proxy_url)
    all_items = []

    for p in range(1, pages + 1):
        params = {"query": kw, "page": p, "per_page": 24}
        if cat:
            params["category"] = cat

        try:
            r = s.get(SEARCH_API, params=params, headers=HEADERS, timeout=20)
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            print(f"[WARN] page {p} failed: {e}", file=sys.stderr)
            time.sleep(2)
            continue

        items = data.get("data", [])
        if not items:
            break
        all_items.extend(items)
        total = data.get("total_count", 0)
        print(f"  page {p}: {len(items)} items (total ~{total})")
        time.sleep(0.5)

    seen = set()
    results = []
    for item in all_items:
        hid = item.get("hash_id")
        if hid and hid not in seen:
            seen.add(hid)
            results.append({
                "hash_id": hid,
                "title": item.get("title", ""),
                "author": item["user"]["username"] if item.get("user") else "unknown",
                "cover_url": item.get("smaller_square_cover_url", ""),
                "src_url": f"{BASE}/artwork/{hid}",
                "has_multiple": item.get("icons", {}).get("multiple_images", False),
            })
    return results


def main():
    ap = argparse.ArgumentParser(
        description="ArtStation Ref Scout — search art references from ArtStation",
        epilog="Example: as-scout --kw 'cyberpunk chinese' --cat environment --pages 2",
    )
    ap.add_argument("--kw", required=True, help="Search keywords (English works best)")
    ap.add_argument("--cat", default="",
                    choices=["", "character_design", "environment", "game_art",
                             "3d_modeling", "concept_art", "illustration"],
                    help="Category filter")
    ap.add_argument("--pages", type=int, default=2, help="Result pages (24 items/page)")
    ap.add_argument("--outdir", default=os.path.expanduser("~/art-refs"),
                    help="Output directory")
    ap.add_argument("--proxy", default="", help="Proxy URL (e.g. http://127.0.0.1:7897)")
    ap.add_argument("--auto-proxy", action="store_true", default=True,
                    help="Auto-detect local proxy (default: on)")
    args = ap.parse_args()

    slug = args.kw.lower().replace(" ", "-").replace("--", "-")[:40]
    outdir = os.path.join(args.outdir, slug)
    os.makedirs(outdir, exist_ok=True)

    proxy_url = _resolve_proxy(args)

    print(f"[AS] Searching: '{args.kw}' (cat={args.cat or 'all'}, pages={args.pages})")
    results = search(args.kw, args.cat or None, args.pages, proxy_url)
    if not results:
        print("[AS] No projects found.")
        sys.exit(1)

    print(f"[AS] Found {len(results)} projects")

    # index.json
    index = {
        "query": args.kw,
        "category": args.cat or "all",
        "total": len(results),
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "projects": results,
    }
    json_path = os.path.join(outdir, "index.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    print(f"[AS] Saved → {json_path}")

    # report.md
    md = [
        f"# 美术参考：{args.kw}",
        f"",
        f"- **分类**: {args.cat or '全部'}",
        f"- **项目数**: {len(results)}",
        f"- **生成时间**: {index['generated']}",
        f"",
        f"| # | 标题 | 作者 | 多图 | 链接 | 预览 |",
        f"|---|------|------|------|------|------|",
    ]
    for i, p in enumerate(results[:40], 1):
        title = p["title"][:50].replace("|", "\\|")
        multi = "✓" if p.get("has_multiple") else ""
        md.append(
            f"| {i} | {title} | {p['author']} | {multi} | "
            f"[🔗]({p['src_url']}) | "
            f"![thumb]({p['cover_url']}) |"
        )
    if len(results) > 40:
        md.append(f"| ... | *共 {len(results)} 个项目，仅展示前 40 个* |")
    md.extend(["", "---", "*Generated by AS Ref Scout — click 🔗 to view full-res on ArtStation*"])

    report_path = os.path.join(outdir, "report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print(f"[AS] Report → {report_path}")
    print("[AS] Done!")


if __name__ == "__main__":
    main()
