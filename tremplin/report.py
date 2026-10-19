"""Génération des exports d'analyse : Markdown lisible et HTML imprimable."""

from __future__ import annotations

import html
from datetime import datetime

from .data_skills import SKILLS


def _esc(value) -> str:
    return html.escape(str(value if value is not None else ""))


def analysis_markdown(result: dict, profile: dict) -> str:
    job = result.get("job", {})
    identity = profile.get("identity", {})
    lines: list[str] = []
    lines.append(f"# Analyse Tremplin — {result.get('job_title','')}")
    lines.append("")
    lines.append(f"**Candidat·e :** {identity.get('name','')} — {identity.get('headline','')}")
    lines.append(f"**Offre :** {job.get('title','')} chez {job.get('company','')} ({job.get('contract','')})")
    lines.append(f"**Date :** {result.get('created_at','')[:16].replace('T',' ')}")
    lines.append("")
    lines.append("## Score global")
    lines.append("")
    lines.append(f"**{result.get('score')}/100 — {result.get('verdict',{}).get('label','')}** (confiance : {result.get('confidence')}%)")
    lines.append("")
    lines.append(result.get("narrative", ""))
    lines.append("")
    lines.append("### Sous-scores")
    for key, value in result.get("subscores", {}).items():
        lines.append(f"- {key} : {value}/100")
    lines.append("")
    lines.append("## Points forts")
    for strength in result.get("strengths", []):
        lines.append(f"- **{strength['title']}** — {strength['detail']}")
    lines.append("")
    lines.append("## Lacunes et priorités")
    for gap in result.get("gaps", [])[:10]:
        lines.append(f"- **{gap['title']}** ({gap['severity']}, +{gap['impact_points']:.0f} pts potentiels) : {gap['why']}")
    lines.append("")
    lines.append("## Plan d'action")
    for phase in (result.get("plan") or {}).get("phases", []):
        lines.append(f"### {phase['title']} ({phase['key']})")
        lines.append(phase.get("subtitle", ""))
        lines.append("")
        for action in phase.get("actions", []):
            resource = action.get("resource") or {}
            resource_text = f" [Ressource : {resource.get('title','')} — {resource.get('url','')}]" if resource else ""
            lines.append(f"- [ ] **{action['title']}** — {action['detail']}{resource_text}")
        lines.append("")
    lines.append("## Conseils CV")
    for tip in result.get("cv_tips", []):
        lines.append(f"- {tip}")
    lines.append("")
    lines.append("## Conseils entretien")
    for tip in result.get("interview_tips", []):
        lines.append(f"- {tip}")
    ai = result.get("ai") or {}
    if ai:
        lines.append("")
        lines.append("## Analyse enrichie par IA")
        if ai.get("narrative"):
            lines.append(ai["narrative"])
        for watchout in ai.get("watchouts", []):
            lines.append(f"- **{watchout.get('title','')}** — {watchout.get('detail','')}")
        if ai.get("pitch"):
            lines.append(f"**Pitch :** {ai['pitch']}")
    lines.append("")
    lines.append("---")
    lines.append("Généré par Tremplin — les ressources citées sont fournies à titre indicatif.")
    return "\n".join(lines)


def analysis_html(result: dict, profile: dict) -> str:
    job = result.get("job", {})
    identity = profile.get("identity", {})
    subscores = result.get("subscores", {})
    score = result.get("score", 0)

    def score_color(value: float) -> str:
        if value >= 80:
            return "#17795E"
        if value >= 65:
            return "#4C9A3F"
        if value >= 50:
            return "#DE9A22"
        return "#E4573D"

    strengths_html = "".join(
        f"<li><strong>{_esc(s['title'])}</strong> — {_esc(s['detail'])}</li>"
        for s in result.get("strengths", [])
    )
    gaps_html = "".join(
        f"<li><strong>{_esc(g['title'])}</strong> <em>({_esc(g['severity'])}, +{g['impact_points']:.0f} pts)</em><br>{_esc(g['why'])}</li>"
        for g in result.get("gaps", [])[:10]
    )
    phases_html = ""
    for phase in (result.get("plan") or {}).get("phases", []):
        actions_html = ""
        for action in phase.get("actions", []):
            resource = action.get("resource") or {}
            resource_html = ""
            if resource:
                resource_html = (
                    f'<div class="res">📚 <a href="{_esc(resource.get("url",""))}">{_esc(resource.get("title",""))}</a>'
                    f' — {_esc(resource.get("provider",""))} · {_esc(resource.get("duration",""))} · {_esc(resource.get("price",""))}</div>'
                )
            actions_html += (
                f'<div class="action"><label><input type="checkbox"> <strong>{_esc(action["title"])}</strong></label>'
                f'<div class="detail">{_esc(action["detail"])}</div>{resource_html}</div>'
            )
        phases_html += (
            f'<h3>{_esc(phase["title"])} <span class="tag">{_esc(phase["key"])}</span></h3>'
            f'<p class="muted">{_esc(phase.get("subtitle",""))}</p>{actions_html}'
        )
    subscores_html = "".join(
        f'<div class="sub"><div class="label">{_esc(key)}</div>'
        f'<div class="bar"><span style="width:{value}%;background:{score_color(value)}"></span></div>'
        f'<div class="value">{value}/100</div></div>'
        for key, value in subscores.items()
    )
    ai = result.get("ai") or {}
    ai_html = ""
    if ai:
        watchouts = "".join(
            f"<li><strong>{_esc(w.get('title',''))}</strong> — {_esc(w.get('detail',''))}</li>"
            for w in ai.get("watchouts", [])
        )
        ai_html = f"""
        <section class="card">
          <h2>Analyse enrichie par IA</h2>
          <p>{_esc(ai.get('narrative',''))}</p>
          <ul>{watchouts}</ul>
          <p><strong>Pitch :</strong> {_esc(ai.get('pitch',''))}</p>
        </section>
        """

    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tremplin — Analyse {_esc(job.get('title',''))}</title>
<style>
  :root {{ --ink:#10231F; --muted:#6E7B76; --line:#E7E4D9; --primary:#17795E; --paper:#F7F6F1; }}
  * {{ box-sizing:border-box; }}
  body {{ font-family:'Segoe UI',system-ui,sans-serif; background:var(--paper); color:var(--ink); margin:0; padding:2.5rem 1rem; }}
  .wrap {{ max-width:860px; margin:0 auto; }}
  .hero {{ background:linear-gradient(125deg,#0B3D2E,#17795E); color:#fff; border-radius:24px; padding:2rem; }}
  .hero .score {{ font-size:3.4rem; font-weight:800; line-height:1; }}
  .hero .verdict {{ font-size:1.1rem; color:#D9F55C; font-weight:700; margin-top:.3rem; }}
  .hero p {{ color:#D7E7DD; margin:.6rem 0 0; }}
  .card {{ background:#fff; border:1px solid var(--line); border-radius:20px; padding:1.3rem 1.5rem; margin-top:1.2rem; }}
  h2 {{ font-size:1.25rem; margin:.2rem 0 .6rem; }}
  h3 {{ margin:1.1rem 0 .2rem; }}
  .tag {{ background:#E4F2EC; color:#0E5B45; border-radius:999px; padding:.1rem .5rem; font-size:.72rem; vertical-align:middle; }}
  .muted {{ color:var(--muted); }}
  .sub {{ display:grid; grid-template-columns:150px 1fr 60px; gap:.7rem; align-items:center; margin:.35rem 0; font-size:.88rem; }}
  .sub .label {{ font-weight:700; }}
  .sub .value {{ text-align:right; color:var(--muted); }}
  .bar {{ height:9px; background:#ECE9DF; border-radius:999px; overflow:hidden; }}
  .bar span {{ display:block; height:100%; border-radius:999px; }}
  .action {{ border:1px solid var(--line); border-left:4px solid var(--primary); border-radius:12px; padding:.6rem .8rem; margin:.45rem 0; }}
  .action .detail {{ color:#3D4C46; font-size:.87rem; margin:.25rem 0 0 1.4rem; }}
  .res {{ font-size:.8rem; color:var(--muted); margin:.3rem 0 0 1.4rem; }}
  a {{ color:var(--primary); }}
  li {{ margin:.35rem 0; font-size:.92rem; }}
  ul {{ padding-left:1.2rem; }}
  footer {{ color:var(--muted); font-size:.78rem; text-align:center; margin-top:2rem; }}
</style>
</head>
<body>
<div class="wrap">
  <div class="hero">
    <div style="text-transform:uppercase;letter-spacing:.14em;font-size:.72rem;color:#D9F55C;font-weight:800">Tremplin · Analyse de compatibilité</div>
    <div class="score">{_esc(score)}<span style="font-size:1.2rem;font-weight:600">/100</span></div>
    <div class="verdict">{_esc(result.get('verdict',{}).get('label',''))}</div>
    <p>{_esc(result.get('narrative',''))}</p>
  </div>

  <section class="card">
    <h2>Candidat·e &amp; offre</h2>
    <p><strong>{_esc(identity.get('name',''))}</strong> — {_esc(identity.get('headline',''))}</p>
    <p><strong>Offre :</strong> {_esc(job.get('title',''))} — {_esc(job.get('company',''))} ({_esc(job.get('contract',''))}, {_esc(job.get('location',''))})</p>
    <p class="muted">Analyse générée le {_esc(result.get('created_at','')[:16].replace('T',' '))} · Confiance : {_esc(result.get('confidence',''))}% · Score projeté après plan : {_esc(result.get('projected_score','—'))}/100</p>
  </section>

  <section class="card">
    <h2>Détail du score</h2>
    {subscores_html}
  </section>

  <section class="card">
    <h2>Points forts</h2>
    <ul>{strengths_html or '<li>À construire : complète ton profil.</li>'}</ul>
  </section>

  <section class="card">
    <h2>Lacunes prioritaires</h2>
    <ul>{gaps_html or '<li>Aucune lacune majeure : prépare l\'entretien.</li>'}</ul>
  </section>

  <section class="card">
    <h2>Plan d'action 7 / 30 / 90 jours</h2>
    {phases_html}
  </section>

  <section class="card">
    <h2>Conseils CV</h2>
    <ul>{''.join(f'<li>{_esc(t)}</li>' for t in result.get('cv_tips', []))}</ul>
    <h2>Conseils entretien</h2>
    <ul>{''.join(f'<li>{_esc(t)}</li>' for t in result.get('interview_tips', []))}</ul>
  </section>

  {ai_html}

  <footer>Généré par Tremplin · {_esc(datetime.now().strftime('%d/%m/%Y %H:%M'))} · Les ressources citées sont fournies à titre indicatif.</footer>
</div>
</body>
</html>"""
