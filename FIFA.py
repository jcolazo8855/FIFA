"""
2026 FIFA World Cup — Interactive Stats & Predictor
=====================================================
Run:   streamlit run worldcup2026.py
Deps:  pip install streamlit plotly pandas numpy
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="2026 FIFA World Cup",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Inter:wght@300;400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer { visibility: hidden; }
.block-container { padding: 1rem 2rem 2rem; max-width: 1400px; }

/* Header */
.wc-header {
    background: linear-gradient(135deg, #003366 0%, #cc0000 50%, #006600 100%);
    border-radius: 16px; padding: 2rem; margin-bottom: 1.5rem; text-align: center;
}
.wc-header h1 { font-family:'Rajdhani',sans-serif; font-size:2.8rem; font-weight:700;
    color:#FFD700; margin:0; text-shadow:2px 2px 4px rgba(0,0,0,.5); }
.wc-header p  { color:rgba(255,255,255,.85); font-size:1rem; margin:6px 0 0; }

/* Group card */
.group-card {
    background:var(--color-background-primary);
    border:0.5px solid var(--color-border-tertiary);
    border-radius:12px; padding:1rem 1.1rem; height:100%; }
.group-title { font-family:'Rajdhani',sans-serif; font-size:1.1rem;
    font-weight:700; color:var(--color-text-primary); margin-bottom:.5rem; }

/* Team flag badge */
.team-row { display:flex; align-items:center; gap:8px; padding:4px 0;
    font-size:13px; border-bottom:0.5px solid var(--color-border-tertiary); }
.team-row:last-child { border-bottom:none; }
.flag { font-size:20px; width:28px; text-align:center; }

/* Stat card */
.stat-card { background:var(--color-background-secondary);
    border-radius:10px; padding:.9rem 1rem; text-align:center; }
.stat-val { font-family:'Rajdhani',sans-serif; font-size:1.8rem;
    font-weight:700; color:var(--color-text-primary); }
.stat-lbl { font-size:11px; color:var(--color-text-secondary);
    text-transform:uppercase; letter-spacing:.08em; margin-top:2px; }

/* KPI chips */
.kpi-row { display:flex; flex-wrap:wrap; gap:8px; margin:8px 0; }
.kpi-chip { background:var(--color-background-secondary);
    border:0.5px solid var(--color-border-tertiary);
    border-radius:8px; padding:4px 10px; font-size:12px; }
.kpi-chip b { color:var(--color-text-primary); }

/* Probability bar */
.prob-bar-wrap { margin:4px 0; }
.prob-bar-label { font-size:12px; color:var(--color-text-secondary);
    display:flex; justify-content:space-between; margin-bottom:2px; }
.prob-bar-track { height:10px; background:var(--color-background-secondary);
    border-radius:5px; overflow:hidden; }

/* Schedule table */
.match-row { display:flex; align-items:center; gap:10px; padding:8px 10px;
    border-bottom:0.5px solid var(--color-border-tertiary); font-size:13px; }
.match-row:last-child { border-bottom:none; }
.match-teams { flex:1; font-weight:500; }
.match-info  { font-size:11px; color:var(--color-text-secondary); }

/* Section headers */
.section-hdr { font-family:'Rajdhani',sans-serif; font-size:1.4rem;
    font-weight:700; color:var(--color-text-primary);
    border-bottom:2px solid #cc0000; padding-bottom:4px; margin:1.5rem 0 1rem; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# DATA
# ─────────────────────────────────────────────────────────────
# FIFA Rankings (March 2026 approx), titles, odds, etc.
TEAMS = {
    # name: {flag, confederation, fifa_rank, world_titles, win_odds_decimal,
    #        group, qualified_via, star_player, form_pts (last 5 games),
    #        avg_goals_scored, avg_goals_conceded, squad_depth, head_coach}
    "Spain":        {"flag":"🇪🇸","conf":"UEFA","rank":1, "titles":1,"odds":5.0, "group":"H","via":"Auto","star":"Yamal","form":12,"gs":2.3,"gc":0.5,"depth":95,"coach":"De la Fuente"},
    "France":       {"flag":"🇫🇷","conf":"UEFA","rank":2, "titles":2,"odds":6.5, "group":"I","via":"Auto","star":"Mbappé","form":11,"gs":2.1,"gc":0.7,"depth":94,"coach":"Deschamps"},
    "England":      {"flag":"🏴󠁧󠁢󠁥󠁮󠁧󠁿","conf":"UEFA","rank":3, "titles":1,"odds":6.0, "group":"L","via":"Auto","star":"Bellingham","form":11,"gs":1.9,"gc":0.8,"depth":93,"coach":"Tuchel"},
    "Brazil":       {"flag":"🇧🇷","conf":"CONMEBOL","rank":4,"titles":5,"odds":7.5, "group":"C","via":"Auto","star":"Vinicius Jr","form":10,"gs":2.0,"gc":0.9,"depth":92,"coach":"Ancelotti"},
    "Argentina":    {"flag":"🇦🇷","conf":"CONMEBOL","rank":5,"titles":3,"odds":8.0, "group":"J","via":"Auto","star":"Messi","form":13,"gs":2.2,"gc":0.6,"depth":91,"coach":"Scaloni"},
    "Portugal":     {"flag":"🇵🇹","conf":"UEFA","rank":6, "titles":0,"odds":10.0,"group":"K","via":"Auto","star":"Ronaldo","form":10,"gs":2.0,"gc":0.7,"depth":90,"coach":"Martinez"},
    "Netherlands":  {"flag":"🇳🇱","conf":"UEFA","rank":7, "titles":0,"odds":12.0,"group":"F","via":"Auto","star":"Van Dijk","form":10,"gs":1.8,"gc":0.8,"depth":88,"coach":"Slot"},
    "Belgium":      {"flag":"🇧🇪","conf":"UEFA","rank":8, "titles":0,"odds":15.0,"group":"G","via":"Auto","star":"De Bruyne","form":9, "gs":1.7,"gc":0.9,"depth":87,"coach":"Tedesco"},
    "Germany":      {"flag":"🇩🇪","conf":"UEFA","rank":9, "titles":4,"odds":11.0,"group":"E","via":"Auto","star":"Musiala","form":9, "gs":1.8,"gc":0.8,"depth":89,"coach":"Nagelsmann"},
    "Mexico":       {"flag":"🇲🇽","conf":"CONCACAF","rank":16,"titles":0,"odds":40.0,"group":"A","via":"Host","star":"Lozano","form":8, "gs":1.4,"gc":1.1,"depth":78,"coach":"González"},
    "USA":          {"flag":"🇺🇸","conf":"CONCACAF","rank":14,"titles":0,"odds":66.0,"group":"D","via":"Host","star":"Pulisic","form":9, "gs":1.5,"gc":1.0,"depth":80,"coach":"Pochettino"},
    "Canada":       {"flag":"🇨🇦","conf":"CONCACAF","rank":47,"titles":0,"odds":80.0,"group":"B","via":"Host","star":"Davies","form":8, "gs":1.3,"gc":1.2,"depth":74,"coach":"Herdman"},
    "South Korea":  {"flag":"🇰🇷","conf":"AFC","rank":22,"titles":0,"odds":60.0,"group":"A","via":"Auto","star":"Son","form":8, "gs":1.6,"gc":0.9,"depth":82,"coach":"Hong"},
    "Japan":        {"flag":"🇯🇵","conf":"AFC","rank":15,"titles":0,"odds":30.0,"group":"F","via":"Auto","star":"Kubo","form":10,"gs":1.8,"gc":0.7,"depth":85,"coach":"Moriyasu"},
    "Australia":    {"flag":"🇦🇺","conf":"AFC","rank":23,"titles":0,"odds":100.0,"group":"D","via":"Auto","star":"Leckie","form":7, "gs":1.2,"gc":1.1,"depth":72,"coach":"Arnold"},
    "Iran":         {"flag":"🇮🇷","conf":"AFC","rank":20,"titles":0,"odds":120.0,"group":"G","via":"Auto","star":"Taremi","form":7, "gs":1.3,"gc":1.0,"depth":73,"coach":"Queiroz"},
    "Saudi Arabia": {"flag":"🇸🇦","conf":"AFC","rank":53,"titles":0,"odds":150.0,"group":"H","via":"Auto","star":"Al-Dawsari","form":6,"gs":1.1,"gc":1.3,"depth":68,"coach":"Renard"},
    "Qatar":        {"flag":"🇶🇦","conf":"AFC","rank":60,"titles":0,"odds":200.0,"group":"B","via":"Auto","star":"Al-Haydos","form":5,"gs":0.9,"gc":1.4,"depth":65,"coach":"Tintin"},
    "Uzbekistan":   {"flag":"🇺🇿","conf":"AFC","rank":68,"titles":0,"odds":250.0,"group":"K","via":"Auto","star":"Shomurodov","form":6,"gs":1.1,"gc":1.2,"depth":64,"coach":"Sholev"},
    "Jordan":       {"flag":"🇯🇴","conf":"AFC","rank":74,"titles":0,"odds":300.0,"group":"J","via":"Auto","star":"Al-Naimat","form":5,"gs":0.9,"gc":1.3,"depth":62,"coach":"Jaradat"},
    "Morocco":      {"flag":"🇲🇦","conf":"CAF","rank":14,"titles":0,"odds":18.0,"group":"C","via":"Auto","star":"Hakimi","form":10,"gs":1.6,"gc":0.6,"depth":86,"coach":"Regragui"},
    "Senegal":      {"flag":"🇸🇳","conf":"CAF","rank":18,"titles":0,"odds":25.0,"group":"I","via":"Auto","star":"Mané","form":8, "gs":1.4,"gc":0.9,"depth":82,"coach":"Cissé"},
    "Egypt":        {"flag":"🇪🇬","conf":"CAF","rank":35,"titles":0,"odds":70.0,"group":"G","via":"Auto","star":"Salah","form":7, "gs":1.3,"gc":1.0,"depth":77,"coach":"El-Khatib"},
    "Algeria":      {"flag":"🇩🇿","conf":"CAF","rank":40,"titles":0,"odds":90.0,"group":"J","via":"Auto","star":"Mahrez","form":6, "gs":1.2,"gc":1.0,"depth":74,"coach":"Petkovic"},
    "Ivory Coast":  {"flag":"🇨🇮","conf":"CAF","rank":43,"titles":0,"odds":80.0,"group":"E","via":"Auto","star":"Zaha","form":7, "gs":1.3,"gc":1.0,"depth":75,"coach":"Faé"},
    "Tunisia":      {"flag":"🇹🇳","conf":"CAF","rank":30,"titles":0,"odds":100.0,"group":"F","via":"Auto","star":"Msakni","form":6, "gs":1.1,"gc":1.1,"depth":72,"coach":"Jilani"},
    "South Africa": {"flag":"🇿🇦","conf":"CAF","rank":55,"titles":0,"odds":200.0,"group":"A","via":"Auto","star":"Dolly","form":6, "gs":1.0,"gc":1.3,"depth":65,"coach":"Broos"},
    "Ghana":        {"flag":"🇬🇭","conf":"CAF","rank":65,"titles":0,"odds":180.0,"group":"L","via":"Auto","star":"Kudus","form":6, "gs":1.2,"gc":1.1,"depth":70,"coach":"Addo"},
    "Cape Verde":   {"flag":"🇨🇻","conf":"CAF","rank":70,"titles":0,"odds":250.0,"group":"H","via":"Auto","star":"Pires","form":7, "gs":1.1,"gc":1.0,"depth":68,"coach":"Beja"},
    "Colombia":     {"flag":"🇨🇴","conf":"CONMEBOL","rank":12,"titles":0,"odds":22.0,"group":"K","via":"Auto","star":"Díaz","form":9, "gs":1.7,"gc":0.8,"depth":83,"coach":"Néstor"},
    "Uruguay":      {"flag":"🇺🇾","conf":"CONMEBOL","rank":17,"titles":2,"odds":30.0,"group":"H","via":"Auto","star":"Núñez","form":8, "gs":1.5,"gc":0.9,"depth":81,"coach":"Bielsa"},
    "Ecuador":      {"flag":"🇪🇨","conf":"CONMEBOL","rank":28,"titles":0,"odds":80.0,"group":"E","via":"Auto","star":"Caicedo","form":7, "gs":1.3,"gc":1.0,"depth":73,"coach":"Sánchez"},
    "Paraguay":     {"flag":"🇵🇾","conf":"CONMEBOL","rank":50,"titles":0,"odds":150.0,"group":"D","via":"Auto","star":"Sanabria","form":6, "gs":1.0,"gc":1.2,"depth":67,"coach":"Berizzo"},
    "Switzerland":  {"flag":"🇨🇭","conf":"UEFA","rank":19,"titles":0,"odds":30.0,"group":"B","via":"Auto","star":"Shaqiri","form":8, "gs":1.5,"gc":0.9,"depth":82,"coach":"Yakin"},
    "Croatia":      {"flag":"🇭🇷","conf":"UEFA","rank":10,"titles":0,"odds":25.0,"group":"L","via":"Auto","star":"Modrić","form":8, "gs":1.6,"gc":0.8,"depth":83,"coach":"Dalić"},
    "Austria":      {"flag":"🇦🇹","conf":"UEFA","rank":24,"titles":0,"odds":50.0,"group":"J","via":"Auto","star":"Alaba","form":7, "gs":1.4,"gc":0.9,"depth":78,"coach":"Rangnick"},
    "Norway":       {"flag":"🇳🇴","conf":"UEFA","rank":26,"titles":0,"odds":20.0,"group":"I","via":"Auto","star":"Haaland","form":10,"gs":2.0,"gc":0.8,"depth":84,"coach":"Ståle"},
    "Scotland":     {"flag":"🏴󠁧󠁢󠁳󠁣󠁴󠁿","conf":"UEFA","rank":38,"titles":0,"odds":100.0,"group":"C","via":"Auto","star":"McTominay","form":7,"gs":1.3,"gc":1.0,"depth":73,"coach":"Clarke"},
    "Panama":       {"flag":"🇵🇦","conf":"CONCACAF","rank":44,"titles":0,"odds":200.0,"group":"L","via":"Auto","star":"Davis","form":6, "gs":1.0,"gc":1.2,"depth":66,"coach":"Thomas"},
    "Haiti":        {"flag":"🇭🇹","conf":"CONCACAF","rank":82,"titles":0,"odds":400.0,"group":"C","via":"Auto","star":"Nazon","form":5, "gs":0.8,"gc":1.5,"depth":58,"coach":"Ménard"},
    "Curaçao":      {"flag":"🇨🇼","conf":"CONCACAF","rank":89,"titles":0,"odds":500.0,"group":"E","via":"Auto","star":"Mijnals","form":5, "gs":0.8,"gc":1.5,"depth":55,"coach":"Gomez"},
    "New Zealand":  {"flag":"🇳🇿","conf":"OFC","rank":95,"titles":0,"odds":500.0,"group":"G","via":"Auto","star":"Wood","form":5, "gs":0.7,"gc":1.6,"depth":55,"coach":"Farina"},
    # Playoff slots (representative TBD)
    "UEFA Playoff A":{"flag":"🏆","conf":"UEFA","rank":30,"titles":0,"odds":50.0,"group":"B","via":"Playoff","star":"TBD","form":7,"gs":1.4,"gc":0.9,"depth":75,"coach":"TBD"},
    "UEFA Playoff B":{"flag":"🏆","conf":"UEFA","rank":32,"titles":0,"odds":60.0,"group":"F","via":"Playoff","star":"TBD","form":7,"gs":1.3,"gc":1.0,"depth":73,"coach":"TBD"},
    "UEFA Playoff C":{"flag":"🏆","conf":"UEFA","rank":34,"titles":0,"odds":70.0,"group":"D","via":"Playoff","star":"TBD","form":7,"gs":1.3,"gc":1.0,"depth":72,"coach":"TBD"},
    "UEFA Playoff D":{"flag":"🏆","conf":"UEFA","rank":36,"titles":0,"odds":80.0,"group":"A","via":"Playoff","star":"TBD","form":7,"gs":1.2,"gc":1.1,"depth":71,"coach":"TBD"},
    "Intercont. PO 1":{"flag":"🌍","conf":"Other","rank":80,"titles":0,"odds":300.0,"group":"K","via":"Playoff","star":"TBD","form":5,"gs":1.0,"gc":1.3,"depth":62,"coach":"TBD"},
    "Intercont. PO 2":{"flag":"🌍","conf":"Other","rank":85,"titles":0,"odds":350.0,"group":"I","via":"Playoff","star":"TBD","form":5,"gs":0.9,"gc":1.4,"depth":60,"coach":"TBD"},
}

GROUPS = {
    "A": ["Mexico","South Korea","South Africa","UEFA Playoff D"],
    "B": ["Canada","Switzerland","Qatar","UEFA Playoff A"],
    "C": ["Brazil","Morocco","Scotland","Haiti"],
    "D": ["USA","Paraguay","Australia","UEFA Playoff C"],
    "E": ["Germany","Ivory Coast","Ecuador","Curaçao"],
    "F": ["Netherlands","Japan","UEFA Playoff B","Tunisia"],
    "G": ["Belgium","Egypt","Iran","New Zealand"],
    "H": ["Spain","Uruguay","Saudi Arabia","Cape Verde"],
    "I": ["France","Senegal","Norway","Intercont. PO 2"],
    "J": ["Argentina","Algeria","Austria","Jordan"],
    "K": ["Portugal","Colombia","Uzbekistan","Intercont. PO 1"],
    "L": ["England","Croatia","Ghana","Panama"],
}

STAR_PLAYERS = [
    {"name":"Kylian Mbappé",      "country":"France",     "flag":"🇫🇷","age":27,"club":"Real Madrid","pos":"FW","wc_goals":12,"market_val_M":180,"rating":94},
    {"name":"Erling Haaland",     "country":"Norway",     "flag":"🇳🇴","age":25,"club":"Man City",    "pos":"FW","wc_goals":0, "market_val_M":200,"rating":93},
    {"name":"Lionel Messi",       "country":"Argentina",  "flag":"🇦🇷","age":38,"club":"Inter Miami",  "pos":"FW","wc_goals":13,"market_val_M":35, "rating":92},
    {"name":"Lamine Yamal",       "country":"Spain",      "flag":"🇪🇸","age":18,"club":"Barcelona",   "pos":"FW","wc_goals":0, "market_val_M":220,"rating":91},
    {"name":"Vinicius Jr",        "country":"Brazil",     "flag":"🇧🇷","age":24,"club":"Real Madrid","pos":"FW","wc_goals":1, "market_val_M":180,"rating":91},
    {"name":"Jude Bellingham",    "country":"England",    "flag":"🏴󠁧󠁢󠁥󠁮󠁧󠁿","age":22,"club":"Real Madrid","pos":"MF","wc_goals":1, "market_val_M":180,"rating":90},
    {"name":"Cristiano Ronaldo",  "country":"Portugal",   "flag":"🇵🇹","age":41,"club":"Al Nassr",    "pos":"FW","wc_goals":8, "market_val_M":15, "rating":88},
    {"name":"Mohamed Salah",      "country":"Egypt",      "flag":"🇪🇬","age":33,"club":"Liverpool",   "pos":"FW","wc_goals":1, "market_val_M":50, "rating":89},
    {"name":"Pedri",              "country":"Spain",      "flag":"🇪🇸","age":23,"club":"Barcelona",   "pos":"MF","wc_goals":0, "market_val_M":120,"rating":89},
    {"name":"Kevin De Bruyne",    "country":"Belgium",    "flag":"🇧🇪","age":34,"club":"Man City",    "pos":"MF","wc_goals":1, "market_val_M":40, "rating":89},
    {"name":"Jamal Musiala",      "country":"Germany",    "flag":"🇩🇪","age":22,"club":"Bayern",      "pos":"MF","wc_goals":1, "market_val_M":150,"rating":89},
    {"name":"Heung-min Son",      "country":"South Korea","flag":"🇰🇷","age":33,"club":"Tottenham",   "pos":"FW","wc_goals":2, "market_val_M":35, "rating":87},
    {"name":"Achraf Hakimi",      "country":"Morocco",    "flag":"🇲🇦","age":27,"club":"PSG",         "pos":"DF","wc_goals":1, "market_val_M":70, "rating":88},
    {"name":"Federico Valverde",  "country":"Uruguay",    "flag":"🇺🇾","age":25,"club":"Real Madrid","pos":"MF","wc_goals":0, "market_val_M":100,"rating":88},
    {"name":"Christian Pulisic",  "country":"USA",        "flag":"🇺🇸","age":27,"club":"AC Milan",    "pos":"FW","wc_goals":2, "market_val_M":65, "rating":85},
    {"name":"Luis Díaz",          "country":"Colombia",   "flag":"🇨🇴","age":27,"club":"Liverpool",   "pos":"FW","wc_goals":1, "market_val_M":90, "rating":87},
    {"name":"Bukayo Saka",        "country":"England",    "flag":"🏴󠁧󠁢󠁥󠁮󠁧󠁿","age":24,"club":"Arsenal",     "pos":"FW","wc_goals":2, "market_val_M":150,"rating":88},
    {"name":"Takefusa Kubo",      "country":"Japan",      "flag":"🇯🇵","age":23,"club":"Real Sociedad","pos":"FW","wc_goals":0,"market_val_M":80, "rating":85},
    {"name":"Raphaël Varane",     "country":"France",     "flag":"🇫🇷","age":32,"club":"Como",        "pos":"DF","wc_goals":1, "market_val_M":25, "rating":84},
    {"name":"Alphonso Davies",    "country":"Canada",     "flag":"🇨🇦","age":24,"club":"Bayern",      "pos":"DF","wc_goals":0, "market_val_M":90, "rating":86},
    {"name":"Virgil van Dijk",    "country":"Netherlands","flag":"🇳🇱","age":34,"club":"Liverpool",   "pos":"DF","wc_goals":1, "market_val_M":40, "rating":87},
    {"name":"Luka Modrić",        "country":"Croatia",    "flag":"🇭🇷","age":40,"club":"Real Madrid","pos":"MF","wc_goals":2, "market_val_M":8,  "rating":84},
    {"name":"Darwin Núñez",       "country":"Uruguay",    "flag":"🇺🇾","age":25,"club":"Liverpool",   "pos":"FW","wc_goals":0, "market_val_M":100,"rating":85},
    {"name":"Moisés Caicedo",     "country":"Ecuador",    "flag":"🇪🇨","age":23,"club":"Chelsea",     "pos":"MF","wc_goals":0, "market_val_M":100,"rating":85},
    {"name":"Sadio Mané",         "country":"Senegal",    "flag":"🇸🇳","age":33,"club":"Al-Nassr",    "pos":"FW","wc_goals":3, "market_val_M":25, "rating":84},
]

GROUP_SCHEDULE = {
    "A": [
        {"date":"Jun 11","match":"Mexico vs South Africa","venue":"Mexico City","time":"3pm ET"},
        {"date":"Jun 11","match":"South Korea vs UEFA PO-D","venue":"Guadalajara","time":"10pm ET"},
        {"date":"Jun 18","match":"UEFA PO-D vs South Africa","venue":"Atlanta","time":"Noon ET"},
        {"date":"Jun 18","match":"Mexico vs South Korea","venue":"Guadalajara","time":"9pm ET"},
        {"date":"Jun 26","match":"Mexico vs UEFA PO-D","venue":"Dallas","time":"3pm ET"},
        {"date":"Jun 26","match":"South Africa vs South Korea","venue":"Atlanta","time":"3pm ET"},
    ],
    "B": [
        {"date":"Jun 12","match":"Canada vs UEFA PO-A","venue":"Toronto","time":"3pm ET"},
        {"date":"Jun 13","match":"Qatar vs Switzerland","venue":"San Francisco","time":"3pm ET"},
        {"date":"Jun 18","match":"Switzerland vs UEFA PO-A","venue":"Los Angeles","time":"3pm ET"},
        {"date":"Jun 18","match":"Canada vs Qatar","venue":"Vancouver","time":"6pm ET"},
        {"date":"Jun 24","match":"Switzerland vs Canada","venue":"Vancouver","time":"3pm ET"},
        {"date":"Jun 24","match":"UEFA PO-A vs Qatar","venue":"Los Angeles","time":"3pm ET"},
    ],
    "C": [
        {"date":"Jun 13","match":"Brazil vs Morocco","venue":"New York/NJ","time":"6pm ET"},
        {"date":"Jun 13","match":"Haiti vs Scotland","venue":"Boston","time":"9pm ET"},
        {"date":"Jun 19","match":"Scotland vs Morocco","venue":"Boston","time":"6pm ET"},
        {"date":"Jun 19","match":"Brazil vs Haiti","venue":"Philadelphia","time":"9pm ET"},
        {"date":"Jun 25","match":"Brazil vs Scotland","venue":"Kansas City","time":"3pm ET"},
        {"date":"Jun 25","match":"Morocco vs Haiti","venue":"Houston","time":"3pm ET"},
    ],
    "D": [
        {"date":"Jun 12","match":"USA vs Paraguay","venue":"Los Angeles","time":"9pm ET"},
        {"date":"Jun 13","match":"Australia vs UEFA PO-C","venue":"Vancouver","time":"12am ET"},
        {"date":"Jun 19","match":"USA vs Australia","venue":"Seattle","time":"3pm ET"},
        {"date":"Jun 20","match":"Uruguay vs Cape Verde","venue":"Miami","time":"6pm ET"},  # placeholders for later rounds
        {"date":"Jun 25","match":"UEFA PO-C vs USA","venue":"Seattle","time":"3pm ET"},
        {"date":"Jun 26","match":"Paraguay vs Australia","venue":"San Francisco","time":"3pm ET"},
    ],
    "E": [
        {"date":"Jun 14","match":"Ivory Coast vs Ecuador","venue":"Miami","time":"Noon ET"},
        {"date":"Jun 14","match":"Germany vs Curaçao","venue":"Toronto","time":"3pm ET"},
        {"date":"Jun 20","match":"Germany vs Ivory Coast","venue":"Toronto","time":"4pm ET"},
        {"date":"Jun 20","match":"Ecuador vs Curaçao","venue":"Kansas City","time":"8pm ET"},
        {"date":"Jun 26","match":"Ecuador vs Germany","venue":"New York/NJ","time":"3pm ET"},
        {"date":"Jun 26","match":"Curaçao vs Ivory Coast","venue":"Philadelphia","time":"3pm ET"},
    ],
    "F": [
        {"date":"Jun 14","match":"UEFA PO-B vs Tunisia","venue":"Monterrey","time":"10pm ET"},
        {"date":"Jun 14","match":"Netherlands vs Japan","venue":"Houston","time":"1pm ET"},
        {"date":"Jun 20","match":"Netherlands vs UEFA PO-B","venue":"Houston","time":"1pm ET"},
        {"date":"Jun 20","match":"Tunisia vs Japan","venue":"Monterrey","time":"12am ET"},
        {"date":"Jun 25","match":"Tunisia vs Netherlands","venue":"Kansas City","time":"3pm ET"},
        {"date":"Jun 25","match":"Japan vs UEFA PO-B","venue":"Los Angeles","time":"3pm ET"},
    ],
    "G": [
        {"date":"Jun 15","match":"Belgium vs Egypt","venue":"Seattle","time":"3pm ET"},
        {"date":"Jun 15","match":"Iran vs New Zealand","venue":"Los Angeles","time":"9pm ET"},
        {"date":"Jun 21","match":"Belgium vs Iran","venue":"Los Angeles","time":"3pm ET"},
        {"date":"Jun 21","match":"New Zealand vs Egypt","venue":"Vancouver","time":"9pm ET"},
        {"date":"Jun 26","match":"Egypt vs Iran","venue":"Seattle","time":"3pm ET"},
        {"date":"Jun 27","match":"New Zealand vs Belgium","venue":"Vancouver","time":"3pm ET"},
    ],
    "H": [
        {"date":"Jun 15","match":"Spain vs Cape Verde","venue":"Atlanta","time":"Noon ET"},
        {"date":"Jun 15","match":"Saudi Arabia vs Uruguay","venue":"Miami","time":"6pm ET"},
        {"date":"Jun 21","match":"Spain vs Saudi Arabia","venue":"Atlanta","time":"Noon ET"},
        {"date":"Jun 21","match":"Uruguay vs Cape Verde","venue":"Miami","time":"6pm ET"},
        {"date":"Jun 26","match":"Cape Verde vs Saudi Arabia","venue":"Miami","time":"3pm ET"},
        {"date":"Jun 26","match":"Uruguay vs Spain","venue":"Atlanta","time":"3pm ET"},
    ],
    "I": [
        {"date":"Jun 16","match":"France vs Senegal","venue":"New York/NJ","time":"3pm ET"},
        {"date":"Jun 16","match":"Intercont. PO 2 vs Norway","venue":"Boston","time":"6pm ET"},
        {"date":"Jun 22","match":"France vs Intercont. PO 2","venue":"Philadelphia","time":"5pm ET"},
        {"date":"Jun 22","match":"Norway vs Senegal","venue":"New York/NJ","time":"8pm ET"},
        {"date":"Jun 26","match":"Senegal vs Intercont. PO 2","venue":"Toronto","time":"3pm ET"},
        {"date":"Jun 26","match":"Norway vs France","venue":"Boston","time":"3pm ET"},
    ],
    "J": [
        {"date":"Jun 16","match":"Argentina vs Algeria","venue":"Kansas City","time":"9pm ET"},
        {"date":"Jun 16","match":"Austria vs Jordan","venue":"San Francisco","time":"12am ET"},
        {"date":"Jun 21","match":"Argentina vs Austria","venue":"Dallas","time":"1pm ET"},
        {"date":"Jun 22","match":"Algeria vs Jordan","venue":"San Francisco","time":"11pm ET"},
        {"date":"Jun 27","match":"Algeria vs Austria","venue":"Kansas City","time":"3pm ET"},
        {"date":"Jun 27","match":"Jordan vs Argentina","venue":"Dallas","time":"3pm ET"},
    ],
    "K": [
        {"date":"Jun 17","match":"Portugal vs Intercont. PO 1","venue":"Houston","time":"1pm ET"},
        {"date":"Jun 17","match":"Uzbekistan vs Colombia","venue":"Mexico City","time":"10pm ET"},
        {"date":"Jun 23","match":"Portugal vs Uzbekistan","venue":"Houston","time":"1pm ET"},
        {"date":"Jun 23","match":"Colombia vs Intercont. PO 1","venue":"Guadalajara","time":"10pm ET"},
        {"date":"Jun 27","match":"Intercont. PO 1 vs Uzbekistan","venue":"Houston","time":"3pm ET"},
        {"date":"Jun 27","match":"Colombia vs Portugal","venue":"Guadalajara","time":"3pm ET"},
    ],
    "L": [
        {"date":"Jun 17","match":"England vs Croatia","venue":"Dallas","time":"4pm ET"},
        {"date":"Jun 17","match":"Ghana vs Panama","venue":"Toronto","time":"7pm ET"},
        {"date":"Jun 23","match":"England vs Ghana","venue":"Boston","time":"4pm ET"},
        {"date":"Jun 23","match":"Panama vs Croatia","venue":"Toronto","time":"7pm ET"},
        {"date":"Jun 27","match":"Panama vs England","venue":"New York/NJ","time":"3pm ET"},
        {"date":"Jun 27","match":"Croatia vs Ghana","venue":"Dallas","time":"3pm ET"},
    ],
}

KNOCKOUT_DATES = {
    "Round of 32": "Jun 28 – Jul 3, 2026",
    "Round of 16": "Jul 4 – Jul 7, 2026",
    "Quarter-finals": "Jul 9 – Jul 11, 2026",
    "Semi-finals": "Jul 14 – Jul 15, 2026",
    "Third-place playoff": "Jul 18, 2026",
    "FINAL 🏆": "Jul 19, 2026 · MetLife Stadium, New Jersey",
}

VENUES = {
    "MetLife Stadium (New York/NJ)": {"city":"East Rutherford, NJ","capacity":82_500,"host":"Final"},
    "SoFi Stadium (Los Angeles)":    {"city":"Inglewood, CA",    "capacity":70_240,"host":"Semis/QFs"},
    "AT&T Stadium (Dallas)":         {"city":"Arlington, TX",    "capacity":80_000,"host":"SF + QF"},
    "Hard Rock Stadium (Miami)":     {"city":"Miami Gardens, FL","capacity":65_000,"host":"QF"},
    "Levi's Stadium (San Francisco)":{"city":"Santa Clara, CA",  "capacity":68_500,"host":"Groups/R32"},
    "Lincoln Financial (Philadelphia)":{"city":"Philadelphia, PA","capacity":69_796,"host":"Groups/R32"},
    "Arrowhead Stadium (Kansas City)":{"city":"Kansas City, MO", "capacity":76_416,"host":"Groups/R32"},
    "Gillette Stadium (Boston)":     {"city":"Foxborough, MA",   "capacity":65_878,"host":"Groups/R32"},
    "Estadio Azteca (Mexico City)":  {"city":"Mexico City, MX",  "capacity":87_523,"host":"Opening match"},
    "Estadio Akron (Guadalajara)":   {"city":"Guadalajara, MX",  "capacity":49_850,"host":"Groups"},
    "Estadio BBVA (Monterrey)":      {"city":"Monterrey, MX",    "capacity":51_350,"host":"Groups"},
    "BMO Field (Toronto)":           {"city":"Toronto, ON",      "capacity":45_736,"host":"Groups"},
    "BC Place (Vancouver)":          {"city":"Vancouver, BC",    "capacity":54_500,"host":"Groups"},
    "Mercedes-Benz (Atlanta)":       {"city":"Atlanta, GA",      "capacity":72_000,"host":"QF + Groups"},
    "Lumen Field (Seattle)":         {"city":"Seattle, WA",      "capacity":69_000,"host":"Groups"},
    "NRG Stadium (Houston)":         {"city":"Houston, TX",      "capacity":72_220,"host":"Groups/R32"},
}

CONF_COLORS = {
    "UEFA":"#003399","CONMEBOL":"#009933","CONCACAF":"#cc3300",
    "AFC":"#cc9900","CAF":"#006600","OFC":"#660099","Other":"#666666"
}


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────
def win_probability(team_name):
    """Monte Carlo-style win probability based on team attributes."""
    t = TEAMS[team_name]
    # ELO-like score
    score = (
        (101 - t["rank"]) * 0.4 +
        t["titles"]         * 5.0 +
        t["form"]           * 2.0 +
        t["gs"]             * 8.0 +
        (2 - t["gc"])       * 6.0 +
        t["depth"]          * 0.3
    )
    # Convert to implied probability via odds
    implied = 1 / t["odds"] * 100
    # Blend
    raw = score * 0.6 + implied * 0.4
    return round(raw, 2)

# Normalise all probabilities to sum to 100
all_scores = {t: win_probability(t) for t in TEAMS}
total = sum(all_scores.values())
WIN_PROBS = {t: round(v / total * 100, 2) for t, v in all_scores.items()}

def group_advance_prob(team_name):
    """Probability of advancing from group stage (top 2 + best 3rd)."""
    t = TEAMS.get(team_name)
    if not t: return 50.0
    # Based on rank relative to group
    grp = GROUPS.get(t["group"], [])
    ranks = [TEAMS[x]["rank"] for x in grp if x in TEAMS]
    my_rank = t["rank"]
    better = sum(1 for r in ranks if r < my_rank)
    # 0 better = ~85%, 1 better = ~65%, 2 better = ~40%, 3 better = ~20%
    prob = max(10, 90 - better * 25 + (10 - t["rank"]) * 0.1)
    return round(min(95, prob), 1)


# ─────────────────────────────────────────────────────────────
# UI SECTIONS
# ─────────────────────────────────────────────────────────────
def page_overview():
    st.markdown("""
    <div class="wc-header">
        <h1>⚽ 2026 FIFA World Cup</h1>
        <p>June 11 – July 19, 2026 · USA · Canada · Mexico · 48 Teams · 104 Matches</p>
    </div>
    """, unsafe_allow_html=True)

    # Quick stats row
    c1,c2,c3,c4,c5 = st.columns(5)
    for col, val, lbl in [
        (c1,"48","Teams"),
        (c2,"12","Groups"),
        (c3,"104","Matches"),
        (c4,"16","Host Cities"),
        (c5,"39","Days of Football"),
    ]:
        col.markdown(f"""<div class="stat-card"><div class="stat-val">{val}</div>
        <div class="stat-lbl">{lbl}</div></div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-hdr">🗓️ Key Dates</div>', unsafe_allow_html=True)
    cols = st.columns(3)
    for i,(stage,dates) in enumerate(KNOCKOUT_DATES.items()):
        with cols[i%3]:
            st.markdown(f"""<div class="stat-card" style="margin-bottom:8px;text-align:left">
            <div style="font-size:12px;color:var(--color-text-secondary)">{stage}</div>
            <div style="font-size:14px;font-weight:500">{dates}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-hdr">🏆 Top 10 Favourites to Win</div>', unsafe_allow_html=True)
    top10 = sorted(WIN_PROBS.items(), key=lambda x: -x[1])[:10]
    fig = go.Figure()
    names = [t for t,_ in top10]
    probs = [p for _,p in top10]
    flags = [TEAMS[t]["flag"] for t in names]
    colors = [CONF_COLORS[TEAMS[t]["conf"]] for t in names]

    fig.add_trace(go.Bar(
        x=names, y=probs,
        marker_color=colors,
        text=[f"{p:.1f}%" for p in probs],
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Win probability: %{y:.2f}%<extra></extra>",
    ))
    fig.update_layout(
        height=380, margin=dict(l=20,r=20,t=20,b=80),
        yaxis_title="Win Probability (%)",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=12),
        yaxis=dict(gridcolor="rgba(128,128,128,.15)"),
        xaxis=dict(tickangle=-15),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Confederation breakdown
    st.markdown('<div class="section-hdr">🌍 Teams by Confederation</div>', unsafe_allow_html=True)
    conf_counts = {}
    for t,d in TEAMS.items():
        if "Playoff" not in t and "Intercont" not in t:
            c = d["conf"]
            conf_counts[c] = conf_counts.get(c,0) + 1
    fig2 = go.Figure(go.Pie(
        labels=list(conf_counts.keys()),
        values=list(conf_counts.values()),
        hole=0.45,
        marker_colors=[CONF_COLORS[c] for c in conf_counts],
        textinfo="label+value",
    ))
    fig2.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0),
                       paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig2, use_container_width=True)


def page_groups():
    st.markdown('<div class="section-hdr">📋 Group Stage Draw</div>', unsafe_allow_html=True)
    st.caption("12 groups of 4 · Top 2 + 8 best 3rd-place teams advance to Round of 32")

    cols = st.columns(3)
    for i, (grp, teams) in enumerate(GROUPS.items()):
        with cols[i % 3]:
            rows = ""
            for t in teams:
                td = TEAMS.get(t, {})
                flag = td.get("flag","🏳")
                rank = td.get("rank","?")
                adv  = group_advance_prob(t)
                rows += f"""<div class="team-row">
                    <span class="flag">{flag}</span>
                    <span style="flex:1">{t}</span>
                    <span style="font-size:10px;color:var(--color-text-tertiary)">#{rank}</span>
                    <span style="font-size:11px;color:#2563eb;margin-left:6px">{adv}%</span>
                </div>"""
            st.markdown(f"""<div class="group-card">
                <div class="group-title">Group {grp}</div>{rows}</div>
                <br>""", unsafe_allow_html=True)

    st.caption("% = estimated probability of advancing from group stage")


def page_schedule():
    st.markdown('<div class="section-hdr">📅 Match Schedule</div>', unsafe_allow_html=True)

    grp_sel = st.selectbox("Select Group", list(GROUPS.keys()), key="sched_grp")

    matches = GROUP_SCHEDULE.get(grp_sel, [])
    for m in matches:
        st.markdown(f"""
        <div class="match-row">
            <div style="width:60px;font-size:11px;color:var(--color-text-tertiary)">{m['date']}</div>
            <div class="match-teams">{m['match']}</div>
            <div class="match-info">{m['venue']} · {m['time']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-hdr" style="margin-top:2rem">🏟️ Knockout Stage Dates</div>',
                unsafe_allow_html=True)
    for stage,dates in KNOCKOUT_DATES.items():
        st.markdown(f"""<div class="match-row">
            <div style="width:180px;font-weight:500">{stage}</div>
            <div class="match-info">{dates}</div>
        </div>""", unsafe_allow_html=True)


def page_teams():
    st.markdown('<div class="section-hdr">🌐 Team Profiles</div>', unsafe_allow_html=True)

    conf_opts = ["All"] + sorted({d["conf"] for d in TEAMS.values()})
    grp_opts  = ["All"] + list(GROUPS.keys())
    c1,c2,c3 = st.columns(3)
    conf_f = c1.selectbox("Confederation", conf_opts)
    grp_f  = c2.selectbox("Group", grp_opts)
    sort_f = c3.selectbox("Sort by", ["FIFA Rank","Win Probability","Form","Goals Scored"])

    filtered = {
        t:d for t,d in TEAMS.items()
        if "Playoff" not in t and "Intercont" not in t
        and (conf_f=="All" or d["conf"]==conf_f)
        and (grp_f=="All" or d["group"]==grp_f)
    }

    sort_key = {
        "FIFA Rank": lambda x: x[1]["rank"],
        "Win Probability": lambda x: -WIN_PROBS.get(x[0],0),
        "Form": lambda x: -x[1]["form"],
        "Goals Scored": lambda x: -x[1]["gs"],
    }[sort_f]
    filtered = dict(sorted(filtered.items(), key=sort_key))

    st.caption(f"Showing {len(filtered)} teams")

    for t,d in filtered.items():
        with st.expander(f"{d['flag']} {t}  ·  Group {d['group']}  ·  #{d['rank']} FIFA"):
            c1,c2,c3,c4 = st.columns(4)
            c1.metric("FIFA Rank", f"#{d['rank']}")
            c2.metric("World Titles", d["titles"])
            c3.metric("Win Probability", f"{WIN_PROBS.get(t,0):.2f}%")
            c4.metric("Group Advance", f"{group_advance_prob(t)}%")

            st.markdown(f"""
            <div class="kpi-row">
                <div class="kpi-chip">🧑‍💼 Coach: <b>{d['coach']}</b></div>
                <div class="kpi-chip">⭐ Star: <b>{d['star']}</b></div>
                <div class="kpi-chip">🏟️ Confederation: <b>{d['conf']}</b></div>
                <div class="kpi-chip">🎟️ Qualified via: <b>{d['via']}</b></div>
            </div>
            """, unsafe_allow_html=True)

            # Radar chart
            categories = ["Attack","Defense","Form","Depth","Experience"]
            vals = [
                d["gs"]/2.5*100,
                (2-d["gc"])/2*100,
                d["form"]/13*100,
                d["depth"],
                min(100, d["titles"]*15 + (101-d["rank"])*0.5)
            ]
            vals = [max(0,min(100,v)) for v in vals]
            fig = go.Figure(go.Scatterpolar(
                r=vals+[vals[0]], theta=categories+[categories[0]],
                fill="toself", fillcolor=f"{CONF_COLORS[d['conf']]}33",
                line=dict(color=CONF_COLORS[d["conf"]], width=2),
            ))
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0,100])),
                showlegend=False, height=280,
                margin=dict(l=40,r=40,t=20,b=20),
                paper_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig, use_container_width=True)


def page_probability():
    st.markdown('<div class="section-hdr">🎲 Win Probability Calculator</div>',
                unsafe_allow_html=True)

    qualified = [t for t in TEAMS if "Playoff" not in t and "Intercont" not in t]

    st.subheader("Overall tournament win probabilities")
    top_n = st.slider("Show top N teams", 5, 42, 15)
    sorted_probs = sorted(WIN_PROBS.items(), key=lambda x: -x[1])
    top = [(t,p) for t,p in sorted_probs if "Playoff" not in t and "Intercont" not in t][:top_n]

    fig = go.Figure()
    for t,p in top:
        fig.add_trace(go.Bar(
            x=[t], y=[p],
            name=t,
            marker_color=CONF_COLORS[TEAMS[t]["conf"]],
            text=[f"{p:.2f}%"], textposition="outside",
            showlegend=False,
            hovertemplate=f"<b>{TEAMS[t]['flag']} {t}</b><br>Win prob: {p:.2f}%<br>Group: {TEAMS[t]['group']}<extra></extra>",
        ))
    fig.update_layout(
        height=420, margin=dict(l=20,r=20,t=20,b=100),
        yaxis_title="Tournament Win Probability (%)",
        xaxis_tickangle=-30,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(gridcolor="rgba(128,128,128,.15)"),
        bargap=0.2,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Head-to-head matchup predictor")
    c1,c2 = st.columns(2)
    t1 = c1.selectbox("Team 1", qualified, index=qualified.index("Spain") if "Spain" in qualified else 0)
    t2 = c2.selectbox("Team 2", qualified, index=qualified.index("Argentina") if "Argentina" in qualified else 1)

    if t1 and t2 and t1 != t2:
        d1,d2 = TEAMS[t1], TEAMS[t2]
        # H2H model
        score1 = (101-d1["rank"])*0.5 + d1["gs"]*10 + (2-d1["gc"])*8 + d1["form"]*1.5
        score2 = (101-d2["rank"])*0.5 + d2["gs"]*10 + (2-d2["gc"])*8 + d2["form"]*1.5
        total  = score1 + score2
        p1     = score1/total*100
        p2     = score2/total*100
        draw_p = min(25, max(10, 30 - abs(p1-p2)*0.5))
        adj    = (100-draw_p)/100
        p1_win = round(p1*adj, 1)
        p2_win = round(p2*adj, 1)
        draw_p = round(100 - p1_win - p2_win, 1)

        col1,col2,col3 = st.columns(3)
        col1.metric(f"{d1['flag']} {t1} Win", f"{p1_win}%")
        col2.metric("Draw", f"{draw_p}%")
        col3.metric(f"{d2['flag']} {t2} Win", f"{p2_win}%")

        # Bar chart
        fig2 = go.Figure(go.Bar(
            x=[f"{d1['flag']} {t1} Win","Draw",f"{d2['flag']} {t2} Win"],
            y=[p1_win, draw_p, p2_win],
            marker_color=[CONF_COLORS[d1["conf"]],"#888888",CONF_COLORS[d2["conf"]]],
            text=[f"{v}%" for v in [p1_win,draw_p,p2_win]],
            textposition="outside",
        ))
        fig2.update_layout(
            height=320, margin=dict(l=20,r=20,t=10,b=20),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(gridcolor="rgba(128,128,128,.15)", title="Probability (%)"),
        )
        st.plotly_chart(fig2, use_container_width=True)

        # Attribute comparison
        st.markdown("**Attribute comparison**")
        attrs = ["FIFA Rank (inv.)","Goals Scored","Goals Conceded (inv.)","Form","Squad Depth"]
        v1 = [101-d1["rank"], d1["gs"]*40, (2-d1["gc"])*50, d1["form"]*7.5, d1["depth"]]
        v2 = [101-d2["rank"], d2["gs"]*40, (2-d2["gc"])*50, d2["form"]*7.5, d2["depth"]]

        fig3 = go.Figure()
        fig3.add_trace(go.Scatterpolar(r=v1+[v1[0]], theta=attrs+[attrs[0]],
            fill="toself", name=t1, fillcolor=f"{CONF_COLORS[d1['conf']]}44",
            line=dict(color=CONF_COLORS[d1["conf"]], width=2)))
        fig3.add_trace(go.Scatterpolar(r=v2+[v2[0]], theta=attrs+[attrs[0]],
            fill="toself", name=t2, fillcolor=f"{CONF_COLORS[d2['conf']]}44",
            line=dict(color=CONF_COLORS[d2["conf"]], width=2)))
        fig3.update_layout(
            polar=dict(radialaxis=dict(visible=True)),
            height=380, margin=dict(l=60,r=60,t=30,b=30),
            paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1),
        )
        st.plotly_chart(fig3, use_container_width=True)


def page_players():
    st.markdown('<div class="section-hdr">⭐ Player Statistics</div>', unsafe_allow_html=True)

    df = pd.DataFrame(STAR_PLAYERS)

    # Filters
    c1,c2,c3 = st.columns(3)
    pos_f     = c1.selectbox("Position", ["All","FW","MF","DF"])
    sort_col  = c2.selectbox("Sort by", ["rating","market_val_M","wc_goals","age"])
    conf_fp   = c3.selectbox("Confederation", ["All"]+sorted(set(TEAMS.get(p["country"],{}).get("conf","?") for p in STAR_PLAYERS)))

    filtered = df.copy()
    if pos_f != "All":
        filtered = filtered[filtered["pos"]==pos_f]
    if conf_fp != "All":
        filtered = filtered[filtered["country"].map(
            lambda c: TEAMS.get(c,{}).get("conf","?"))==conf_fp]
    filtered = filtered.sort_values(sort_col, ascending=False).reset_index(drop=True)

    # Display as cards
    for _, row in filtered.iterrows():
        wc_goals_str = f"{int(row['wc_goals'])} WC goals" if row['wc_goals']>0 else "WC debut 2026" if row['wc_goals']==0 else ""
        st.markdown(f"""
        <div style="background:var(--color-background-primary);border:0.5px solid var(--color-border-tertiary);
            border-radius:12px;padding:.85rem 1.1rem;margin-bottom:8px;display:flex;align-items:center;gap:16px">
            <div style="font-size:32px">{row['flag']}</div>
            <div style="flex:1">
                <div style="font-weight:600;font-size:15px">{row['name']}</div>
                <div style="font-size:12px;color:var(--color-text-secondary)">{row['country']} · {row['club']} · {row['pos']} · Age {row['age']}</div>
            </div>
            <div class="kpi-row" style="gap:6px">
                <div class="kpi-chip">⭐ Rating: <b>{row['rating']}</b></div>
                <div class="kpi-chip">💰 Value: <b>€{row['market_val_M']}M</b></div>
                <div class="kpi-chip">⚽ {wc_goals_str}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Player comparison")
    p_names = [p["name"] for p in STAR_PLAYERS]
    p1_n = st.selectbox("Player 1", p_names, index=0)
    p2_n = st.selectbox("Player 2", p_names, index=1)

    p1 = next(p for p in STAR_PLAYERS if p["name"]==p1_n)
    p2 = next(p for p in STAR_PLAYERS if p["name"]==p2_n)

    attrs = ["Rating","Market Value (norm)","WC Goals","Age (inv.)","Experience"]
    def norm(p):
        return [
            p["rating"],
            min(100, p["market_val_M"]/2.2),
            min(100, p["wc_goals"]*7),
            max(0, 100 - (p["age"]-16)*2),
            min(100, p["wc_goals"]*5 + (p["rating"]-80)*3)
        ]

    fig = go.Figure()
    for p,color in [(p1,"#2563eb"),(p2,"#cc0000")]:
        v = norm(p)
        fig.add_trace(go.Scatterpolar(
            r=v+[v[0]], theta=attrs+[attrs[0]],
            fill="toself", name=p["name"],
            fillcolor=f"{color}33",
            line=dict(color=color, width=2),
        ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0,100])),
        height=400, margin=dict(l=60,r=60,t=30,b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h",yanchor="bottom",y=1.02),
    )
    st.plotly_chart(fig, use_container_width=True)


def page_venues():
    st.markdown('<div class="section-hdr">🏟️ Host Venues</div>', unsafe_allow_html=True)

    df_v = pd.DataFrame([
        {"Venue":k,"City":v["city"],"Capacity":v["capacity"],"Role":v["host"]}
        for k,v in VENUES.items()
    ]).sort_values("Capacity", ascending=False)

    fig = px.bar(df_v, x="Venue", y="Capacity", color="Role",
                  text="Capacity",
                  color_discrete_sequence=px.colors.qualitative.Set2)
    fig.update_traces(texttemplate="%{text:,}", textposition="outside")
    fig.update_layout(
        height=420, margin=dict(l=20,r=20,t=20,b=160),
        xaxis_tickangle=-30,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(gridcolor="rgba(128,128,128,.15)", title="Capacity"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig, use_container_width=True)

    for venue,(data) in VENUES.items():
        st.markdown(f"""<div class="match-row">
            <div style="width:300px;font-weight:500">{venue}</div>
            <div class="match-info">{data['city']} · Capacity: {data['capacity']:,} · {data['host']}</div>
        </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# SIDEBAR + ROUTER
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:.5rem 0 1rem'>
        <div style='font-size:24px;font-weight:700;font-family:Rajdhani,sans-serif;
            background:linear-gradient(135deg,#003366,#cc0000);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
            background-clip:text'>
            2026 World Cup
        </div>
        <div style='font-size:12px;color:var(--color-text-tertiary)'>
            USA · Canada · Mexico
        </div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio("Navigate", [
        "🏠 Overview",
        "📋 Groups & Draw",
        "📅 Match Schedule",
        "🌐 Team Profiles",
        "🎲 Win Probability",
        "⭐ Player Stats",
        "🏟️ Venues",
    ], label_visibility="collapsed")

    st.markdown("---")
    st.markdown("""
    <div style='font-size:11px;color:var(--color-text-tertiary);line-height:1.8'>
    <b>Data sources</b><br>
    FIFA.com · ESPN · Wikipedia<br>
    Bleacher Report · CBS Sports<br><br>
    <b>Note:</b> 6 playoff spots TBD<br>
    (UEFA + Intercontinental)<br>
    March 2026 · Probabilities<br>
    are model estimates only.
    </div>
    """, unsafe_allow_html=True)

# Route
if   "Overview"     in page: page_overview()
elif "Groups"       in page: page_groups()
elif "Schedule"     in page: page_schedule()
elif "Team"         in page: page_teams()
elif "Probability"  in page: page_probability()
elif "Player"       in page: page_players()
elif "Venues"       in page: page_venues()
