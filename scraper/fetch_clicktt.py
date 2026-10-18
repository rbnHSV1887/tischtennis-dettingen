#!/usr/bin/env python3
"""Holt Spielplan, Ergebnisse und Tabellen des TSV Dettingen aus click-TT (TTBW)
und schreibt sie nach site/data.json. Das sind dieselben Daten, die mytischtennis.de anzeigt.

Aufruf:  python scraper/fetch_clicktt.py            (schreibt site/data.json)
         python scraper/fetch_clicktt.py --dry-run  (zeigt nur an)
"""
import argparse
import datetime as dt
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlencode, urljoin

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "scraper" / "config.json"
OUT = ROOT / "site" / "data.json"
UA = "TSV-Dettingen-Tischtennis-Homepage/1.0 (Vereinshomepage; stuendlicher Abruf)"

FLAG_RE = re.compile(r"(\d{1,2}:\d{2})\s*(.*)")
SCORE_RE = re.compile(r"\b(\d{1,2}:\d{1,2})\b")


def clean(text):
    return re.sub(r"\s+", " ", (text or "").replace("\xa0", " ")).strip()


def header_map(table):
    """Spaltenüberschrift -> Index (colspan berücksichtigt)."""
    for tr in table.find_all("tr"):
        ths = tr.find_all("th")
        if not ths:
            continue
        mapping, idx = {}, 0
        for th in ths:
            name = clean(th.get_text(" "))
            if name and name not in mapping:
                mapping[name] = idx
            idx += int(th.get("colspan", 1) or 1)
        return mapping
    return {}


def find_table(soup, must_have):
    for table in soup.select("table.result-set") or soup.find_all("table"):
        if must_have in header_map(table):
            return table
    return None


def to_iso(date_de):
    d, m, y = date_de.split(".")
    return f"{y}-{m.zfill(2)}-{d.zfill(2)}"


def parse_meetings(html, base):
    soup = BeautifulSoup(html, "html.parser")
    table = find_table(soup, "Heimmannschaft")
    if table is None:
        raise ValueError("Spielplantabelle nicht gefunden")
    h = header_map(table)
    i_date, i_time = h.get("Datum", 1), h.get("Zeit", 2)
    i_lg, i_home, i_away = h.get("Liga", 4), h.get("Heimmannschaft", 5), h.get("Gastmannschaft", 6)
    i_res = h.get("Spiele", i_away + 1)

    matches, last_date = [], ""
    for tr in table.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) <= i_away:
            continue
        cell = [clean(td.get_text(" ")) for td in tds]
        if re.match(r"\d{2}\.\d{2}\.\d{4}", cell[i_date]):
            last_date = cell[i_date]
        if not last_date:
            continue
        t, flags = "", []
        m = FLAG_RE.match(cell[i_time])
        if m:
            t = m.group(1)
            flags = [f for f in re.split(r"[/\s]+", m.group(2)) if f]
        res, report, note = "", "", ""
        if i_res < len(tds):
            sm = SCORE_RE.search(cell[i_res])
            res = sm.group(1) if sm else ""
            a = tds[i_res].find("a", href=True)
            if a and "MeetingReport" in a["href"]:
                report = urljoin(base + "/", a["href"])
        # Zusatzmarkierung (z. B. "NA") steht in der Spalte nach dem Ergebnis
        for extra in cell[i_res + 1:]:
            if re.fullmatch(r"[A-Z]{1,3}", extra):
                note = extra
                break
        matches.append({
            "d": to_iso(last_date), "t": t, "f": flags, "lg": cell[i_lg],
            "h": cell[i_home], "a": cell[i_away], "r": res, "n": note, "u": report,
        })
    return matches


def parse_table(html):
    soup = BeautifulSoup(html, "html.parser")
    table = find_table(soup, "Rang")
    if table is None:
        raise ValueError("Tabelle nicht gefunden")
    h = header_map(table)
    keys = {"Rang": "rank", "Mannschaft": "team", "Begegnungen": "m", "S": "w",
            "U": "d", "N": "l", "Spiele": "games", "+/-": "diff", "Punkte": "pts"}
    rows = []
    for tr in table.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) < 6:
            continue
        cell = [clean(td.get_text(" ")) for td in tds]
        # Manche Tabellen haben eine Icon-Spalte ohne <th>; dann ist die Zeile breiter als der Kopf
        shift = len(tds) - (max(h.values()) + 1) if h else 0
        shift = max(shift, 0)
        row = {}
        for head, key in keys.items():
            if head in h and h[head] + shift < len(cell):
                row[key] = cell[h[head] + shift]
        if not row.get("rank", "").isdigit():
            # Fallback: erste Zahl in der Zeile ist der Rang
            nums = [c for c in cell if c.isdigit()]
            if not nums:
                continue
            row["rank"] = nums[0]
        for k in ("rank", "m", "w", "d", "l"):
            if k in row and row[k].lstrip("-").isdigit():
                row[k] = int(row[k])
        rows.append(row)
    return rows


def get(session, url):
    for attempt in range(3):
        try:
            r = session.get(url, timeout=30)
            r.raise_for_status()
            r.encoding = r.encoding or "utf-8"
            return r.text
        except requests.RequestException as e:
            print(f"  Versuch {attempt + 1} fehlgeschlagen: {e}", file=sys.stderr)
            time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"Abruf fehlgeschlagen: {url}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    base = cfg["base"]
    old = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    old_tables = {t["key"]: t.get("table", []) for t in old.get("teams", [])}

    s = requests.Session()
    s.headers["User-Agent"] = UA
    errors = []

    meetings_url = f"{base}/clubMeetings?" + urlencode({
        "club": cfg["club_id"], "searchType": "1",
        "searchTimeRangeFrom": cfg["season_from"], "searchTimeRangeTo": cfg["season_to"],
        "selectedTeamId": "WONoSelectionString", "searchMeetings": "Suchen",
    })
    try:
        matches = parse_meetings(get(s, meetings_url), base)
        print(f"Spielplan: {len(matches)} Begegnungen")
    except Exception as e:  # alte Daten behalten
        errors.append(f"Spielplan: {e}")
        matches = old.get("matches", [])

    teams = []
    for t in cfg["teams"]:
        time.sleep(2)  # click-TT schonen
        url = f"{base}/groupPage?" + urlencode({"championship": t["championship"], "group": t["group"]})
        team = {k: t[k] for k in ("key", "label", "clicktt", "short", "league")}
        team["clickttUrl"] = url
        team["myttUrl"] = t.get("mytt", "")
        try:
            team["table"] = parse_table(get(s, url))
            print(f"{t['label']}: {len(team['table'])} Tabellenzeilen")
        except Exception as e:
            errors.append(f"{t['label']}: {e}")
            team["table"] = old_tables.get(t["key"], [])
        teams.append(team)

    if not matches and not any(t["table"] for t in teams):
        print("Keine Daten erhalten – data.json bleibt unverändert.", file=sys.stderr)
        sys.exit(1)

    data = {
        "updated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "season": cfg["season"],
        "clubName": cfg["club_name"],
        "clubUrl": f"{base}/clubInfoDisplay?club={cfg['club_id']}",
        "myttClubUrl": f"https://www.mytischtennis.de/click-tt/TTBW/{cfg['mytt_season']}/verein/{cfg['club_nr']}/TSV_Dettingen/mannschaften/",
        "cups": cfg.get("cups", {}),
        "club": cfg.get("club", {}),
        "teams": teams,
        "matches": matches,
        "warnings": errors,
    }
    if args.dry_run:
        print(json.dumps(data, ensure_ascii=False, indent=1)[:3000])
        return
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Geschrieben: {OUT}" + (f" (Warnungen: {errors})" if errors else ""))


if __name__ == "__main__":
    main()
