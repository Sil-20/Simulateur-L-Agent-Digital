"""
Simulateur ROI Commercial – Signature+ v4 (Extension complète)
l'agentdigital

Modules :
  0 – Profil prospect
  1 – Situation actuelle
  2 – Module Relance devis (CA perdu / récupérable)
  3 – Module Acquisition client (CA additionnel)
  4 – Vision combinée + ROI global
  5 – Recommandation commerciale
  6 – Scénarios
  7 – Conclusion de rendez-vous
  8 – Export PDF (hérité v3, étendu)

Palette marque : #2A93B5 · #1C2B36 · #F0F8FB
"""

import streamlit as st
import plotly.graph_objects as go
import io, os, base64, json
from datetime import date
from dataclasses import dataclass, field, asdict
from typing import Optional

# ─── ReportLab (PDF) – import optionnel ─────────────────────────────────────────
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable, KeepTogether
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.graphics.shapes import Drawing, Rect, String, Line, Wedge
    from reportlab.graphics import renderPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# ─── CONFIG PAGE ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Simulateur ROI – Signature+ v4",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── PALETTE ────────────────────────────────────────────────────────────────────
BLUE_AD   = "#2A93B5"
BLUE_DARK = "#1C6E8A"
NAVY      = "#1C2B36"
BG_LIGHT  = "#F0F8FB"
BG_WHITE  = "#FFFFFF"
BORDER    = "#CBE8F2"
GRAY_TEXT = "#5A7080"
GRAY_MID  = "#8AACBA"
GREEN     = "#2ECC71"
ORANGE    = "#E67E22"
RED       = "#E74C3C"

# ─── CSS ────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Inter:wght@300;400;500;600&display=swap');

  html, body, [class*="css"] {{
      font-family: 'Inter', sans-serif;
      background-color: {BG_LIGHT};
      color: {NAVY};
  }}
  .main .block-container {{
      padding: 0 2rem 3rem;
      max-width: 1520px;
  }}

  /* HEADER */
  .header-band {{
      background: linear-gradient(135deg, {NAVY} 0%, #234558 60%, {BLUE_DARK} 100%);
      margin: 0 -2rem 2.5rem;
      padding: 2.5rem 3rem 2rem;
      text-align: center;
      position: relative;
      overflow: hidden;
  }}
  .header-band::before {{
      content:""; position:absolute; top:-50px; right:-50px;
      width:260px; height:260px;
      background:radial-gradient(circle,{BLUE_AD}30,transparent 70%);
      border-radius:50%; pointer-events:none;
  }}
  .header-title {{
      font-family:'Syne',sans-serif; font-size:2rem; font-weight:700;
      color:#fff; margin:0 0 .4rem; line-height:1.15;
  }}
  .header-title em {{ color:{BLUE_AD}; font-style:normal; }}
  .header-subtitle {{
      font-size:.76rem; color:{GRAY_MID}; letter-spacing:.12em;
      text-transform:uppercase; font-weight:400;
  }}
  .logo-fallback {{
      font-family:'Syne',sans-serif; font-size:2rem; font-weight:800;
      letter-spacing:.04em; margin-bottom:.9rem;
  }}
  .logo-fallback .accent{{ color:{BLUE_AD}; }}
  .logo-fallback .white {{ color:#fff; }}

  /* SECTION LABELS */
  .section-label {{
      font-size:.68rem; font-weight:600; letter-spacing:.14em;
      text-transform:uppercase; color:{BLUE_AD};
      margin: 1.4rem 0 .8rem;
      padding-bottom:.4rem; border-bottom:2px solid {BORDER};
  }}
  .module-title {{
      font-family:'Syne',sans-serif; font-size:1.15rem; font-weight:700;
      color:{NAVY}; margin: 1.5rem 0 .6rem;
      padding: .5rem 1rem; background:{BG_LIGHT};
      border-left:4px solid {BLUE_AD}; border-radius:0 8px 8px 0;
  }}

  /* KPI CARDS */
  .kpi-card {{
      background:{BG_WHITE}; border:1px solid {BORDER};
      border-left:4px solid {BLUE_AD}; border-radius:10px;
      padding:1rem 1.3rem; margin-bottom:.8rem;
  }}
  .kpi-card-green {{
      background:{BG_WHITE}; border:1px solid #A8E6C3;
      border-left:4px solid {GREEN}; border-radius:10px;
      padding:1rem 1.3rem; margin-bottom:.8rem;
  }}
  .kpi-card-red {{
      background:#FFF8F8; border:1px solid #F5C6C6;
      border-left:4px solid {RED}; border-radius:10px;
      padding:1rem 1.3rem; margin-bottom:.8rem;
  }}
  .kpi-card-orange {{
      background:#FFFBF5; border:1px solid #F5DDB4;
      border-left:4px solid {ORANGE}; border-radius:10px;
      padding:1rem 1.3rem; margin-bottom:.8rem;
  }}
  .kpi-card-highlight {{
      background:linear-gradient(135deg,{BLUE_AD} 0%,{BLUE_DARK} 100%);
      border-radius:12px; padding:1.3rem 1.6rem; margin-bottom:.8rem;
      box-shadow:0 6px 24px {BLUE_AD}44;
  }}
  .kpi-label {{ font-size:.67rem; font-weight:600; letter-spacing:.09em;
      text-transform:uppercase; color:{GRAY_TEXT}; margin-bottom:.3rem; }}
  .kpi-value {{ font-family:'Syne',sans-serif; font-size:1.8rem;
      font-weight:700; color:{NAVY}; line-height:1; }}
  .kpi-value-sm {{ font-family:'Syne',sans-serif; font-size:1.3rem;
      font-weight:700; color:{NAVY}; line-height:1; }}
  .kpi-value-red {{ font-family:'Syne',sans-serif; font-size:1.8rem;
      font-weight:700; color:{RED}; line-height:1; }}
  .kpi-value-green {{ font-family:'Syne',sans-serif; font-size:1.8rem;
      font-weight:700; color:{GREEN}; line-height:1; }}
  .kpi-label-highlight {{ font-size:.67rem; font-weight:600; letter-spacing:.09em;
      text-transform:uppercase; color:rgba(255,255,255,.7); margin-bottom:.3rem; }}
  .kpi-value-highlight {{ font-family:'Syne',sans-serif; font-size:2.4rem;
      font-weight:800; color:#fff; line-height:1; }}
  .kpi-sub {{ font-size:.73rem; color:{GRAY_TEXT}; margin-top:.3rem; }}
  .kpi-sub-highlight {{ font-size:.73rem; color:rgba(255,255,255,.6); margin-top:.3rem; }}

  /* RECO BOX */
  .reco-box {{
      background:linear-gradient(135deg,{NAVY} 0%,#234558 100%);
      border-radius:14px; padding:1.6rem 2rem; margin: 1rem 0;
      color:#fff;
  }}
  .reco-title {{ font-family:'Syne',sans-serif; font-size:1.1rem;
      font-weight:700; color:{BLUE_AD}; margin-bottom:.5rem; }}
  .reco-text {{ font-size:.9rem; line-height:1.65; color:rgba(255,255,255,.88); }}

  /* CONCLUSION */
  .conclusion-box {{
      background:linear-gradient(135deg,{BLUE_AD}18,{BG_LIGHT} 100%);
      border:2px solid {BLUE_AD}; border-radius:14px;
      padding:1.8rem 2.2rem; margin: 1.5rem 0;
  }}
  .conclusion-title {{ font-family:'Syne',sans-serif; font-size:1.15rem;
      font-weight:700; color:{NAVY}; margin-bottom:.8rem; }}
  .conclusion-text {{ font-size:.92rem; line-height:1.75; color:{NAVY}; }}
  .conclusion-text strong {{ color:{BLUE_AD}; }}

  /* OFFRE CARD */
  .offre-card {{
      background:{BG_WHITE}; border:1.5px solid {BORDER};
      border-radius:12px; padding:1.3rem 1.5rem; margin-bottom:.8rem;
      text-align:center;
  }}
  .offre-card-featured {{
      background:linear-gradient(135deg,{BLUE_AD}18,{BG_LIGHT});
      border:2px solid {BLUE_AD}; border-radius:12px;
      padding:1.3rem 1.5rem; margin-bottom:.8rem; text-align:center;
  }}
  .offre-name {{ font-family:'Syne',sans-serif; font-size:1rem;
      font-weight:700; color:{NAVY}; margin-bottom:.4rem; }}
  .offre-price {{ font-family:'Syne',sans-serif; font-size:1.6rem;
      font-weight:800; color:{BLUE_AD}; }}
  .offre-detail {{ font-size:.75rem; color:{GRAY_TEXT}; margin-top:.3rem; line-height:1.5; }}

  /* ERROR */
  .error-box {{
      background:#FFF3F3; border:1px solid {RED};
      border-left:4px solid {RED}; border-radius:8px;
      padding:.7rem 1rem; font-size:.83rem; color:#C62828; margin-bottom:1rem;
  }}
  .warn-box {{
      background:#FFFBF0; border:1px solid {ORANGE};
      border-left:4px solid {ORANGE}; border-radius:8px;
      padding:.7rem 1rem; font-size:.83rem; color:#8B5E02; margin-bottom:1rem;
  }}

  /* FOOTER */
  .footer {{
      margin-top:3rem; padding-top:1.25rem; border-top:1px solid {BORDER};
      font-size:.68rem; color:{GRAY_MID}; text-align:center;
      letter-spacing:.03em; line-height:1.7;
  }}

  /* STREAMLIT OVERRIDES */
  div.stButton > button {{
      background:linear-gradient(135deg,{BLUE_AD} 0%,{BLUE_DARK} 100%);
      color:white; border:none; border-radius:8px;
      font-family:'Inter',sans-serif; font-weight:600; font-size:.88rem;
      padding:.7rem 1.5rem; letter-spacing:.05em; width:100%;
      box-shadow:0 4px 14px {BLUE_AD}55;
  }}
  div.stButton > button:hover {{
      background:linear-gradient(135deg,{BLUE_DARK} 0%,#145E78 100%);
      color:white;
  }}
  div.stDownloadButton > button {{
      background:white; color:{BLUE_AD}; border:2px solid {BLUE_AD};
      border-radius:8px; font-family:'Inter',sans-serif;
      font-weight:600; font-size:.88rem; width:100%; padding:.65rem 1.5rem;
  }}
  div.stDownloadButton > button:hover {{ background:{BLUE_AD}; color:white; }}
  label[data-testid="stWidgetLabel"] p {{
      color:{GRAY_TEXT} !important; font-size:.83rem !important; font-weight:500 !important;
  }}
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# DATACLASSES
# ════════════════════════════════════════════════════════════════════════════════

@dataclass
class ProfilProspect:
    societe: str = ""
    dirigeant: str = ""
    secteur: str = ""
    panier_moyen: float = 8000.0
    marge_brute_pct: float = 30.0
    nb_commerciaux: int = 1
    zone: str = ""
    commentaires: str = ""

@dataclass
class SituationActuelle:
    leads_entrants: int = 40
    leads_qualifies: int = 25
    devis_envoyes: int = 20
    taux_transfo_actuel: float = 25.0  # %
    ventes_signees: int = 5
    ca_mensuel: float = 40000.0
    delai_relance_jours: int = 7
    nb_relances: int = 1
    taux_devis_non_relances: float = 60.0  # %
    delai_contact_lead: int = 3  # jours

@dataclass
class HypothesesRelance:
    amelioration_taux_conversion: float = 5.0   # pts supplém.
    reduction_devis_oublies: float = 70.0        # % de récupération
    scenario: str = "Réaliste"

@dataclass
class HypothesesAcquisition:
    budget_pub: float = 1000.0
    cout_par_clic: float = 2.5
    taux_conversion_lp: float = 8.0      # %
    taux_qualification: float = 60.0     # %
    taux_passage_rdv: float = 70.0       # %
    taux_devis_emis: float = 85.0        # %
    taux_transfo_devis: float = 25.0     # %

@dataclass
class CoutsAgence:
    setup: float = 2500.0
    mensuel: float = 490.0

@dataclass
class ResultatsRelance:
    devis_sous_exploites: float = 0
    ventes_perdues: float = 0
    ca_perdu_mensuel: float = 0
    ca_perdu_annuel: float = 0
    ca_recuperable_prudent: float = 0
    ca_recuperable_realiste: float = 0
    ca_recuperable_ambitieux: float = 0

@dataclass
class ResultatsAcquisition:
    clics: float = 0
    leads: float = 0
    leads_qualifies: float = 0
    devis: float = 0
    ventes: float = 0
    ca_additionnel: float = 0
    marge_brute: float = 0
    cout_par_lead: float = 0
    cout_par_vente: float = 0
    roas: float = 0
    roi_business: float = 0


# ════════════════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════════════════

def fmt(val: float, suffix: str = " €") -> str:
    """Formatage monétaire avec espace comme séparateur de milliers."""
    return f"{val:,.0f}{suffix}".replace(",", " ")

def pct(val: float) -> str:
    return f"{val:.1f} %"

def kpi(label, value, sub="", color="default"):
    card_class = {
        "default": "kpi-card",
        "green": "kpi-card-green",
        "red": "kpi-card-red",
        "orange": "kpi-card-orange",
        "highlight": "kpi-card-highlight",
    }.get(color, "kpi-card")

    val_class = {
        "default": "kpi-value",
        "green": "kpi-value-green",
        "red": "kpi-value-red",
        "orange": "kpi-value",
        "highlight": "kpi-value-highlight",
    }.get(color, "kpi-value")

    lbl_class = "kpi-label-highlight" if color == "highlight" else "kpi-label"
    sub_class = "kpi-sub-highlight" if color == "highlight" else "kpi-sub"

    return f"""
    <div class="{card_class}">
      <div class="{lbl_class}">{label}</div>
      <div class="{val_class}">{value}</div>
      {"" if not sub else f'<div class="{sub_class}">{sub}</div>'}
    </div>"""

def img_to_b64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


# ════════════════════════════════════════════════════════════════════════════════
# CALCULS
# ════════════════════════════════════════════════════════════════════════════════

def calcul_relance(sit: SituationActuelle, hyp: HypothesesRelance, profil: ProfilProspect) -> ResultatsRelance:
    """Module 1 : CA perdu et récupérable via relance."""
    devis_sous_exploites = sit.devis_envoyes * (sit.taux_devis_non_relances / 100)

    # Taux de récupération selon scénario
    # Combien de ces devis oubliés peuvent être convertis ?
    recup_map = {"Prudent": 0.10, "Réaliste": 0.15, "Ambitieux": 0.22}
    taux_recup = recup_map.get(hyp.scenario, 0.15)

    ventes_perdues = devis_sous_exploites * taux_recup
    ca_perdu_mensuel = ventes_perdues * profil.panier_moyen
    ca_perdu_annuel = ca_perdu_mensuel * 12

    # Gain avec relance selon 3 scénarios
    ca_recuperable_prudent    = devis_sous_exploites * 0.10 * profil.panier_moyen
    ca_recuperable_realiste   = devis_sous_exploites * 0.15 * profil.panier_moyen
    ca_recuperable_ambitieux  = devis_sous_exploites * 0.22 * profil.panier_moyen

    return ResultatsRelance(
        devis_sous_exploites=devis_sous_exploites,
        ventes_perdues=ventes_perdues,
        ca_perdu_mensuel=ca_perdu_mensuel,
        ca_perdu_annuel=ca_perdu_annuel,
        ca_recuperable_prudent=ca_recuperable_prudent,
        ca_recuperable_realiste=ca_recuperable_realiste,
        ca_recuperable_ambitieux=ca_recuperable_ambitieux,
    )


def calcul_acquisition(hyp: HypothesesAcquisition, profil: ProfilProspect) -> ResultatsAcquisition:
    """Module 2 : CA additionnel via acquisition client."""
    if hyp.cout_par_clic <= 0:
        return ResultatsAcquisition()

    clics = hyp.budget_pub / hyp.cout_par_clic
    leads = clics * (hyp.taux_conversion_lp / 100)
    leads_qual = leads * (hyp.taux_qualification / 100)
    devis = leads_qual * (hyp.taux_devis_emis / 100)
    ventes = devis * (hyp.taux_transfo_devis / 100)
    ca = ventes * profil.panier_moyen
    marge = ca * (profil.marge_brute_pct / 100)

    cout_par_lead = hyp.budget_pub / leads if leads > 0 else 0
    cout_par_vente = hyp.budget_pub / ventes if ventes > 0 else 0
    roas = ca / hyp.budget_pub if hyp.budget_pub > 0 else 0
    roi_business = (marge - hyp.budget_pub) / hyp.budget_pub if hyp.budget_pub > 0 else 0

    return ResultatsAcquisition(
        clics=clics,
        leads=leads,
        leads_qualifies=leads_qual,
        devis=devis,
        ventes=ventes,
        ca_additionnel=ca,
        marge_brute=marge,
        cout_par_lead=cout_par_lead,
        cout_par_vente=cout_par_vente,
        roas=roas,
        roi_business=roi_business,
    )


def calcul_vision_combinee(rel: ResultatsRelance, acq: ResultatsAcquisition,
                            profil: ProfilProspect, couts: CoutsAgence,
                            hyp_acq: HypothesesAcquisition,
                            scenario: str) -> dict:
    """Module 3 : vision globale combinée."""
    map_ca_rel = {
        "Prudent": rel.ca_recuperable_prudent,
        "Réaliste": rel.ca_recuperable_realiste,
        "Ambitieux": rel.ca_recuperable_ambitieux,
    }
    ca_relance_mensuel = map_ca_rel.get(scenario, rel.ca_recuperable_realiste)
    ca_acquisition_mensuel = acq.ca_additionnel
    ca_total_mensuel = ca_relance_mensuel + ca_acquisition_mensuel
    ca_total_annuel = ca_total_mensuel * 12

    marge_relance = ca_relance_mensuel * (profil.marge_brute_pct / 100)
    marge_acquisition = acq.marge_brute
    marge_totale_mensuel = marge_relance + marge_acquisition

    cout_total_mensuel = couts.mensuel + hyp_acq.budget_pub
    cout_total_annuel = couts.setup + (cout_total_mensuel * 12)

    gain_net_mensuel = marge_totale_mensuel - cout_total_mensuel
    gain_net_annuel = gain_net_mensuel * 12

    # Payback en mois
    payback_mois = couts.setup / gain_net_mensuel if gain_net_mensuel > 0 else None

    # Nb ventes mini pour couvrir abonnement
    ventes_min_mensuel = couts.mensuel / profil.panier_moyen if profil.panier_moyen > 0 else 0

    roi_global = gain_net_annuel / cout_total_annuel if cout_total_annuel > 0 else 0

    return {
        "ca_relance_mensuel": ca_relance_mensuel,
        "ca_acquisition_mensuel": ca_acquisition_mensuel,
        "ca_total_mensuel": ca_total_mensuel,
        "ca_total_annuel": ca_total_annuel,
        "marge_totale_mensuel": marge_totale_mensuel,
        "cout_total_mensuel": cout_total_mensuel,
        "cout_total_annuel": cout_total_annuel,
        "gain_net_mensuel": gain_net_mensuel,
        "gain_net_annuel": gain_net_annuel,
        "payback_mois": payback_mois,
        "ventes_min_mensuel": ventes_min_mensuel,
        "roi_global": roi_global,
    }


def recommandation(sit: SituationActuelle, rel: ResultatsRelance,
                   acq: ResultatsAcquisition, comb: dict) -> tuple[str, str, str]:
    """
    Retourne (titre, explication, couleur) selon les données.
    Règles :
    - Si ca_perdu > ca_acquisition && taux_transfo < 25% → priorité relance
    - Si leads faibles et taux_transfo ok → priorité acquisition
    - Si taux < 15% → retravailler process avant acquisition
    - Sinon → les deux
    """
    taux_transfo = sit.taux_transfo_actuel
    ca_rel = rel.ca_recuperable_realiste
    ca_acq = acq.ca_additionnel

    if taux_transfo < 15:
        return (
            "⚠️ Priorité : Retravailler le traitement commercial",
            "Votre taux de transformation actuel est très faible. Avant d'investir dans l'acquisition de nouveaux leads, il est prioritaire d'optimiser votre processus commercial pour ne pas perdre les demandes que vous recevez déjà. Un système de relance structuré est la première étape.",
            ORANGE
        )
    elif ca_rel > ca_acq * 1.5 and taux_transfo < 30:
        return (
            "🎯 Priorité : Relance & Suivi des devis",
            "Votre plus grand levier de croissance est l'optimisation de votre suivi de devis. Vous perdez potentiellement plus de chiffre d'affaires sur vos devis non relancés que ce que l'acquisition pourrait vous apporter à court terme. Commencez par un système de relance automatique.",
            BLUE_AD
        )
    elif sit.leads_qualifies < 10 and taux_transfo >= 25:
        return (
            "🚀 Priorité : Acquisition de nouveaux leads",
            "Votre taux de transformation est correct, mais le volume de demandes est insuffisant pour développer votre activité. L'acquisition client via publicité ciblée est le levier prioritaire pour vous permettre de croître.",
            GREEN
        )
    else:
        return (
            "💡 Priorité : Les deux leviers en synergie",
            "Votre situation appelle à agir simultanément sur les deux leviers : relancer les devis déjà envoyés pour ne plus perdre de chiffre d'affaires, et générer de nouveaux leads qualifiés pour alimenter votre activité. C'est la combinaison la plus efficace.",
            BLUE_AD
        )


# ════════════════════════════════════════════════════════════════════════════════
# GRAPHIQUES
# ════════════════════════════════════════════════════════════════════════════════

def chart_comparatif_scenarios(rel: ResultatsRelance) -> go.Figure:
    labels = ["Prudent", "Réaliste", "Ambitieux"]
    values = [rel.ca_recuperable_prudent, rel.ca_recuperable_realiste, rel.ca_recuperable_ambitieux]
    colors_list = [GRAY_MID, BLUE_AD, BLUE_DARK]

    fig = go.Figure(go.Bar(
        x=labels, y=values,
        marker_color=colors_list, marker_line_width=0,
        text=[fmt(v) for v in values],
        textposition="inside", insidetextanchor="end",
        textfont=dict(family="Inter", size=11, color="white"),
        width=0.5,
    ))
    fig.update_layout(
        title=dict(text="CA récupérable mensuel selon scénario", font=dict(family="Inter", size=13, color=GRAY_TEXT), x=0),
        paper_bgcolor=BG_WHITE, plot_bgcolor=BG_WHITE,
        margin=dict(t=48, b=28, l=10, r=10),
        yaxis=dict(showgrid=True, gridcolor=BORDER, tickformat=",.0f", ticksuffix=" €",
                   showline=False, zeroline=False, tickfont=dict(family="Inter", size=10, color=GRAY_TEXT)),
        xaxis=dict(tickfont=dict(family="Inter", size=12, color=NAVY)),
        showlegend=False, height=280,
    )
    return fig


def chart_entonnoir_acquisition(acq: ResultatsAcquisition) -> go.Figure:
    stages = ["Clics", "Leads", "Leads qualifiés", "Devis émis", "Ventes"]
    values = [acq.clics, acq.leads, acq.leads_qualifies, acq.devis, acq.ventes]

    fig = go.Figure(go.Funnel(
        y=stages,
        x=[round(v, 1) for v in values],
        marker_color=[BLUE_DARK, BLUE_AD, BLUE_AD, BLUE_AD, GREEN],
        textinfo="value+percent initial",
        textfont=dict(family="Inter", size=11),
    ))
    fig.update_layout(
        title=dict(text="Entonnoir acquisition client", font=dict(family="Inter", size=13, color=GRAY_TEXT), x=0),
        paper_bgcolor=BG_WHITE, plot_bgcolor=BG_WHITE,
        margin=dict(t=48, b=28, l=10, r=10),
        height=300, showlegend=False,
    )
    return fig


def chart_comparatif_leviers(comb: dict) -> go.Figure:
    labels = ["Relance devis seule", "Acquisition seule", "Offre complète"]
    values = [comb["ca_relance_mensuel"], comb["ca_acquisition_mensuel"], comb["ca_total_mensuel"]]

    fig = go.Figure(go.Bar(
        x=labels, y=values,
        marker_color=[ORANGE, GREEN, BLUE_AD],
        marker_line_width=0,
        text=[fmt(v) for v in values],
        textposition="inside", insidetextanchor="end",
        textfont=dict(family="Inter", size=11, color="white"),
        width=0.5,
    ))
    fig.update_layout(
        title=dict(text="Comparatif des leviers – CA additionnel mensuel", font=dict(family="Inter", size=13, color=GRAY_TEXT), x=0),
        paper_bgcolor=BG_WHITE, plot_bgcolor=BG_WHITE,
        margin=dict(t=48, b=28, l=10, r=10),
        yaxis=dict(showgrid=True, gridcolor=BORDER, tickformat=",.0f", ticksuffix=" €",
                   showline=False, zeroline=False, tickfont=dict(family="Inter", size=10, color=GRAY_TEXT)),
        xaxis=dict(tickfont=dict(family="Inter", size=12, color=NAVY)),
        showlegend=False, height=280,
    )
    return fig


def chart_gain_vs_cout(comb: dict) -> go.Figure:
    labels = ["Gain net mensuel", "Coût mensuel total"]
    values = [max(0, comb["gain_net_mensuel"]), comb["cout_total_mensuel"]]
    colors_list = [GREEN if comb["gain_net_mensuel"] > 0 else RED, GRAY_MID]

    fig = go.Figure(go.Bar(
        x=labels, y=values,
        marker_color=colors_list, marker_line_width=0,
        text=[fmt(v) for v in values],
        textposition="inside", insidetextanchor="end",
        textfont=dict(family="Inter", size=12, color="white"),
        width=0.45,
    ))
    fig.update_layout(
        title=dict(text="Gain net vs coût mensuel", font=dict(family="Inter", size=13, color=GRAY_TEXT), x=0),
        paper_bgcolor=BG_WHITE, plot_bgcolor=BG_WHITE,
        margin=dict(t=48, b=28, l=10, r=10),
        yaxis=dict(showgrid=True, gridcolor=BORDER, tickformat=",.0f", ticksuffix=" €",
                   showline=False, zeroline=False),
        showlegend=False, height=280,
    )
    return fig


# ════════════════════════════════════════════════════════════════════════════════
# HEADER
# ════════════════════════════════════════════════════════════════════════════════

def render_header():
    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
    if os.path.exists(logo_path):
        b64 = img_to_b64(logo_path)
        logo_html = f'<img src="data:image/png;base64,{b64}" alt="logo" style="max-height:80px;max-width:300px;object-fit:contain;filter:brightness(0) invert(1);margin-bottom:1rem;" />'
    else:
        logo_html = (
            '<div class="logo-fallback">'
            '<span class="white">l\'</span>'
            '<span class="accent">agent</span>'
            '<span class="white">digital</span>'
            '</div>'
        )

    st.markdown(f"""
    <div class="header-band">
        {logo_html}
        <div class="header-title">Simulateur ROI <em>Signature+</em></div>
        <div class="header-subtitle">Diagnostic commercial · Relance devis · Acquisition client</div>
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# VALIDATION
# ════════════════════════════════════════════════════════════════════════════════

def validations(sit: SituationActuelle, profil: ProfilProspect) -> list[str]:
    errs = []
    if sit.ventes_signees > sit.devis_envoyes:
        errs.append("Le nombre de ventes signées ne peut pas dépasser le nombre de devis envoyés.")
    if sit.devis_envoyes > sit.leads_qualifies:
        errs.append("Le nombre de devis envoyés ne peut pas dépasser le nombre de leads qualifiés.")
    if sit.leads_qualifies > sit.leads_entrants:
        errs.append("Les leads qualifiés ne peuvent pas dépasser les leads entrants.")
    if profil.panier_moyen <= 0:
        errs.append("Le panier moyen doit être positif.")
    if not (0 <= sit.taux_transfo_actuel <= 100):
        errs.append("Le taux de transformation doit être entre 0 et 100 %.")
    ca_calc = sit.ventes_signees * profil.panier_moyen
    if sit.ca_mensuel > 0 and abs(ca_calc - sit.ca_mensuel) / max(sit.ca_mensuel, 1) > 0.4:
        errs.append(f"Le CA mensuel saisi ({fmt(sit.ca_mensuel)}) semble incohérent avec les ventes × panier moyen ({fmt(ca_calc)}). Vérifiez vos données.")
    return errs


# ════════════════════════════════════════════════════════════════════════════════
# EXPORT JSON / RÉSUMÉ TEXTE
# ════════════════════════════════════════════════════════════════════════════════

def generate_resume_texte(profil: ProfilProspect, sit: SituationActuelle,
                           rel: ResultatsRelance, acq: ResultatsAcquisition,
                           comb: dict, scenario: str) -> str:
    map_ca_rel = {
        "Prudent": rel.ca_recuperable_prudent,
        "Réaliste": rel.ca_recuperable_realiste,
        "Ambitieux": rel.ca_recuperable_ambitieux,
    }
    ca_rel = map_ca_rel.get(scenario, rel.ca_recuperable_realiste)
    payback_str = (f"{comb['payback_mois']:.1f} mois" if comb.get("payback_mois") else "Non calculable")
    nom = profil.societe or "l'entreprise"
    txt = f"""== RÉSUMÉ COMMERCIAL – {nom} ==
Date : {date.today().strftime("%d/%m/%Y")}
Scénario retenu : {scenario}

--- SITUATION ACTUELLE ---
Devis envoyés par mois : {sit.devis_envoyes}
Taux de transformation actuel : {pct(sit.taux_transfo_actuel)}
CA mensuel estimé : {fmt(sit.ca_mensuel)}

--- MODULE 1 : RELANCE DEVIS ---
Devis sous-exploités par mois : {rel.devis_sous_exploites:.1f}
CA perdu mensuel estimé : {fmt(rel.ca_perdu_mensuel)}
CA récupérable mensuel (scénario {scenario}) : {fmt(ca_rel)}
CA récupérable annuel (scénario {scenario}) : {fmt(ca_rel * 12)}

--- MODULE 2 : ACQUISITION CLIENT ---
Leads générés / mois : {acq.leads:.1f}
Devis émis / mois : {acq.devis:.1f}
Ventes supplémentaires / mois : {acq.ventes:.1f}
CA additionnel mensuel : {fmt(acq.ca_additionnel)}
Coût par lead : {fmt(acq.cout_par_lead)}
ROAS : {acq.roas:.1f}x

--- VISION COMBINÉE ---
CA additionnel total mensuel : {fmt(comb['ca_total_mensuel'])}
CA additionnel total annuel : {fmt(comb['ca_total_annuel'])}
Marge additionnelle mensuelle : {fmt(comb['marge_totale_mensuel'])}
Gain net mensuel : {fmt(comb['gain_net_mensuel'])}
Coût mensuel total (abonnement + pub) : {fmt(comb['cout_total_mensuel'])}
Délai de rentabilité (payback setup) : {payback_str}
ROI global estimé : {comb['roi_global']:.1f}x

---
Projections théoriques – ne constituent pas une garantie de performance.
"""
    return txt


# ════════════════════════════════════════════════════════════════════════════════
# EXPORT PDF
# ════════════════════════════════════════════════════════════════════════════════

def _fp(val: float, suffix: str = " E") -> str:
    """Formatage PDF : séparateur espace, pas de caractère Unicode exotique."""
    s = f"{int(round(val)):,}".replace(",", " ")
    return s + suffix


def _pdf_bar(labels, values, colors_hex, w_cm=8.0, h_cm=4.5):
    """Mini bar chart ReportLab."""
    from reportlab.graphics.shapes import Drawing, Rect, String
    w, h = w_cm * cm, h_cm * cm
    d = Drawing(w, h)
    mx = max(v for v in values if v > 0) or 1
    bot, top = 0.7 * cm, 0.5 * cm
    ch = h - bot - top
    n = len(values)
    slot = w / n
    bw = slot * 0.52
    for i, (lbl, val, col) in enumerate(zip(labels, values, colors_hex)):
        cx = slot * i + slot / 2
        bh = max(3, (val / mx) * ch)
        d.add(Rect(cx - bw / 2, bot, bw, bh,
                   fillColor=colors.HexColor(col), strokeColor=None))
        d.add(String(cx, bot + bh + 3, _fp(val),
                     fontName="Helvetica-Bold", fontSize=7,
                     fillColor=colors.HexColor(NAVY), textAnchor="middle"))
        d.add(String(cx, 2, lbl,
                     fontName="Helvetica", fontSize=6,
                     fillColor=colors.HexColor(GRAY_TEXT), textAnchor="middle"))
    return d


def generate_pdf_report(profil: ProfilProspect, sit: SituationActuelle,
                         rel: ResultatsRelance, acq: ResultatsAcquisition,
                         comb: dict, scenario: str,
                         forfait_nom: str, budget_pub: float) -> io.BytesIO:
    """Génère un rapport PDF 1-2 pages style Signature+ v3."""
    if not PDF_AVAILABLE:
        raise RuntimeError("reportlab non installé")

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=1.5 * cm, leftMargin=1.5 * cm,
        topMargin=1.6 * cm, bottomMargin=1.8 * cm,
    )

    C_BLUE  = colors.HexColor(BLUE_AD)
    C_NAVY  = colors.HexColor(NAVY)
    C_GRAY  = colors.HexColor(GRAY_TEXT)
    C_BDR   = colors.HexColor(BORDER)
    C_BG    = colors.HexColor(BG_LIGHT)
    C_WHITE = colors.white
    C_GREEN = colors.HexColor(GREEN)
    C_ORANGE= colors.HexColor(ORANGE)

    def ps(name, **kw):
        return ParagraphStyle(name, **kw)

    title_s  = ps("T",  fontSize=16, leading=20, fontName="Helvetica-Bold",
                  textColor=C_NAVY, alignment=TA_CENTER, spaceAfter=2)
    sub_s    = ps("S",  fontSize=8,  leading=10, fontName="Helvetica",
                  textColor=C_GRAY,  alignment=TA_CENTER, spaceAfter=0)
    sec_s    = ps("L",  fontSize=6.5,leading=8,  fontName="Helvetica-Bold",
                  textColor=C_BLUE,  letterSpacing=1.4, spaceBefore=10, spaceAfter=4,
                  alignment=TA_CENTER)
    body_s   = ps("B",  fontSize=8,  leading=12, fontName="Helvetica", textColor=C_NAVY)
    foot_s   = ps("F",  fontSize=6,  leading=8,  fontName="Helvetica",
                  textColor=C_GRAY,  alignment=TA_CENTER)
    concl_s  = ps("C",  fontSize=8.5,leading=13, fontName="Helvetica", textColor=C_NAVY)
    bold_s   = ps("BL", fontSize=8.5,leading=13, fontName="Helvetica-Bold", textColor=C_NAVY)

    story = []

    # ── HEADER ─────────────────────────────────────────────────────────────────
    _lp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
    from reportlab.platypus import Image as RLImage
    if os.path.exists(_lp):
        logo_el = RLImage(_lp, width=4.5*cm, height=2.5*cm, kind="proportional")
    else:
        logo_el = Paragraph("<b>l'agentdigital</b>",
                            ps("LF", fontSize=11, textColor=C_BLUE, fontName="Helvetica-Bold"))

    nom_soc = profil.societe or "Prospect"
    nom_dir = f" – {profil.dirigeant}" if profil.dirigeant else ""
    title_col = Table([
        [Paragraph(f"Simulateur <font color='#2A93B5'>ROI Signature+</font>", title_s)],
        [Paragraph("Diagnostic commercial · Relance devis · Acquisition client", sub_s)],
        [Paragraph(f"{nom_soc}{nom_dir} · {date.today().strftime('%d/%m/%Y')} · Scenario : {scenario}", sub_s)],
    ], colWidths=[13.0*cm])
    title_col.setStyle(TableStyle([
        ("INNERGRID",(0,0),(-1,-1),0,C_WHITE),("BOX",(0,0),(-1,-1),0,C_WHITE),
        ("TOPPADDING",(0,0),(-1,-1),1),("BOTTOMPADDING",(0,0),(-1,-1),1),
        ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
    ]))
    hdr = Table([[logo_el, title_col]], colWidths=[4.2*cm, 13.0*cm])
    hdr.setStyle(TableStyle([
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),("ALIGN",(1,0),(1,0),"CENTER"),
        ("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),0),
        ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
        ("INNERGRID",(0,0),(-1,-1),0,C_WHITE),("BOX",(0,0),(-1,-1),0,C_WHITE),
    ]))
    story.append(hdr)
    story.append(HRFlowable(width="100%", thickness=2, color=C_BLUE, spaceAfter=10, spaceBefore=8))

    # ── KPI HERO (Drawing pur) ──────────────────────────────────────────────────
    map_ca_rel = {"Prudent": rel.ca_recuperable_prudent,
                  "Réaliste": rel.ca_recuperable_realiste,
                  "Ambitieux": rel.ca_recuperable_ambitieux}
    ca_rel_sc = map_ca_rel.get(scenario, rel.ca_recuperable_realiste)
    payback_str = (f"{comb['payback_mois']:.1f} mois" if comb.get("payback_mois") and comb["payback_mois"] > 0 else "—")

    from reportlab.graphics.shapes import Drawing, Rect, String, Line
    def hero_drawing(kpis, w_cm=17.2, h_cm=3.0):
        w, h = w_cm * cm, h_cm * cm
        d = Drawing(w, h)
        d.add(Rect(0, 0, w, h, fillColor=colors.HexColor(BG_LIGHT),
                   strokeColor=C_BLUE, strokeWidth=1.2, rx=3, ry=3))
        cw = w / len(kpis)
        for i, (lbl, val, sub) in enumerate(kpis):
            cx = cw * i
            if i > 0:
                d.add(Line(cx, h*0.08, cx, h*0.92,
                           strokeColor=C_BDR, strokeWidth=0.6))
            px = cx + 10
            d.add(String(px, h - 14, lbl,
                         fontName="Helvetica-Bold", fontSize=6.2,
                         fillColor=C_GRAY))
            d.add(String(px, h - 38, val,
                         fontName="Helvetica-Bold", fontSize=18,
                         fillColor=C_BLUE))
            d.add(String(px, 6, sub,
                         fontName="Helvetica", fontSize=6,
                         fillColor=C_GRAY))
        return d

    hero = hero_drawing([
        ("CA PERDU MENSUEL (RELANCE)",    _fp(rel.ca_perdu_mensuel),       f"Devis non relances : {rel.devis_sous_exploites:.0f}/mois"),
        ("CA RECUPERABLE (sc. {})".format(scenario), _fp(ca_rel_sc),       f"Annuel : {_fp(ca_rel_sc * 12)}"),
        ("CA ADDITIONNEL (ACQUISITION)",  _fp(acq.ca_additionnel),         f"ROAS : {acq.roas:.1f}x · {acq.ventes:.1f} ventes/mois"),
        ("GAIN NET MENSUEL",              _fp(comb['gain_net_mensuel']),    f"Payback setup : {payback_str}"),
    ])
    story.append(hero)
    story.append(Spacer(1, 10))

    # ── SECTION 1 : SITUATION + RELANCE ──────────────────────────────────────
    story.append(Paragraph("MODULE 1 – RELANCE DEVIS", sec_s))

    tbl_base = [
        ("FONTSIZE",(0,0),(-1,-1),7.5),
        ("BACKGROUND",(0,0),(-1,0),BG_LIGHT),
        ("TEXTCOLOR",(0,0),(-1,0),C_NAVY),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("FONTNAME",(0,1),(-1,-1),"Helvetica"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[C_WHITE, colors.HexColor(BG_LIGHT)]),
        ("GRID",(0,0),(-1,-1),0.4,C_BDR),
        ("LEFTPADDING",(0,0),(-1,-1),5),
        ("RIGHTPADDING",(0,0),(-1,-1),5),
        ("TOPPADDING",(0,0),(-1,-1),4),
        ("BOTTOMPADDING",(0,0),(-1,-1),4),
    ]

    sit_data = [
        ["Indicateur", "Valeur"],
        ["Devis envoyes / mois", str(sit.devis_envoyes)],
        ["Taux non relances", f"{sit.taux_devis_non_relances:.0f} %"],
        ["Devis sous-exploites", f"{rel.devis_sous_exploites:.1f}"],
        ["Taux transfo actuel", f"{sit.taux_transfo_actuel:.0f} %"],
        ["CA mensuel actuel", _fp(sit.ca_mensuel)],
    ]
    rel_data = [
        ["Resultat relance", "Valeur"],
        ["CA perdu mensuel",     _fp(rel.ca_perdu_mensuel)],
        ["CA recuperable Prudent",    _fp(rel.ca_recuperable_prudent)],
        ["CA recuperable Realiste",   _fp(rel.ca_recuperable_realiste)],
        ["CA recuperable Ambitieux",  _fp(rel.ca_recuperable_ambitieux)],
        ["CA recuperable annuel (sc.)", _fp(ca_rel_sc * 12)],
    ]
    CW1, CW2 = 3.8*cm, 4.5*cm
    t_sit = Table(sit_data, colWidths=[CW2, CW1])
    t_sit.setStyle(TableStyle(tbl_base))
    t_rel = Table(rel_data, colWidths=[CW2 + 0.3*cm, CW1])
    t_rel.setStyle(TableStyle(tbl_base + [
        ("FONTNAME",(0,2),(0,2),"Helvetica"),
        ("FONTNAME",(0,4),(-1,4),"Helvetica-Bold"),
        ("BACKGROUND",(0,4),(-1,4),colors.HexColor(BLUE_AD)),
        ("TEXTCOLOR",(0,4),(-1,4),C_WHITE),
    ]))

    bar_rel = _pdf_bar(
        ["Prudent", "Realiste", "Ambitieux"],
        [rel.ca_recuperable_prudent, rel.ca_recuperable_realiste, rel.ca_recuperable_ambitieux],
        [GRAY_MID, BLUE_AD, BLUE_DARK], w_cm=5.5, h_cm=4.2,
    )

    row1 = Table([[t_sit, t_rel, bar_rel]],
                 colWidths=[CW2 + CW1 + 0.2*cm, CW2 + 0.3*cm + CW1 + 0.2*cm, 5.8*cm])
    row1.setStyle(TableStyle([
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),4),
        ("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),0),
        ("INNERGRID",(0,0),(-1,-1),0,C_WHITE),("BOX",(0,0),(-1,-1),0,C_WHITE),
    ]))
    story.append(row1)
    story.append(Spacer(1, 10))

    # ── SECTION 2 : ACQUISITION ───────────────────────────────────────────────
    story.append(Paragraph("MODULE 2 – ACQUISITION CLIENT", sec_s))

    acq_data = [
        ["Indicateur", "Valeur"],
        ["Budget pub mensuel",    _fp(budget_pub)],
        ["Clics generes",         f"{acq.clics:.0f}"],
        ["Leads generes",         f"{acq.leads:.1f}"],
        ["Leads qualifies",       f"{acq.leads_qualifies:.1f}"],
        ["Devis emis",            f"{acq.devis:.1f}"],
        ["Ventes generees",       f"{acq.ventes:.1f}"],
        ["CA additionnel",        _fp(acq.ca_additionnel)],
        ["Marge brute",           _fp(acq.marge_brute)],
        ["Cout par lead",         _fp(acq.cout_par_lead)],
        ["ROAS",                  f"{acq.roas:.1f}x"],
    ]
    comb_data = [
        ["Vision combinee", "Valeur"],
        ["CA relance mensuel",    _fp(comb['ca_relance_mensuel'])],
        ["CA acquisition mensuel",_fp(comb['ca_acquisition_mensuel'])],
        ["CA total mensuel",      _fp(comb['ca_total_mensuel'])],
        ["CA total annuel",       _fp(comb['ca_total_annuel'])],
        ["Marge totale mensuelle",_fp(comb['marge_totale_mensuel'])],
        ["Cout mensuel total",    _fp(comb['cout_total_mensuel'])],
        ["Gain net mensuel",      _fp(comb['gain_net_mensuel'])],
        ["Payback setup",         payback_str],
        ["ROI global",            f"{comb['roi_global']:.1f}x"],
        ["Forfait retenu",        forfait_nom],
    ]
    t_acq  = Table(acq_data,  colWidths=[CW2, CW1])
    t_acq.setStyle(TableStyle(tbl_base + [
        ("FONTNAME",(0,-1),(-1,-1),"Helvetica-Bold"),
    ]))
    t_comb = Table(comb_data, colWidths=[CW2 + 0.3*cm, CW1])
    t_comb.setStyle(TableStyle(tbl_base + [
        ("FONTNAME",(0,4),(-1,4),"Helvetica-Bold"),
        ("BACKGROUND",(0,4),(-1,4),colors.HexColor(BLUE_AD)),
        ("TEXTCOLOR",(0,4),(-1,4),C_WHITE),
        ("FONTNAME",(0,-1),(-1,-1),"Helvetica-Bold"),
    ]))

    bar_comb = _pdf_bar(
        ["Relance", "Acquisition", "Total"],
        [comb['ca_relance_mensuel'], comb['ca_acquisition_mensuel'], comb['ca_total_mensuel']],
        [ORANGE, GREEN, BLUE_AD], w_cm=5.5, h_cm=4.2,
    )

    row2 = Table([[t_acq, t_comb, bar_comb]],
                 colWidths=[CW2 + CW1 + 0.2*cm, CW2 + 0.3*cm + CW1 + 0.2*cm, 5.8*cm])
    row2.setStyle(TableStyle([
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),4),
        ("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),0),
        ("INNERGRID",(0,0),(-1,-1),0,C_WHITE),("BOX",(0,0),(-1,-1),0,C_WHITE),
    ]))
    story.append(row2)
    story.append(Spacer(1, 12))

    # ── CONCLUSION AUTO ──────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=1, color=C_BDR, spaceAfter=8))

    nom_affiche = profil.societe or "l'entreprise"
    concl_text = (
        f"D'apres les donnees renseignees, {nom_affiche} perd potentiellement "
        f"{_fp(rel.ca_perdu_mensuel)} de CA par mois faute de relance structuree "
        f"(soit {_fp(rel.ca_perdu_annuel)} / an). "
        f"Un systeme de relance permettrait de recuperer {_fp(ca_rel_sc)} / mois "
        f"(scenario {scenario}). "
        f"En parallele, un systeme d'acquisition avec {_fp(budget_pub)} de budget pub "
        f"genererait {acq.ventes:.1f} ventes et {_fp(acq.ca_additionnel)} de CA additionnel / mois. "
        f"Le gain net mensuel estime est de {_fp(comb['gain_net_mensuel'])} "
        f"pour un cout total de {_fp(comb['cout_total_mensuel'])} / mois. "
        f"Payback du setup : {payback_str}."
    )
    story.append(Paragraph(concl_text, concl_s))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=0.5, color=C_BDR, spaceAfter=4))
    story.append(Paragraph(
        "Projections theoriques basees sur les donnees fournies. Ne constituent pas une garantie de performance.",
        foot_s
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer


# ════════════════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════════════════

def main():
    render_header()

    # ── SIDEBAR : hypothèses avancées ─────────────────────────────────────────
    with st.sidebar:
        st.markdown("### ⚙️ Hypothèses avancées")
        st.caption("Ces valeurs sont modifiables pour affiner la simulation.")

        st.markdown("**Relance devis**")
        scenario = st.selectbox("Scénario global", ["Prudent", "Réaliste", "Ambitieux"], index=1)

        st.markdown("**Coûts agence**")
        # Forfaits fixes de l'agence
        FORFAITS = {
            "Relance devis":      {"setup": 2000.0, "mensuel": 249.0},
            "Acquisition client": {"setup": 2000.0, "mensuel": 549.0},
            "Offre complète":     {"setup": 3700.0, "mensuel": 749.0},
        }
        forfait_choisi = st.selectbox("Forfait agence", list(FORFAITS.keys()), index=2)
        setup   = FORFAITS[forfait_choisi]["setup"]
        mensuel = FORFAITS[forfait_choisi]["mensuel"]
        st.caption(f"Setup : **{fmt(setup)}** · Mensuel : **{fmt(mensuel)}**")

        st.markdown("**Acquisition client**")
        budget_pub = st.number_input("Budget pub mensuel (€)", min_value=0.0, value=1000.0, step=100.0)
        cpc = st.number_input("Coût par clic estimé (€)", min_value=0.1, value=2.5, step=0.1)
        taux_lp = st.slider("Taux de conversion landing page (%)", 1, 30, 8)
        taux_qual = st.slider("Taux de qualification des leads (%)", 10, 100, 60)
        taux_rdv = st.slider("Taux de prise de RDV / contact (%)", 10, 100, 70)
        taux_devis = st.slider("Taux de devis émis (des leads qualifiés) (%)", 10, 100, 85)
        taux_transfo_acq = st.slider("Taux de transformation devis → vente (acq.) (%)", 5, 60, 25)

        st.divider()
        if st.button("🔄 Réinitialiser les hypothèses"):
            st.rerun()

    # ── ONGLETS ───────────────────────────────────────────────────────────────
    tabs = st.tabs([
        "👤 Profil",
        "📊 Situation",
        "🔁 Relance devis",
        "🚀 Acquisition",
        "💡 Vision combinée",
        "✅ Recommandation",
        "📋 Conclusion",
        "🔬 Méthodologie",
    ])

    # ────────────────────────────────────────────────────────────────────────
    # TAB 0 – PROFIL PROSPECT
    # ────────────────────────────────────────────────────────────────────────
    with tabs[0]:
        st.markdown('<div class="module-title">👤 Profil du prospect</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            societe   = st.text_input("Nom de l'entreprise", value="", placeholder="Ex. : Rénovation Martin")
            dirigeant = st.text_input("Nom du dirigeant (optionnel)", value="")
            secteur   = st.text_input("Secteur / Activité", value="Rénovation énergétique",
                                      help="Type de travaux ou activité principale")
        with c2:
            zone          = st.text_input("Zone géographique", value="", placeholder="Ex. : Bordeaux et alentours")
            nb_commerciaux= st.number_input("Personnes traitant les demandes", min_value=1, max_value=50, value=1)
            commentaires  = st.text_area("Commentaires libres", value="", height=80,
                                         placeholder="Notes de rendez-vous, contexte particulier…")

        c3, c4 = st.columns(2)
        with c3:
            panier_moyen  = st.number_input("Panier moyen par chantier (€)", min_value=100.0,
                                            max_value=500000.0, value=8000.0, step=500.0, format="%.0f",
                                            help="Montant moyen d'un chantier signé")
        with c4:
            marge_brute_pct = st.slider("Marge brute estimée (%)", 0, 80, 30,
                                        help="25–35 % est courant en rénovation énergétique")

        profil = ProfilProspect(
            societe=societe, dirigeant=dirigeant, secteur=secteur,
            panier_moyen=panier_moyen, marge_brute_pct=marge_brute_pct,
            nb_commerciaux=nb_commerciaux, zone=zone, commentaires=commentaires
        )

        st.markdown(kpi("Panier moyen", fmt(profil.panier_moyen), f"Marge brute : {marge_brute_pct} %"), unsafe_allow_html=True)

    # ────────────────────────────────────────────────────────────────────────
    # TAB 1 – SITUATION ACTUELLE
    # ────────────────────────────────────────────────────────────────────────
    with tabs[1]:
        st.markdown('<div class="module-title">📊 Situation actuelle</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="section-label">Volume commercial</div>', unsafe_allow_html=True)
            leads_entrants  = st.number_input("Leads entrants / mois", min_value=0, value=40,
                                              help="Total de demandes reçues (formulaire, tel, email…)")
            leads_qualifies = st.number_input("Leads qualifiés / mois", min_value=0, value=25,
                                              help="Demandes qui correspondent à vos critères")
            devis_envoyes   = st.number_input("Devis envoyés / mois", min_value=0, value=20)
            taux_actuel     = st.slider("Taux de transformation devis → vente (%)", 0, 100, 25,
                                        help="Pourcentage de devis transformés en chantiers")
            ventes_signees  = st.number_input("Ventes signées / mois", min_value=0, value=5)
            ca_mensuel      = st.number_input("CA mensuel actuel (€)", min_value=0.0, value=40000.0,
                                              step=1000.0, format="%.0f",
                                              help="Votre chiffre d'affaires moyen mensuel")
        with c2:
            st.markdown('<div class="section-label">Suivi des devis</div>', unsafe_allow_html=True)
            delai_relance = st.number_input("Délai moyen de relance après devis (jours)", min_value=0, value=7,
                                            help="Combien de jours après l'envoi du devis contactez-vous le prospect ?")
            nb_relances   = st.number_input("Nombre moyen de relances effectuées", min_value=0, value=1,
                                            help="Relances téléphoniques ou email effectuées après envoi")
            taux_non_relances = st.slider("Taux de devis jamais relancés (%)", 0, 100, 60,
                                          help="Estimation du % de devis envoyés sans aucune relance")
            delai_contact  = st.number_input("Délai moyen lead → prise de contact (jours)", min_value=0, value=3,
                                             help="Combien de temps avant de contacter un nouveau lead ?")

        sit = SituationActuelle(
            leads_entrants=leads_entrants,
            leads_qualifies=leads_qualifies,
            devis_envoyes=devis_envoyes,
            taux_transfo_actuel=taux_actuel,
            ventes_signees=ventes_signees,
            ca_mensuel=ca_mensuel,
            delai_relance_jours=delai_relance,
            nb_relances=nb_relances,
            taux_devis_non_relances=taux_non_relances,
            delai_contact_lead=delai_contact,
        )

        # Validations
        errs = validations(sit, profil if 'profil' in dir() else ProfilProspect(panier_moyen=8000))
        for err in errs:
            st.markdown(f'<div class="error-box">⚠️ {err}</div>', unsafe_allow_html=True)

        # Synthèse situation
        st.markdown('<div class="section-label">Synthèse de la situation</div>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        ca_calc = ventes_signees * panier_moyen
        with c1: st.markdown(kpi("CA mensuel actuel", fmt(ca_mensuel), f"{ventes_signees} ventes × {fmt(panier_moyen, '')} €"), unsafe_allow_html=True)
        with c2: st.markdown(kpi("Taux transformation", pct(taux_actuel), f"{devis_envoyes} devis → {ventes_signees} ventes"), unsafe_allow_html=True)
        with c3: st.markdown(kpi("Devis non relancés", pct(taux_non_relances), f"≈ {devis_envoyes * taux_non_relances / 100:.0f} devis / mois", color="orange"), unsafe_allow_html=True)
        with c4: st.markdown(kpi("Délai de relance", f"{delai_relance} j", "après envoi du devis", color="orange"), unsafe_allow_html=True)

    # ────────────────────────────────────────────────────────────────────────
    # TAB 2 – MODULE RELANCE
    # ────────────────────────────────────────────────────────────────────────
    with tabs[2]:
        st.markdown('<div class="module-title">🔁 Module 1 : Relance automatique des devis</div>', unsafe_allow_html=True)
        st.caption("Ce module calcule le chiffre d'affaires que vous perdez faute de relances structurées, et ce que vous pourriez récupérer.")

        hyp_rel = HypothesesRelance(scenario=scenario)
        rel = calcul_relance(sit, hyp_rel, profil)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(kpi("Devis sous-exploités / mois", f"{rel.devis_sous_exploites:.1f}",
                            f"{taux_non_relances} % de {devis_envoyes} devis envoyés", color="orange"), unsafe_allow_html=True)
        with c2:
            st.markdown(kpi("CA perdu mensuel estimé", fmt(rel.ca_perdu_mensuel),
                            f"Scénario {scenario}", color="red"), unsafe_allow_html=True)
        with c3:
            st.markdown(kpi("CA perdu annuel estimé", fmt(rel.ca_perdu_annuel),
                            "Si rien ne change", color="red"), unsafe_allow_html=True)

        st.markdown('<div class="section-label">CA récupérable avec relance automatique</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(kpi("Scénario Prudent", fmt(rel.ca_recuperable_prudent),
                            "Taux de récupération : 10 %", color="default"), unsafe_allow_html=True)
            st.markdown(kpi("Annuel Prudent", fmt(rel.ca_recuperable_prudent * 12)), unsafe_allow_html=True)
        with c2:
            st.markdown(kpi("Scénario Réaliste", fmt(rel.ca_recuperable_realiste),
                            "Taux de récupération : 15 %", color="default"), unsafe_allow_html=True)
            st.markdown(kpi("Annuel Réaliste", fmt(rel.ca_recuperable_realiste * 12)), unsafe_allow_html=True)
        with c3:
            st.markdown(kpi("Scénario Ambitieux", fmt(rel.ca_recuperable_ambitieux),
                            "Taux de récupération : 22 %", color="green"), unsafe_allow_html=True)
            st.markdown(kpi("Annuel Ambitieux", fmt(rel.ca_recuperable_ambitieux * 12), color="green"), unsafe_allow_html=True)

        st.plotly_chart(chart_comparatif_scenarios(rel), use_container_width=True,
                        config={"displayModeBar": False})

        with st.expander("ℹ️ Comment ces chiffres sont calculés ?"):
            st.markdown(f"""
**Devis sous-exploités** = devis envoyés × taux de non-relance
= {devis_envoyes} × {taux_non_relances} % = **{rel.devis_sous_exploites:.1f} devis / mois**

**Ventes perdues** = devis sous-exploités × taux de récupération estimé
- Prudent : {rel.devis_sous_exploites:.1f} × 10 % = {rel.devis_sous_exploites * 0.10:.1f} ventes
- Réaliste : {rel.devis_sous_exploites:.1f} × 15 % = {rel.devis_sous_exploites * 0.15:.1f} ventes
- Ambitieux : {rel.devis_sous_exploites:.1f} × 22 % = {rel.devis_sous_exploites * 0.22:.1f} ventes

**CA récupérable** = ventes récupérées × panier moyen ({fmt(panier_moyen)})
""")

    # ────────────────────────────────────────────────────────────────────────
    # TAB 3 – MODULE ACQUISITION
    # ────────────────────────────────────────────────────────────────────────
    with tabs[3]:
        st.markdown('<div class="module-title">🚀 Module 2 : Acquisition client</div>', unsafe_allow_html=True)
        st.caption("Ce module simule le chiffre d'affaires additionnel généré grâce à un système d'acquisition par publicité en ligne.")

        hyp_acq = HypothesesAcquisition(
            budget_pub=budget_pub,
            cout_par_clic=cpc,
            taux_conversion_lp=taux_lp,
            taux_qualification=taux_qual,
            taux_passage_rdv=taux_rdv,
            taux_devis_emis=taux_devis,
            taux_transfo_devis=taux_transfo_acq,
        )
        acq = calcul_acquisition(hyp_acq, profil)

        # Validation : ventes <= devis
        if acq.ventes > acq.devis and acq.devis > 0:
            st.markdown('<div class="error-box">⚠️ Vérification : le nombre de ventes ne peut pas dépasser le nombre de devis émis.</div>', unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(kpi("Clics / mois", f"{acq.clics:.0f}", f"Budget {fmt(budget_pub)} / {cpc} € CPC"), unsafe_allow_html=True)
            st.markdown(kpi("Leads générés", f"{acq.leads:.1f}", f"Taux LP : {taux_lp} %"), unsafe_allow_html=True)
        with c2:
            st.markdown(kpi("Leads qualifiés", f"{acq.leads_qualifies:.1f}", f"Taux qual. : {taux_qual} %"), unsafe_allow_html=True)
            st.markdown(kpi("Devis émis", f"{acq.devis:.1f}", f"Taux devis : {taux_devis} %"), unsafe_allow_html=True)
        with c3:
            st.markdown(kpi("Ventes générées", f"{acq.ventes:.1f}", f"Taux transfo. : {taux_transfo_acq} %", color="green"), unsafe_allow_html=True)
            st.markdown(kpi("Coût par lead", fmt(acq.cout_par_lead), "Budget / leads"), unsafe_allow_html=True)
        with c4:
            st.markdown(kpi("CA additionnel mensuel", fmt(acq.ca_additionnel), color="highlight"), unsafe_allow_html=True)
            st.markdown(kpi("Marge brute additionnelle", fmt(acq.marge_brute), f"{marge_brute_pct} %"), unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(kpi("ROAS", f"{acq.roas:.1f}×", "CA généré / budget pub"), unsafe_allow_html=True)
        with c2:
            st.markdown(kpi("Coût par vente", fmt(acq.cout_par_vente), "Budget pub / ventes"), unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(chart_entonnoir_acquisition(acq), use_container_width=True,
                            config={"displayModeBar": False})
        with c2:
            with st.expander("ℹ️ Détail des calculs", expanded=True):
                st.markdown(f"""
**Clics** = {fmt(budget_pub, '')} € / {cpc} € CPC = **{acq.clics:.0f} clics**
**Leads** = {acq.clics:.0f} × {taux_lp} % = **{acq.leads:.1f} leads**
**Leads qualifiés** = {acq.leads:.1f} × {taux_qual} % = **{acq.leads_qualifies:.1f}**
**Devis émis** = {acq.leads_qualifies:.1f} × {taux_devis} % = **{acq.devis:.1f}**
**Ventes** = {acq.devis:.1f} × {taux_transfo_acq} % = **{acq.ventes:.1f}**
**CA additionnel** = {acq.ventes:.1f} × {fmt(panier_moyen)} = **{fmt(acq.ca_additionnel)}**
**Marge** = {fmt(acq.ca_additionnel)} × {marge_brute_pct} % = **{fmt(acq.marge_brute)}**
""")

    # ────────────────────────────────────────────────────────────────────────
    # TAB 4 – VISION COMBINÉE
    # ────────────────────────────────────────────────────────────────────────
    with tabs[4]:
        st.markdown('<div class="module-title">💡 Module 3 : Vision combinée – ROI global</div>', unsafe_allow_html=True)

        couts = CoutsAgence(setup=setup, mensuel=mensuel)
        comb = calcul_vision_combinee(rel, acq, profil, couts, hyp_acq, scenario)

        payback_str = (f"{comb['payback_mois']:.1f} mois"
                       if comb.get("payback_mois") and comb["payback_mois"] > 0
                       else "Non atteint dans ce scénario")

        # KPIs principaux
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(kpi("CA additionnel – Relance", fmt(comb["ca_relance_mensuel"]),
                            f"Scénario {scenario}", color="orange"), unsafe_allow_html=True)
        with c2:
            st.markdown(kpi("CA additionnel – Acquisition", fmt(comb["ca_acquisition_mensuel"]),
                            f"Budget pub {fmt(budget_pub)}", color="green"), unsafe_allow_html=True)
        with c3:
            st.markdown(kpi("CA additionnel total / mois", fmt(comb["ca_total_mensuel"]),
                            f"Soit {fmt(comb['ca_total_annuel'])} / an", color="highlight"), unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(kpi("Marge additionnelle / mois", fmt(comb["marge_totale_mensuel"]),
                            f"À {marge_brute_pct} %"), unsafe_allow_html=True)
        with c2:
            st.markdown(kpi("Coût mensuel total", fmt(comb["cout_total_mensuel"]),
                            f"Abonnement {fmt(mensuel)} + pub {fmt(budget_pub)}"), unsafe_allow_html=True)
        with c3:
            gain_color = "green" if comb["gain_net_mensuel"] > 0 else "red"
            st.markdown(kpi("Gain net mensuel", fmt(comb["gain_net_mensuel"]),
                            "Marge – coûts", color=gain_color), unsafe_allow_html=True)
        with c4:
            st.markdown(kpi("Payback setup", payback_str,
                            f"Setup : {fmt(setup)}"), unsafe_allow_html=True)

        st.markdown(kpi("ROI global estimé", f"{comb['roi_global']:.1f}×",
                        f"Gain net annuel {fmt(comb['gain_net_annuel'])} / coût total {fmt(comb['cout_total_annuel'])}",
                        color="highlight"), unsafe_allow_html=True)

        # Alerte si ROI négatif
        if comb["gain_net_mensuel"] <= 0:
            st.markdown('<div class="warn-box">⚠️ Dans ce scénario, le gain net est négatif ou nul. Revoyez le budget publicitaire, le panier moyen ou les taux de conversion.</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(chart_comparatif_leviers(comb), use_container_width=True,
                            config={"displayModeBar": False})
        with c2:
            st.plotly_chart(chart_gain_vs_cout(comb), use_container_width=True,
                            config={"displayModeBar": False})

        # Tableau synthèse avant / après
        st.markdown('<div class="section-label">Tableau comparatif avant / après</div>', unsafe_allow_html=True)
        st.table({
            "Indicateur": [
                "CA mensuel",
                "Ventes / mois",
                "CA annuel",
            ],
            "Situation actuelle": [
                fmt(ca_mensuel),
                f"{ventes_signees}",
                fmt(ca_mensuel * 12),
            ],
            "Avec la solution": [
                fmt(ca_mensuel + comb["ca_total_mensuel"]),
                f"{ventes_signees + acq.ventes + rel.ventes_perdues:.1f}",
                fmt((ca_mensuel + comb["ca_total_mensuel"]) * 12),
            ],
        })

        # Offre recommandée
        st.markdown('<div class="section-label">Nos forfaits</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        roi_relance = rel.ca_recuperable_realiste / 249 if 249 > 0 else 0
        roi_acq = acq.ca_additionnel / (549 + budget_pub) if (549 + budget_pub) > 0 else 0
        roi_complet = comb["ca_total_mensuel"] / (749 + budget_pub) if (749 + budget_pub) > 0 else 0
        with c1:
            st.markdown(f"""
            <div class="offre-card">
                <div class="offre-name">Relance devis</div>
                <div class="offre-price">249 € / mois</div>
                <div class="offre-detail">Setup : 2 000 €<br>
                CA récupérable estimé : {fmt(rel.ca_recuperable_realiste)} / mois<br>
                ROI estimé : {roi_relance:.1f}× (scénario réaliste)</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="offre-card-featured">
                <div class="offre-name">⭐ Offre complète</div>
                <div class="offre-price">749 € / mois</div>
                <div class="offre-detail">Setup : 3 700 €<br>
                + Budget pub : {fmt(budget_pub)} / mois<br>
                CA additionnel estimé : {fmt(comb['ca_total_mensuel'])} / mois<br>
                Payback : {payback_str}</div>
            </div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="offre-card">
                <div class="offre-name">Acquisition client</div>
                <div class="offre-price">549 € / mois</div>
                <div class="offre-detail">Setup : 2 000 €<br>
                + Budget pub : {fmt(budget_pub)} / mois<br>
                CA additionnel : {fmt(acq.ca_additionnel)} / mois<br>
                ROAS : {acq.roas:.1f}×</div>
            </div>""", unsafe_allow_html=True)

    # ────────────────────────────────────────────────────────────────────────
    # TAB 5 – RECOMMANDATION
    # ────────────────────────────────────────────────────────────────────────
    with tabs[5]:
        st.markdown('<div class="module-title">✅ Recommandation commerciale</div>', unsafe_allow_html=True)

        titre_reco, txt_reco, _ = recommandation(sit, rel, acq, comb)

        st.markdown(f"""
        <div class="reco-box">
            <div class="reco-title">{titre_reco}</div>
            <div class="reco-text">{txt_reco}</div>
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="section-label">Scénarios automatiques</div>', unsafe_allow_html=True)

        sc_data = {
            "Indicateur": [
                "CA relance mensuel",
                "CA acquisition mensuel",
                "CA total mensuel",
                "Gain net mensuel",
                "ROI global",
            ]
        }

        for sc in ["Prudent", "Réaliste", "Ambitieux"]:
            hyp_r = HypothesesRelance(scenario=sc)
            r_sc = calcul_relance(sit, hyp_r, profil)

            # Ajustements selon scénario
            mult = {"Prudent": 0.7, "Réaliste": 1.0, "Ambitieux": 1.35}[sc]
            hyp_a_sc = HypothesesAcquisition(
                budget_pub=budget_pub,
                cout_par_clic=cpc,
                taux_conversion_lp=min(30, taux_lp * mult),
                taux_qualification=min(100, taux_qual * mult),
                taux_passage_rdv=taux_rdv,
                taux_devis_emis=taux_devis,
                taux_transfo_devis=min(60, taux_transfo_acq * mult),
            )
            a_sc = calcul_acquisition(hyp_a_sc, profil)
            c_sc = calcul_vision_combinee(r_sc, a_sc, profil, couts, hyp_a_sc, sc)

            sc_data[sc] = [
                fmt(c_sc["ca_relance_mensuel"]),
                fmt(c_sc["ca_acquisition_mensuel"]),
                fmt(c_sc["ca_total_mensuel"]),
                fmt(c_sc["gain_net_mensuel"]),
                f"{c_sc['roi_global']:.1f}×",
            ]

        st.table(sc_data)

    # ────────────────────────────────────────────────────────────────────────
    # TAB 6 – CONCLUSION
    # ────────────────────────────────────────────────────────────────────────
    with tabs[6]:
        st.markdown('<div class="module-title">📋 Conclusion de rendez-vous</div>', unsafe_allow_html=True)

        nom_affiche = profil.societe or "l'entreprise"
        map_ca_rel = {
            "Prudent": rel.ca_recuperable_prudent,
            "Réaliste": rel.ca_recuperable_realiste,
            "Ambitieux": rel.ca_recuperable_ambitieux,
        }
        ca_rel_scenario = map_ca_rel.get(scenario, rel.ca_recuperable_realiste)

        payback_concl = (f"{comb['payback_mois']:.0f} mois"
                         if comb.get("payback_mois") and comb["payback_mois"] > 0
                         else "un délai supérieur à l'horizon simulé")

        conclusion_html = f"""
        <div class="conclusion-box">
            <div class="conclusion-title">📌 Synthèse – {nom_affiche}</div>
            <div class="conclusion-text">
                D'après les données renseignées, <strong>{nom_affiche}</strong> perd potentiellement
                <strong>{fmt(rel.ca_perdu_mensuel)}</strong> de chiffre d'affaires par mois à cause d'un suivi
                de devis insuffisant – soit <strong>{fmt(rel.ca_perdu_annuel)}</strong> par an.
                <br><br>
                Un système de relance automatique permettrait de récupérer entre
                <strong>{fmt(rel.ca_recuperable_prudent)}</strong> (scénario prudent) et
                <strong>{fmt(rel.ca_recuperable_ambitieux)}</strong> (scénario ambitieux) par mois,
                soit <strong>{fmt(ca_rel_scenario)}</strong> dans le scénario {scenario} retenu.
                <br><br>
                En parallèle, un système d'acquisition client avec un budget publicitaire de
                <strong>{fmt(budget_pub)}</strong> par mois pourrait générer
                <strong>{acq.ventes:.1f} ventes supplémentaires</strong> et
                <strong>{fmt(acq.ca_additionnel)}</strong> de chiffre d'affaires additionnel mensuel.
                <br><br>
                Le potentiel total estimé se situe entre
                <strong>{fmt(rel.ca_recuperable_prudent + acq.ca_additionnel * 0.7)}</strong> et
                <strong>{fmt(rel.ca_recuperable_ambitieux + acq.ca_additionnel * 1.3)}</strong>
                par mois selon le scénario retenu.
                <br><br>
                Le gain net mensuel estimé est de <strong>{fmt(comb['gain_net_mensuel'])}</strong>
                après déduction des coûts de la solution ({fmt(comb['cout_total_mensuel'])} / mois).
                Le retour sur l'investissement initial (setup) est atteint en
                <strong>{payback_concl}</strong>.
            </div>
        </div>"""

        st.markdown(conclusion_html, unsafe_allow_html=True)

        # Export options
        st.markdown('<div class="section-label">Exports</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)

        resume_txt = generate_resume_texte(profil, sit, rel, acq, comb, scenario)
        with c1:
            st.download_button(
                "📋 Résumé texte",
                data=resume_txt,
                file_name=f"resume_roi_{profil.societe or 'prospect'}_{date.today().isoformat()}.txt",
                mime="text/plain",
            )

        export_data = {
            "date": date.today().isoformat(),
            "profil": asdict(profil),
            "situation": asdict(sit),
            "scenario": scenario,
            "resultats_relance": asdict(rel),
            "resultats_acquisition": asdict(acq),
            "vision_combinee": comb,
        }
        with c2:
            st.download_button(
                "📁 Export JSON",
                data=json.dumps(export_data, ensure_ascii=False, indent=2),
                file_name=f"simulation_{profil.societe or 'prospect'}_{date.today().isoformat()}.json",
                mime="application/json",
            )

        with c3:
            if PDF_AVAILABLE:
                try:
                    pdf_buf = generate_pdf_report(
                        profil, sit, rel, acq, comb, scenario,
                        forfait_choisi, budget_pub,
                    )
                    st.download_button(
                        "📄 Télécharger le rapport PDF",
                        data=pdf_buf,
                        file_name=f"rapport_roi_{profil.societe or 'prospect'}_{date.today().isoformat()}.pdf",
                        mime="application/pdf",
                    )
                except Exception as e:
                    st.warning(f"Export PDF indisponible : {e}")
            else:
                st.info("Installez reportlab pour activer l'export PDF.")

    # ────────────────────────────────────────────────────────────────────────
    # TAB 7 – MÉTHODOLOGIE
    # ────────────────────────────────────────────────────────────────────────
    with tabs[7]:
        st.markdown('<div class="module-title">🔬 Méthodologie & Formules</div>', unsafe_allow_html=True)
        st.markdown("""
### Module 1 – Relance devis

| Variable | Formule |
|---|---|
| Devis sous-exploités | `devis_envoyés × taux_non_relancés` |
| Ventes perdues (réaliste) | `devis_sous_exploités × 15 %` |
| CA perdu mensuel | `ventes_perdues × panier_moyen` |
| CA récupérable prudent | `devis_sous × 10 % × panier` |
| CA récupérable réaliste | `devis_sous × 15 % × panier` |
| CA récupérable ambitieux | `devis_sous × 22 % × panier` |

### Module 2 – Acquisition client

| Variable | Formule |
|---|---|
| Clics | `budget_pub / coût_par_clic` |
| Leads | `clics × taux_conversion_LP` |
| Leads qualifiés | `leads × taux_qualification` |
| Devis émis | `leads_qualifiés × taux_devis_émis` |
| Ventes | `devis × taux_transformation` |
| CA additionnel | `ventes × panier_moyen` |
| Marge brute | `CA × marge_brute_%` |
| Coût par lead | `budget_pub / leads` |
| ROAS | `CA_additionnel / budget_pub` |
| ROI business | `(marge - budget) / budget` |

### Module 3 – Vision combinée

| Variable | Formule |
|---|---|
| CA total mensuel | `CA_relance + CA_acquisition` |
| Marge totale | `marge_relance + marge_acquisition` |
| Coût mensuel total | `abonnement_mensuel + budget_pub` |
| Gain net mensuel | `marge_totale - coût_mensuel` |
| Payback setup | `setup / gain_net_mensuel` |
| ROI global | `gain_net_annuel / coût_total_annuel` |

---
**Hypothèses de récupération sur relance :**
- Prudent : 10 % des devis sous-exploités convertis
- Réaliste : 15 % des devis sous-exploités convertis
- Ambitieux : 22 % des devis sous-exploités convertis

Ces taux sont basés sur les résultats observés en pratique sur des systèmes de relance automatisés dans le secteur des travaux / rénovation.
""")

    # ── FOOTER ───────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="footer">
        l'agentdigital · Simulateur ROI Signature+ v4 · {date.today().strftime("%Y")}<br>
        Projections théoriques – ne constituent pas une garantie de performance commerciale.
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
