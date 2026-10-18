"""Test des Parsers mit nachgebauten click-TT-Seiten (Aufbau wie nuLiga, Stand 18.10.2026).
Aufruf: python scraper/test_parser.py   (mit --seed wird site/data.json aus diesen Daten erzeugt)"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import fetch_clicktt as fc  # noqa: E402

MEETINGS = """\
Sa|19.09.2026|16:00 v|E BOL|TSV Dettingen|TTC Grosselfingen|7:9|
|19.09.2026|18:00|E KLB|TSV Dettingen IV|TSV Riederich II|1:9|
|19.09.2026|19:30|E KLA|TSV Dettingen III|TuS Metzingen III|1:9|
Fr|25.09.2026|20:00|E BK|TSV Dettingen II|TSV Sondelfingen II|9:3|
Sa|26.09.2026|17:30|E KLA|TTV Reicheneck|TSV Dettingen III|6:9|
Fr|02.10.2026|19:30 v|E VP|TSV Dettingen II|TV Derendingen II|1:4|
||20:30|S40 BK|TSV Dettingen|VfL Dettenhausen|5:5|
Sa|03.10.2026|18:00|E KLB|TSV Dettingen IV|TSV Sondelfingen IV|9:4|
||18:20 t/v|E BOL|TSV Dettingen|TSV Sondelfingen|9:3|
Fr|16.10.2026|19:00 v|S40 BK|TSV Dettingen|VfL Dettenhausen II|6:4|
||19:30 v|E VP|TSV Dettingen|TV Derendingen|4:3|
Sa|17.10.2026|17:30|E KLA|FC Mittelstadt II|TSV Dettingen III|9:0|NA
||18:00 v|E KKA|TSV Sickenhausen III|TSV Dettingen V|4:6|
||18:30|E BK|TSV Dettingen II|TSV Grafenberg|9:5|
Mi|21.10.2026|20:00|E KKA|TSV Dettingen V|TSV Grafenberg II||
Fr|23.10.2026|20:00|E BK|TSV Dettingen II|TV Neuhausen||
Sa|24.10.2026|18:00|E KKA|TB Metzingen IV|TSV Dettingen V||
||18:00|E BK|TTC Reutlingen II|TSV Dettingen II||
||19:30|E BOL|TSV Dormettingen|TSV Dettingen||
So|25.10.2026|16:00 v|E BP B|TSV Dettingen III|spielfrei||
Do|29.10.2026|20:15 t/v|S40 BK|TSV Gomaringen|TSV Dettingen||
Fr|30.10.2026|19:30 t/v|E KLB|TuS Metzingen V|TSV Dettingen IV||
Sa|31.10.2026|18:00|E BK|SV Rommelsbach II|TSV Dettingen II||
||19:00|E BOL|TSV Nusplingen II|TSV Dettingen||
||19:30|E KLA|TSV Dettingen III|TTC Reutlingen IV||
Fr|06.11.2026|20:00|E KKA|TSV Dettingen V|SV Tübingen IV||
||20:00|E BK|TSV Dettingen II|TSV Riederich||
Sa|07.11.2026|16:30|E BOL|TSV Dettingen|TTC Ergenzingen II||
Sa|14.11.2026|18:00|E KLA|TV Neuhausen II|TSV Dettingen III||
||18:00|E KLB|TB Metzingen III|TSV Dettingen IV||
||18:30|E BK|TSV Dettingen II|TSV Betzingen III||
Mi|18.11.2026|19:30 v|S40 BK|FC Mittelstadt|TSV Dettingen||
||20:00|E KKA|TSV Dettingen V|TTV Reicheneck II||
Sa|21.11.2026|17:30|E KLB|FC Mittelstadt III|TSV Dettingen IV||
||18:00|E BOL|TSV Gomaringen|TSV Dettingen||
||19:30|E KLA|TSV Dettingen III|SV Rommelsbach III||
Fr|27.11.2026|20:30|S40 BK|TSV Dettingen|TuS Metzingen||
Sa|28.11.2026|18:00 t/v|E KLA|TSV Sickenhausen II|TSV Dettingen III||
||18:00|E BK|TTC Reutlingen III|TSV Dettingen II||
Do|03.12.2026|20:30|S40 BK|TTC Ergenzingen|TSV Dettingen||
Fr|04.12.2026|20:00|E KKA|TSV Dettingen V|EK Lustnau II||
Sa|05.12.2026|16:30|E BOL|TSV Dettingen|TSV Nusplingen||
||18:00|E KLB|TuS Metzingen IV|TSV Dettingen IV||
||19:00 v|E KLA|TB Metzingen II|TSV Dettingen III||
Mi|09.12.2026|20:00|E KKA|TSV Dettingen V|SSV Reutlingen IV||
Sa|12.12.2026|16:30|E BOL|TSV Dettingen|SV Tübingen||
||18:00|E KLB|TSV Sondelfingen III|TSV Dettingen IV||"""

TABLES = {
    "529958": """TTC Grosselfingen|3|3|0|0|27:18|+9|6:0
TSV Gomaringen|3|2|0|1|22:15|+7|4:2
TSV Nusplingen|1|1|0|0|9:3|+6|2:0
TSV Dettingen|2|1|0|1|16:12|+4|2:2
SV Tübingen|2|1|0|1|14:11|+3|2:2
TSV Dormettingen|2|1|0|1|12:13|-1|2:2
TSV Sondelfingen|3|1|0|2|14:24|-10|2:4
TSV Nusplingen II|2|0|0|2|13:18|-5|0:4
TTC Ergenzingen II|2|0|0|2|5:18|-13|0:4""",
    "528659": """TSV Dettingen II|2|2|0|0|18:8|+10|4:0
TV Neuhausen|1|1|0|0|9:6|+3|2:0
TSV Grafenberg|2|1|0|1|14:13|+1|2:2
TTC Reutlingen III|2|1|0|1|13:14|-1|2:2
TSV Betzingen III|2|1|0|1|14:15|-1|2:2
SV Rommelsbach II|0|0|0|0|0:0|0|0:0
TSV Riederich|0|0|0|0|0:0|0|0:0
TTC Reutlingen II|1|0|0|1|6:9|-3|0:2
TSV Sondelfingen II|2|0|0|2|9:18|-9|0:4""",
    "528666": """TuS Metzingen III|3|3|0|0|27:1|+26|6:0
FC Mittelstadt II|2|2|0|0|18:7|+11|4:0
TTV Reicheneck|3|2|0|1|24:12|+12|4:2
TTC Reutlingen IV|1|1|0|0|9:3|+6|2:0
SV Rommelsbach III|1|1|0|0|9:4|+5|2:0
TSV Dettingen III|3|1|0|2|10:24|-14|2:4
TB Metzingen II|5|1|0|4|21:39|-18|2:8
TV Neuhausen II|0|0|0|0|0:0|0|0:0
TSV Sickenhausen II|4|0|0|4|8:36|-28|0:8""",
    "528667": """TSV Riederich II|2|2|0|0|18:5|+13|4:0
TuS Metzingen IV|1|1|0|0|9:0|+9|2:0
TSV Sondelfingen III|1|1|0|0|9:1|+8|2:0
FC Mittelstadt III|1|1|0|0|9:2|+7|2:0
TSV Dettingen IV|2|1|0|1|10:13|-3|2:2
TB Metzingen III|1|0|0|1|0:9|-9|0:2
TuS Metzingen V|2|0|0|2|6:18|-12|0:4
TSV Sondelfingen IV|2|0|0|2|5:18|-13|0:4""",
    "528672": """EK Lustnau II|3|2|1|0|23:7|+16|5:1
SV Tübingen IV|3|1|2|0|20:10|+10|4:2
TTV Reicheneck II|2|1|1|0|11:9|+2|3:1
TSV Dettingen V|1|1|0|0|6:4|+2|2:0
TSV Grafenberg II|2|1|0|1|9:11|-2|2:2
SSV Reutlingen IV|3|1|0|2|7:23|-16|2:4
TSV Sickenhausen III|1|0|0|1|4:6|-2|0:2
TB Metzingen IV|3|0|0|3|10:20|-10|0:6""",
    "528676": """TSV Gomaringen|2|2|0|0|12:0|+12|4:0
TuS Metzingen|2|2|0|0|12:5|+7|4:0
TSV Dettingen|2|1|1|0|11:9|+2|3:1
VfL Dettenhausen|3|1|1|1|12:14|-2|3:3
FC Mittelstadt|2|1|0|1|7:7|0|2:2
TTC Ergenzingen|3|1|0|2|10:13|-3|2:4
VfL Dettenhausen II|4|0|0|4|8:24|-16|0:8""",
}


def meetings_html():
    head = ("<tr><th>Tag</th><th>Datum</th><th>Zeit</th><th>Ort</th><th>Liga</th>"
            "<th>Heimmannschaft</th><th>Gastmannschaft</th><th colspan='3'>Spiele</th><th></th></tr>")
    rows = []
    for i, line in enumerate(MEETINGS.splitlines()):
        day, date, tm, lg, h, a, res, note = line.split("|")
        t, _, fl = tm.partition(" ")
        tcell = t + (f"&nbsp;<span title='verlegt'>{fl}</span>" if fl else "")
        rcell = f"<a href='clubMeetingReport?meeting={1000 + i}&amp;club=3939'>{res}</a>" if res else "&nbsp;"
        rows.append(f"<tr><td>{day}</td><td>{date}</td><td nowrap>{tcell}</td><td><a href='#'>(1)</a></td>"
                    f"<td>{lg}</td><td>{h}</td><td>{a}</td><td>{rcell}</td><td>{note}</td><td></td>"
                    f"<td><img src='check.gif' title='Spielbericht genehmigt'></td></tr>")
    return f"<html><body><table class='result-set'>{head}{''.join(rows)}</table></body></html>"


def table_html(text):
    head = ("<tr><th></th><th>Rang</th><th>Mannschaft</th><th>Begegnungen</th><th>S</th><th>U</th>"
            "<th>N</th><th>Spiele</th><th>+/-</th><th>Punkte</th></tr>")
    rows = [f"<tr><td><img src='up.gif'></td><td>{n}</td><td><a href='#'>{p[0]}</a></td>"
            + "".join(f"<td>{x}</td>" for x in p[1:]) + "</tr>"
            for n, p in enumerate((line.split("|") for line in text.splitlines()), 1)]
    return f"<table class='result-set'>{head}{''.join(rows)}</table>"


if __name__ == "__main__":
    base = "https://ttbw.click-tt.de/cgi-bin/WebObjects/nuLigaTTDE.woa/wa"
    matches = fc.parse_meetings(meetings_html(), base)
    assert len(matches) == 47, len(matches)
    assert matches[1]["d"] == "2026-09-19" and matches[1]["t"] == "18:00"   # Datum übernommen
    assert matches[0]["f"] == ["v"] and matches[8]["f"] == ["t", "v"]
    assert matches[11]["r"] == "9:0" and matches[11]["n"] == "NA"
    assert matches[14]["r"] == "" and matches[0]["u"].startswith(base)
    tables = {g: fc.parse_table(table_html(t)) for g, t in TABLES.items()}
    bol = tables["529958"]
    assert bol[3] == {"rank": 4, "team": "TSV Dettingen", "m": 2, "w": 1, "d": 0, "l": 1,
                      "games": "16:12", "diff": "+4", "pts": "2:2"}, bol[3]
    print("Parser-Tests bestanden:", len(matches), "Spiele,", sum(map(len, tables.values())), "Tabellenzeilen")

    if "--seed" in sys.argv:
        cfg = json.loads(fc.CONFIG.read_text(encoding="utf-8"))
        teams = []
        for t in cfg["teams"]:
            team = {k: t[k] for k in ("key", "label", "clicktt", "short", "league")}
            team["clickttUrl"] = f"{base}/groupPage?championship={t['championship'].replace(' ', '+').replace('/', '%2F')}&group={t['group']}"
            team["myttUrl"] = t.get("mytt", "")
            team["table"] = tables[t["group"]]
            teams.append(team)
        data = {
            "updated": "2026-10-18T17:30:00+00:00", "season": cfg["season"], "clubName": cfg["club_name"],
            "clubUrl": f"{base}/clubInfoDisplay?club={cfg['club_id']}",
            "myttClubUrl": f"https://www.mytischtennis.de/click-tt/TTBW/{cfg['mytt_season']}/verein/{cfg['club_nr']}/TSV_Dettingen/mannschaften/",
            "cups": cfg["cups"], "club": cfg["club"], "teams": teams, "matches": matches, "warnings": [],
        }
        fc.OUT.parent.mkdir(exist_ok=True)
        fc.OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        print("Startdaten geschrieben:", fc.OUT)
