import datetime as dt

def score_item(item: dict, now_utc: dt.datetime) -> float:
    # Score ingredients: freshness aka recency(0–1), source weight aka credibility,
    # length bonus if abstract exists
    published = dt.datetime.fromisoformat(item["published_at"])
    age_hours = (now_utc - published).total_seconds() / 3600
    freshness = max(0.0, 1.0 - age_hours / 72.0)  # linear decay over 3 days
    source_w = {
        "bioRxiv - Bioinformatics": 1.0,
        "arXiv — bioinformatics-wide": 0.9,
        "Europe PMC — bioinformatics-wide (last 7 days)": 0.9,
        "Nature Bioinformatics (subject feed)": 1.0,
        "Genome Biology": 0.95,
        "GigaScience": 0.9,
        "PLOS Computational Biology": 0.9,
        "EMBL-EBI News": 0.8,
        "NCBI Insights Blog": 0.8,
        "Biostars hot": 0.6,
        "Bioconductor blog aggregator": 0.7,
        "Nextflow blog": 0.8,
        "Snakemake blog": 0.8,
        "Bioconda updates": 0.85,
        "Biocontainers updates": 0.85,
    }.get(item["source"], 0.8)
    has_abs = 1.0 if item.get("summary_raw") else 0.0
    return 0.6 * freshness + 0.3 * source_w + 0.1 * has_abs
