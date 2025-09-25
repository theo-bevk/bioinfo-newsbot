import yaml, datetime as dt
from .fetchers import fetch_from_config
from .normalize import clean_title, near_duplicate
from .rank import score_item
from .summarize import summarize_item
from .storage import get_db, filter_new, mark_seen
from .render import render_html

def load_config():
    with open("config.yaml","r") as f:
        return yaml.safe_load(f)

def dedupe(items):
    items = [{**i, "title": clean_title(i["title"])} for i in items]
    out = []
    for it in items:
        if not any(near_duplicate(it["title"], j["title"]) or it["url"] == j["url"] for j in out):
            out.append(it)
    return out

def main():
    cfg = load_config()
    all_items = []
    for src in cfg["sources"]:
        try:
            items = fetch_from_config(src)
            all_items.extend(items)
        except Exception as e:
            print(f"[WARN] {src['name']}: {e}")

    all_items = dedupe(all_items)

    con = get_db()
    new_items = filter_new(con, all_items)

    now = dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc)
    ranked = sorted(new_items, key=lambda x: score_item(x, now), reverse=True)

    top = ranked[:cfg["digest"]["top_n"]]
    summarized = [summarize_item(it) for it in top]

    html = render_html(summarized)

    with open("data/digest.html","w",encoding="utf-8") as f:
        f.write(html)

    #add other options (email, telegram...)

    mark_seen(con, top)
    print(f"Prepared {len(top)} items.")

if __name__ == "__main__":
    main()
