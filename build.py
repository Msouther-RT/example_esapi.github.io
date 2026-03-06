#!/usr/bin/env python3
"""
build.py — Generates the ESAPI Script Hub index page from centre/script metadata.

Run this manually or via GitHub Actions on every push.
It reads all centres/*/centre.json and centres/*/scripts/*/info.json files,
then writes a self-contained docs/index.html.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

CENTRES_DIR = Path("centres")
OUTPUT_DIR = Path("docs")


def load_centres():
    """Walk the centres directory and collect all metadata."""
    centres = []

    if not CENTRES_DIR.exists():
        print(f"Error: {CENTRES_DIR} not found. Run from repo root.")
        sys.exit(1)

    for centre_dir in sorted(CENTRES_DIR.iterdir()):
        if not centre_dir.is_dir():
            continue

        centre_json = centre_dir / "centre.json"
        if not centre_json.exists():
            print(f"Warning: No centre.json in {centre_dir}, skipping.")
            continue

        with open(centre_json) as f:
            centre = json.load(f)

        centre["folder"] = centre_dir.name
        centre["scripts"] = []

        scripts_dir = centre_dir / "scripts"
        if scripts_dir.exists():
            for script_dir in sorted(scripts_dir.iterdir()):
                if not script_dir.is_dir():
                    continue

                info_json = script_dir / "info.json"
                if not info_json.exists():
                    print(f"Warning: No info.json in {script_dir}, skipping.")
                    continue

                with open(info_json) as f:
                    script = json.load(f)

                script["folder"] = script_dir.name
                script["centre_folder"] = centre_dir.name
                script["has_readme"] = (script_dir / "README.md").exists()
                centre["scripts"].append(script)

        centres.append(centre)

    return centres


def status_label(status):
    """Convert status code to display label and CSS class."""
    mapping = {
        "in_use": ("In Use", "status-live"),
        "in_development": ("In Development", "status-dev"),
        "concept": ("Concept", "status-concept"),
        "archived": ("Archived", "status-archived"),
    }
    return mapping.get(status, (status, "status-unknown"))


def build_html(centres):
    """Generate the full index.html content."""

    # Collect all scripts flat for the main table
    all_scripts = []
    for centre in centres:
        for script in centre["scripts"]:
            script["_centre_name"] = centre.get("short_name", centre["name"])
            script["_centre_location"] = centre.get("location", "")
            all_scripts.append(script)

    # Helper: normalise tps to a string for display/filtering
    def tps_to_str(tps):
        if isinstance(tps, list):
            return ", ".join(tps)
        return tps if tps else "Unknown"

    # Collect unique values for filters
    tps_set = set()
    for s in all_scripts:
        tps = s.get("tps", "Unknown")
        if isinstance(tps, list):
            tps_set.update(tps)
        else:
            tps_set.add(tps)
    all_tps = sorted(tps_set)
    all_statuses = sorted(set(s.get("status", "unknown") for s in all_scripts))
    all_languages = sorted(set(s.get("language", "Unknown") for s in all_scripts))

    # Build table rows
    rows_html = ""
    for s in all_scripts:
        label, css_class = status_label(s.get("status", "unknown"))
        tags = ", ".join(s.get("tags", []))
        tps_display = tps_to_str(s.get("tps", "Unknown"))
        readme_link = ""
        if s.get("has_readme"):
            readme_path = f"https://github.com/YOUR-ORG/esapi-script-hub/tree/main/centres/{s['centre_folder']}/scripts/{s['folder']}"
            readme_link = f'<a href="{readme_path}" target="_blank">View details</a>'

        rows_html += f"""
        <tr data-tps="{tps_display}" data-status="{s.get('status', '')}" data-lang="{s.get('language', '')}">
            <td><strong>{s['name']}</strong><br><small>{s.get('description', '')}</small></td>
            <td>{s['_centre_name']}<br><small>{s['_centre_location']}</small></td>
            <td>{tps_display}</td>
            <td>{s.get('language', 'N/A')}</td>
            <td><span class="status-badge {css_class}">{label}</span></td>
            <td><small>{tags}</small></td>
            <td>{readme_link}</td>
            <td><a href="mailto:{s.get('contact_email', '')}">{s.get('contact_name', 'N/A')}</a></td>
        </tr>"""

    # Build filter options
    tps_options = "".join(f'<option value="{t}">{t}</option>' for t in all_tps)
    status_options = "".join(
        f'<option value="{st}">{status_label(st)[0]}</option>' for st in all_statuses
    )
    lang_options = "".join(f'<option value="{l}">{l}</option>' for l in all_languages)

    # Stats
    total_scripts = len(all_scripts)
    total_centres = len(centres)
    live_scripts = sum(1 for s in all_scripts if s.get("status") == "in_use")
    dev_scripts = sum(1 for s in all_scripts if s.get("status") == "in_development")

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RT Scripting Hub — ESAPI &amp; TPS Script Registry</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            background: #f6f8fa;
            color: #1f2328;
            line-height: 1.5;
        }}

        .header {{
            background: #0d1117;
            color: #e6edf3;
            padding: 2rem 1.5rem;
            border-bottom: 3px solid #1a7f37;
        }}

        .header h1 {{
            font-size: 1.6rem;
            font-weight: 600;
            margin-bottom: 0.3rem;
        }}

        .header p {{
            color: #8b949e;
            font-size: 0.95rem;
        }}

        .stats-bar {{
            display: flex;
            gap: 2rem;
            padding: 1rem 1.5rem;
            background: #fff;
            border-bottom: 1px solid #d1d9e0;
            font-size: 0.85rem;
            color: #656d76;
        }}

        .stats-bar strong {{
            color: #1f2328;
        }}

        .controls {{
            padding: 1rem 1.5rem;
            background: #fff;
            border-bottom: 1px solid #d1d9e0;
            display: flex;
            gap: 0.75rem;
            flex-wrap: wrap;
            align-items: center;
        }}

        .controls label {{
            font-size: 0.8rem;
            color: #656d76;
            font-weight: 500;
        }}

        .controls select, .controls input {{
            padding: 0.35rem 0.5rem;
            border: 1px solid #d1d9e0;
            border-radius: 6px;
            font-size: 0.85rem;
            background: #f6f8fa;
        }}

        .controls input {{
            width: 220px;
        }}

        .content {{
            padding: 1rem 1.5rem;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            background: #fff;
            border: 1px solid #d1d9e0;
            border-radius: 6px;
            overflow: hidden;
            font-size: 0.85rem;
        }}

        th {{
            background: #f6f8fa;
            padding: 0.6rem 0.75rem;
            text-align: left;
            font-weight: 600;
            font-size: 0.8rem;
            color: #656d76;
            border-bottom: 1px solid #d1d9e0;
            white-space: nowrap;
        }}

        td {{
            padding: 0.6rem 0.75rem;
            border-bottom: 1px solid #d1d9e0;
            vertical-align: top;
        }}

        tr:last-child td {{
            border-bottom: none;
        }}

        tr:hover {{
            background: #f6f8fa;
        }}

        .status-badge {{
            display: inline-block;
            padding: 0.15rem 0.5rem;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 500;
            white-space: nowrap;
        }}

        .status-live {{
            background: #dafbe1;
            color: #116329;
        }}

        .status-dev {{
            background: #ddf4ff;
            color: #0550ae;
        }}

        .status-concept {{
            background: #fff8c5;
            color: #6a5300;
        }}

        .status-archived {{
            background: #f0f0f0;
            color: #666;
        }}

        a {{
            color: #0969da;
            text-decoration: none;
        }}

        a:hover {{
            text-decoration: underline;
        }}

        .footer {{
            padding: 1.5rem;
            text-align: center;
            font-size: 0.8rem;
            color: #8b949e;
        }}

        .no-results {{
            text-align: center;
            padding: 2rem;
            color: #8b949e;
            display: none;
        }}

        @media (max-width: 900px) {{
            .controls {{ flex-direction: column; gap: 0.5rem; }}
            table {{ font-size: 0.78rem; }}
            td, th {{ padding: 0.4rem; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>RT Scripting Hub</h1>
        <p>A community registry of ESAPI and TPS scripts across UK radiotherapy centres. Browse, filter, and reach out to collaborate.</p>
    </div>

    <div class="stats-bar">
        <span><strong>{total_centres}</strong> centres</span>
        <span><strong>{total_scripts}</strong> scripts registered</span>
        <span><strong>{live_scripts}</strong> in clinical use</span>
        <span><strong>{dev_scripts}</strong> in development</span>
        <span>Last built: {now}</span>
    </div>

    <div class="controls">
        <div>
            <label for="search">Search:</label>
            <input type="text" id="search" placeholder="e.g. DVH, naming, complexity...">
        </div>
        <div>
            <label for="filter-tps">TPS:</label>
            <select id="filter-tps">
                <option value="">All</option>
                {tps_options}
            </select>
        </div>
        <div>
            <label for="filter-status">Status:</label>
            <select id="filter-status">
                <option value="">All</option>
                {status_options}
            </select>
        </div>
        <div>
            <label for="filter-lang">Language:</label>
            <select id="filter-lang">
                <option value="">All</option>
                {lang_options}
            </select>
        </div>
    </div>

    <div class="content">
        <table id="scripts-table">
            <thead>
                <tr>
                    <th>Script</th>
                    <th>Centre</th>
                    <th>TPS</th>
                    <th>Language</th>
                    <th>Status</th>
                    <th>Tags</th>
                    <th>Details</th>
                    <th>Contact</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
        <div class="no-results" id="no-results">No scripts match your filters.</div>
    </div>

    <div class="footer">
        <p>Want to add your centre? See the <a href="https://github.com/YOUR-ORG/esapi-script-hub/blob/main/CONTRIBUTING.md">Contributing Guide</a>.
        Built automatically from script metadata. Source on <a href="https://github.com/YOUR-ORG/esapi-script-hub">GitHub</a>.</p>
    </div>

    <script>
        const searchInput = document.getElementById('search');
        const filterTps = document.getElementById('filter-tps');
        const filterStatus = document.getElementById('filter-status');
        const filterLang = document.getElementById('filter-lang');
        const tbody = document.querySelector('#scripts-table tbody');
        const noResults = document.getElementById('no-results');

        function applyFilters() {{
            const query = searchInput.value.toLowerCase();
            const tps = filterTps.value;
            const status = filterStatus.value;
            const lang = filterLang.value;
            let visible = 0;

            tbody.querySelectorAll('tr').forEach(row => {{
                const text = row.textContent.toLowerCase();
                const matchSearch = !query || text.includes(query);
                const matchTps = !tps || row.dataset.tps === tps;
                const matchStatus = !status || row.dataset.status === status;
                const matchLang = !lang || row.dataset.lang === lang;

                const show = matchSearch && matchTps && matchStatus && matchLang;
                row.style.display = show ? '' : 'none';
                if (show) visible++;
            }});

            noResults.style.display = visible === 0 ? 'block' : 'none';
        }}

        searchInput.addEventListener('input', applyFilters);
        filterTps.addEventListener('change', applyFilters);
        filterStatus.addEventListener('change', applyFilters);
        filterLang.addEventListener('change', applyFilters);
    </script>
</body>
</html>"""

    return html


def main():
    centres = load_centres()
    print(f"Found {len(centres)} centres:")
    for c in centres:
        print(f"  {c.get('short_name', c['name'])}: {len(c['scripts'])} scripts")

    OUTPUT_DIR.mkdir(exist_ok=True)
    html = build_html(centres)

    output_file = OUTPUT_DIR / "index.html"
    with open(output_file, "w") as f:
        f.write(html)

    print(f"\nGenerated {output_file} ({len(html):,} bytes)")


if __name__ == "__main__":
    main()