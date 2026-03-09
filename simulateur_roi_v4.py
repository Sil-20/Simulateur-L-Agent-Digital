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

def _fe_draw(val: float) -> str:
    """Formatage nombre pour Drawing — séparateur point (ASCII safe)."""
    if val == 0:
        return "0"
    parts = []
    n = int(round(val))
    while n >= 1000:
        parts.append(f"{n % 1000:03d}")
        n //= 1000
    parts.append(str(n))
    return ".".join(reversed(parts))


def _fe_plain(val: float) -> str:
    """Version ASCII pure, séparateur espace ordinaire, sans symbole."""
    if val == 0:
        return "0"
    return f"{int(round(val)):,}".replace(",", " ")


def _euro(val: float) -> str:
    """Retourne la chaîne formatée avec 'EUR' en suffixe (100% ASCII safe)."""
    return _fe_plain(val) + " EUR"


def _pct_str(val: float) -> str:
    return f"{val:.0f} %"


# ── Primitive : rectangle arrondi simulé (ReportLab ne supporte rx/ry que depuis
#    certaines versions, on fait un rectangle plein classique avec border-radius
#    visuel obtenu via strokeWidth et couleur)
def _rounded_rect(d, x, y, w, h, fill_hex, stroke_hex=None, sw=0):
    from reportlab.graphics.shapes import Rect
    d.add(Rect(x, y, w, h,
               fillColor=colors.HexColor(fill_hex),
               strokeColor=colors.HexColor(stroke_hex) if stroke_hex else colors.HexColor(fill_hex),
               strokeWidth=sw, rx=4, ry=4))


def _pdf_bar_chart(labels, values, bar_colors, title, w_cm=8.5, h_cm=4.8):
    """Bar chart propre avec titre, valeurs au-dessus et libellés en bas."""
    from reportlab.graphics.shapes import Drawing, Rect, String, Line
    w, h = w_cm * cm, h_cm * cm
    d = Drawing(w, h)

    # Fond blanc
    d.add(Rect(0, 0, w, h, fillColor=colors.white, strokeColor=colors.HexColor(BORDER), strokeWidth=0.5))

    # Titre
    d.add(String(w / 2, h - 11, title,
                 fontName="Helvetica-Bold", fontSize=7.5,
                 fillColor=colors.HexColor(NAVY), textAnchor="middle"))

    mx = max(v for v in values if v > 0) or 1
    bottom = 1.2 * cm
    top_pad = 0.6 * cm
    chart_h = h - bottom - top_pad - 14

    n = len(values)
    slot = w / n
    bw = slot * 0.52

    for i, (lbl, val, col) in enumerate(zip(labels, values, bar_colors)):
        cx = slot * i + slot / 2
        bh = max(4, (val / mx) * chart_h)
        by = bottom

        # Grille horizontale légère
        if i == 0:
            for pct_line in [0.25, 0.5, 0.75, 1.0]:
                ly = bottom + pct_line * chart_h
                d.add(Line(0, ly, w, ly, strokeColor=colors.HexColor(BORDER), strokeWidth=0.4))

        # Barre
        d.add(Rect(cx - bw / 2, by, bw, bh,
                   fillColor=colors.HexColor(col), strokeColor=None, rx=2, ry=2))

        # Valeur au-dessus en gras
        v_str = _fe_draw(val)
        d.add(String(cx, by + bh + 5, v_str,
                     fontName="Helvetica-Bold", fontSize=7,
                     fillColor=colors.HexColor(NAVY), textAnchor="middle"))

        # Label en bas
        d.add(String(cx, 5, lbl,
                     fontName="Helvetica-Bold", fontSize=7,
                     fillColor=colors.HexColor(GRAY_TEXT), textAnchor="middle"))

    return d


def _pdf_pie_chart(labels, values, slice_colors, title, w_cm=5.8, h_cm=5.8):
    """Donut chart pour répartition devis relancés vs non relancés."""
    from reportlab.graphics.shapes import Drawing, String, Circle, Rect
    from reportlab.graphics.charts.piecharts import Pie
    w, h = w_cm * cm, h_cm * cm
    d = Drawing(w, h)

    # Fond blanc
    d.add(Rect(0, 0, w, h, fillColor=colors.white, strokeColor=colors.HexColor(BORDER), strokeWidth=0.5))

    total = sum(values) or 1
    title_h = 16
    legend_h = 22
    available_h = h - title_h - legend_h
    cx = w / 2
    cy = legend_h + available_h / 2
    radius = min(w / 2, available_h / 2) * 0.80

    pie = Pie()
    pie.x = cx - radius
    pie.y = cy - radius
    pie.width = 2 * radius
    pie.height = 2 * radius
    pie.data = values
    pie.labels = [''] * len(values)
    pie.simpleLabels = True
    pie.sideLabels = False
    pie.startAngle = 90
    pie.direction = 'clockwise'
    for idx, col in enumerate(slice_colors):
        pie.slices[idx].fillColor = colors.HexColor(col)
        pie.slices[idx].strokeColor = colors.white
        pie.slices[idx].strokeWidth = 2
        pie.slices[idx].popout = 0
    d.add(pie)

    # Cercle central blanc (donut)
    inner_r = radius * 0.52
    d.add(Circle(cx, cy, inner_r, fillColor=colors.white, strokeColor=colors.white, strokeWidth=0))

    # Pourcentage central (valeur 0 = non relancés)
    pct0 = values[0] / total * 100
    d.add(String(cx, cy + 5, f"{pct0:.0f}%",
                 fontName="Helvetica-Bold", fontSize=13,
                 fillColor=colors.HexColor(ORANGE), textAnchor="middle"))
    d.add(String(cx, cy - 9, "non rel.",
                 fontName="Helvetica", fontSize=6,
                 fillColor=colors.HexColor(GRAY_TEXT), textAnchor="middle"))

    # Titre
    d.add(String(w / 2, h - 11, title,
                 fontName="Helvetica-Bold", fontSize=7.5,
                 fillColor=colors.HexColor(NAVY), textAnchor="middle"))

    # Légende en bas
    sw = w / len(labels)
    for idx, (lbl, col) in enumerate(zip(labels, slice_colors)):
        lx = idx * sw + 4
        d.add(Rect(lx, 6, 7, 7, fillColor=colors.HexColor(col), strokeColor=None))
        pct_v = values[idx] / total * 100
        d.add(String(lx + 10, 7, f"{lbl} ({pct_v:.0f}%)",
                     fontName="Helvetica", fontSize=5.5,
                     fillColor=colors.HexColor(GRAY_TEXT)))
    return d


def _pdf_funnel_chart(labels, values, w_cm=5.8, h_cm=12.0):
    """Funnel chart entonnoir acquisition : Clics → Ventes."""
    from reportlab.graphics.shapes import Drawing, Rect, String, Line
    w, h = w_cm * cm, h_cm * cm
    d = Drawing(w, h)

    # Fond blanc
    d.add(Rect(0, 0, w, h, fillColor=colors.white, strokeColor=colors.HexColor(BORDER), strokeWidth=0.5))

    # Titre
    d.add(String(w / 2, h - 11, "Entonnoir acquisition client",
                 fontName="Helvetica-Bold", fontSize=7.5,
                 fillColor=colors.HexColor(NAVY), textAnchor="middle"))

    n = len(labels)
    mx = values[0] if values[0] > 0 else 1
    title_h = 16
    bar_area_h = h - title_h - 8
    slot_h = bar_area_h / n
    bar_h = slot_h * 0.68
    max_bar_w = w * 0.60

    bar_colors_funnel = [BLUE_DARK, BLUE_AD, BLUE_AD, BLUE_AD, GREEN]

    for i, (lbl, val) in enumerate(zip(labels, values)):
        col = bar_colors_funnel[i] if i < len(bar_colors_funnel) else BLUE_AD
        # Position Y (de haut en bas)
        top_y = h - title_h - 8 - i * slot_h
        bot_y = top_y - bar_h

        # Largeur proportionnelle à la valeur
        bw = max(max_bar_w * 0.10, (val / mx) * max_bar_w)
        bx = 4

        # Barre
        d.add(Rect(bx, bot_y, bw, bar_h,
                   fillColor=colors.HexColor(col), strokeColor=None, rx=2, ry=2))

        # % par rapport au premier
        pct = val / mx * 100
        pct_str = "100%" if i == 0 else f"{pct:.0f}%"

        # Label
        val_display = f"{int(round(val))}" if val >= 10 else f"{val:.1f}"
        d.add(String(bx + bw + 5, bot_y + bar_h * 0.28,
                     f"{lbl}: {val_display}",
                     fontName="Helvetica-Bold", fontSize=6.5,
                     fillColor=colors.HexColor(NAVY)))

        # % à droite
        d.add(String(w - 4, bot_y + bar_h * 0.28, pct_str,
                     fontName="Helvetica", fontSize=6,
                     fillColor=colors.HexColor(GRAY_TEXT), textAnchor="end"))

        # Flèche/ligne entre étapes
        if i < n - 1:
            mid_x = bx + max_bar_w * 0.3
            d.add(Line(mid_x, bot_y, mid_x, bot_y - (slot_h - bar_h) + 2,
                       strokeColor=colors.HexColor(BORDER), strokeWidth=1))

    return d


def _kpi_block_drawing(kpis, w_cm=17.5, h_cm=3.2):
    """
    4 blocs KPI côte à côte sur fond dégradé simulé.
    kpis = list of (label, value_str, sub_str, accent_color_hex)
    """
    from reportlab.graphics.shapes import Drawing, Rect, String, Line
    w, h = w_cm * cm, h_cm * cm
    d = Drawing(w, h)

    # Fond global bleu marine
    _rounded_rect(d, 0, 0, w, h, NAVY, NAVY, 0)

    n = len(kpis)
    cw = w / n
    pad = 12

    for i, (label, value, sub, accent) in enumerate(kpis):
        x0 = cw * i

        # Séparateur entre blocs (sauf premier)
        if i > 0:
            d.add(Line(x0, h * 0.1, x0, h * 0.9,
                       strokeColor=colors.HexColor("#2A4558"), strokeWidth=1))

        # Accent strip en haut du bloc
        d.add(Rect(x0 + pad, h - 5, cw - pad * 2, 3,
                   fillColor=colors.HexColor(accent), strokeColor=None))

        # Label (petit, gris clair)
        d.add(String(x0 + pad, h - 20, label,
                     fontName="Helvetica-Bold", fontSize=6,
                     fillColor=colors.HexColor("#8AACBA")))

        # Valeur principale (grande, colorée)
        d.add(String(x0 + pad, h - 54, value,
                     fontName="Helvetica-Bold", fontSize=20,
                     fillColor=colors.HexColor(accent)))

        # Sous-texte (tronqué si trop long pour le bloc)
        max_chars = int(cw / (5.5))  # ~5.5 pts par caractère à fontSize 6
        sub_display = sub if len(sub) <= max_chars else sub[:max_chars - 2] + ".."
        d.add(String(x0 + pad, 8, sub_display,
                     fontName="Helvetica", fontSize=6,
                     fillColor=colors.HexColor("#8AACBA")))

    return d


def _section_header_drawing(title, w_cm=17.5, h_cm=0.7):
    """Bandeau de section avec fond bleu et texte blanc centré."""
    from reportlab.graphics.shapes import Drawing, Rect, String
    w, h = w_cm * cm, h_cm * cm
    d = Drawing(w, h)
    _rounded_rect(d, 0, 0, w, h, BLUE_AD, BLUE_AD, 0)
    d.add(String(w / 2, h / 2 - 4, title,
                 fontName="Helvetica-Bold", fontSize=8,
                 fillColor=colors.white, textAnchor="middle"))
    return d


def _make_table(data, col_widths, highlight_rows=None, value_col=1):
    """
    Crée un tableau stylé. highlight_rows = liste d'index de lignes à surligner.
    La ligne 0 est toujours l'en-tête : fond blanc, texte bleu AD, souligné.
    """
    n_rows = len(data)
    style = [
        # En-tête : fond blanc pur, texte BLUE_AD gras, souligné fort
        ("BACKGROUND",    (0, 0), (-1, 0),  colors.white),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  colors.HexColor(BLUE_AD)),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0),  8.5),
        ("TOPPADDING",    (0, 0), (-1, 0),  8),
        ("BOTTOMPADDING", (0, 0), (-1, 0),  8),
        # Trait fort sous l'en-tête couleur BLUE_AD
        ("LINEBELOW",     (0, 0), (-1, 0),  1.5, colors.HexColor(BLUE_AD)),
        # Bordure gauche sur l'en-tête pour l'accent visuel
        ("LINEBEFORE",    (0, 0), (0, 0),   3,   colors.HexColor(BLUE_AD)),
        # Corps
        ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 1), (-1, -1), 8.5),
        ("TOPPADDING",    (0, 1), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 7),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 7),
        # Alternance de fond très douce : blanc / quasi blanc
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, colors.HexColor("#F5FBFD")]),
        # Grille fine
        ("LINEBELOW",     (0, 1), (-1, -2), 0.3, colors.HexColor(BORDER)),
        ("LINEBELOW",     (0, -1),(-1, -1), 0.3, colors.HexColor(BORDER)),
        # Bordure extérieure légère
        ("BOX",           (0, 0), (-1, -1), 0.5, colors.HexColor(BORDER)),
        # Alignement droite colonne valeur
        ("ALIGN",         (value_col, 0), (value_col, -1), "RIGHT"),
        ("FONTNAME",      (value_col, 1), (value_col, -1), "Helvetica-Bold"),
        ("TEXTCOLOR",     (value_col, 1), (value_col, -1), colors.HexColor(NAVY)),
    ]
    # Lignes surlignées : bleu AD avec texte blanc
    if highlight_rows:
        for r in highlight_rows:
            if 0 < r < n_rows:
                style += [
                    ("BACKGROUND", (0, r), (-1, r), colors.HexColor(BLUE_AD)),
                    ("TEXTCOLOR",  (0, r), (-1, r), colors.white),
                    ("FONTNAME",   (0, r), (-1, r), "Helvetica-Bold"),
                ]
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle(style))
    return t


def generate_pdf_report(profil: ProfilProspect, sit: SituationActuelle,
                         rel: ResultatsRelance, acq: ResultatsAcquisition,
                         comb: dict, scenario: str,
                         forfait_nom: str, budget_pub: float) -> io.BytesIO:
    """
    Rapport PDF 2 pages - design epure inspire Signature+ v3.
    Page 1 : Header · KPI Hero · Module Relance (graphiques + tableaux cote a cote)
    Page 2 : Header · Module Acquisition (entonnoir + camembert + tableaux) · Conclusion
    """
    if not PDF_AVAILABLE:
        raise RuntimeError("reportlab non installe")

    from reportlab.platypus import Image as RLImage, PageBreak
    from reportlab.graphics.shapes import Drawing, Rect, String, Line, Wedge
    import math

    # ── Mise en page (marges genereux pour aerer comme v3) ───────────────────
    buffer = io.BytesIO()
    LM = RM = 1.6 * cm
    TM = 1.4 * cm
    BM = 1.6 * cm
    PW = A4[0] - LM - RM          # ~18.1 cm

    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=LM, rightMargin=RM,
        topMargin=TM, bottomMargin=BM,
    )

    # ── Palette monochromatique #2A93B5 ──────────────────────────────────────
    # Toutes les couleurs derivent de #2A93B5 - pas de vert, pas d'orange
    C_BLUE   = colors.HexColor("#2A93B5")   # bleu principal
    C_BLUE2  = colors.HexColor("#1C6E8A")   # bleu fonce
    C_BLUE3  = colors.HexColor("#5BB3CC")   # bleu moyen
    C_BLUE4  = colors.HexColor("#A8D8E8")   # bleu clair
    C_BLUE5  = colors.HexColor("#D6EEF5")   # bleu tres clair (fond KPI)
    C_NAVY   = colors.HexColor(NAVY)
    C_GRAY   = colors.HexColor(GRAY_TEXT)
    C_BDR    = colors.HexColor(BORDER)
    C_BG     = colors.HexColor(BG_LIGHT)
    C_WHITE  = colors.white
    # Alias graphiques - palette bleue uniquement
    COL_BAR1 = "#A8D8E8"   # barre Prudent  – bleu tres clair
    COL_BAR2 = "#2A93B5"   # barre Realiste – bleu principal
    COL_BAR3 = "#1C6E8A"   # barre Ambitieux – bleu fonce
    COL_PIE1 = "#5BB3CC"   # 1ere part camembert
    COL_PIE2 = "#1C6E8A"   # 2e part camembert
    COL_FUN  = ["#1C6E8A", "#2A93B5", "#2A93B5", "#2A93B5", "#5BB3CC"]  # entonnoir

    # ── Styles texte ─────────────────────────────────────────────────────────
    def ps(name, **kw):
        return ParagraphStyle(name, **kw)

    title_s  = ps("TI", fontSize=16, leading=20, fontName="Helvetica-Bold",
                  textColor=C_NAVY, alignment=TA_CENTER, spaceAfter=0)
    sub_s    = ps("SU", fontSize=7.5, leading=10, fontName="Helvetica",
                  textColor=C_GRAY, alignment=TA_CENTER, spaceAfter=0)
    client_s = ps("CL", fontSize=7.5, leading=10, fontName="Helvetica",
                  textColor=C_GRAY, alignment=TA_CENTER, spaceAfter=0)
    sec_s    = ps("SE", fontSize=6.5, leading=8, fontName="Helvetica-Bold",
                  textColor=C_BLUE, alignment=TA_CENTER,
                  spaceBefore=0, spaceAfter=5, letterSpacing=1.2)
    foot_s   = ps("FO", fontSize=6, leading=8, fontName="Helvetica",
                  textColor=C_GRAY, alignment=TA_CENTER)
    concl_s  = ps("CO", fontSize=8.5, leading=14, fontName="Helvetica",
                  textColor=C_NAVY, spaceAfter=0)

    # ── Donnees communes ─────────────────────────────────────────────────────
    _lp       = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
    nom_soc   = profil.societe or ""
    nom_dir   = profil.dirigeant or ""
    date_str  = date.today().strftime("%d/%m/%Y")

    map_ca    = {
        "Prudent":   rel.ca_recuperable_prudent,
        "Realiste":  rel.ca_recuperable_realiste,
        "Realist":   rel.ca_recuperable_realiste,
        "Realiste":  rel.ca_recuperable_realiste,
        "Ambitieux": rel.ca_recuperable_ambitieux,
    }
    ca_rel_sc   = map_ca.get(scenario, rel.ca_recuperable_realiste)
    payback_str = (f"{comb['payback_mois']:.1f} mois"
                   if comb.get("payback_mois") and comb["payback_mois"] > 0 else "N/A")

    # ─────────────────────────────────────────────────────────────────────────
    # HELPERS
    # ─────────────────────────────────────────────────────────────────────────

    def make_header():
        """Logo gauche + titre centre, identique v3."""
        logo_w = 4.2 * cm
        if os.path.exists(_lp):
            logo_el = RLImage(_lp, width=logo_w, height=2.4 * cm, kind="proportional")
        else:
            logo_el = Paragraph(
                "<b><font color='#2A93B5'>l'agent</font>digital</b>",
                ps("LF", fontSize=11, fontName="Helvetica-Bold",
                   textColor=C_NAVY, alignment=TA_LEFT))

        parts = [p for p in [nom_soc, nom_dir, date_str] if p]
        client_line = " \u00b7 ".join(parts)

        title_w = PW - logo_w - 0.4 * cm
        title_col = Table([
            [Paragraph("Simulateur <font color='#2A93B5'>ROI Signature+</font>", title_s)],
            [Paragraph("Diagnostic commercial \u00b7 Relance devis \u00b7 Acquisition client", sub_s)],
            [Paragraph(client_line, client_s)],
        ], colWidths=[title_w])
        title_col.setStyle(TableStyle([
            ("INNERGRID",     (0,0),(-1,-1), 0, C_WHITE),
            ("BOX",           (0,0),(-1,-1), 0, C_WHITE),
            ("TOPPADDING",    (0,0),(-1,-1), 1),
            ("BOTTOMPADDING", (0,0),(-1,-1), 1),
            ("LEFTPADDING",   (0,0),(-1,-1), 0),
            ("RIGHTPADDING",  (0,0),(-1,-1), 0),
        ]))
        hdr = Table([[logo_el, title_col]],
                    colWidths=[logo_w + 0.4 * cm, title_w])
        hdr.setStyle(TableStyle([
            ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
            ("INNERGRID",     (0,0),(-1,-1), 0, C_WHITE),
            ("BOX",           (0,0),(-1,-1), 0, C_WHITE),
            ("LEFTPADDING",   (0,0),(-1,-1), 0),
            ("RIGHTPADDING",  (0,0),(-1,-1), 0),
            ("TOPPADDING",    (0,0),(-1,-1), 0),
            ("BOTTOMPADDING", (0,0),(-1,-1), 0),
        ]))
        return hdr

    def make_footer():
        return [
            Spacer(1, 8),
            HRFlowable(width="100%", thickness=0.5, color=C_BDR, spaceAfter=4),
            Paragraph(
                "l'agentdigital \u00b7 Simulateur ROI Signature+ v5 \u00b7 "
                f"{date_str} \u00b7 "
                "Projections theoriques. Ne constituent pas une garantie de performance.",
                foot_s),
        ]

    def make_kpi_hero(kpis, h=3.4 * cm):
        """
        Bloc KPI hero N colonnes.
        Fond blanc casse + bordure bleue fine + accent strip top par colonne.
        kpis = [(label, value_str, sub_str), ...]
        """
        w = PW
        d = Drawing(w, h)
        # Fond blanc casse + bordure bleue fine
        d.add(Rect(0, 0, w, h,
                   fillColor=C_BLUE5,
                   strokeColor=C_BLUE,
                   strokeWidth=1.2, rx=4, ry=4))
        n   = len(kpis)
        cw  = w / n
        pad = 16
        for i, (lbl, val, sub) in enumerate(kpis):
            x0 = cw * i
            # Accent strip bleu en haut de chaque colonne
            d.add(Rect(x0 + pad, h - 5, cw - pad * 2, 3,
                       fillColor=C_BLUE, strokeColor=None))
            # Separateur vertical doux
            if i > 0:
                d.add(Line(x0, h * 0.08, x0, h * 0.92,
                           strokeColor=C_BLUE4, strokeWidth=0.8))
            # Label petit, bleu desature, majuscules
            d.add(String(x0 + pad, h - 18, lbl,
                         fontName="Helvetica-Bold", fontSize=6.5,
                         fillColor=C_BLUE2))
            # Valeur grande, bleu principal
            vlen  = len(val)
            vsize = 22 if vlen <= 12 else (17 if vlen <= 17 else 13)
            d.add(String(x0 + pad, h - 46, val,
                         fontName="Helvetica-Bold", fontSize=vsize,
                         fillColor=C_BLUE))
            # Sous-texte gris
            max_ch = int((cw - pad * 2) / 5.2)
            sub_d  = sub if len(sub) <= max_ch else sub[:max_ch - 2] + ".."
            d.add(String(x0 + pad, 9, sub_d,
                         fontName="Helvetica", fontSize=6.5,
                         fillColor=colors.HexColor(GRAY_TEXT)))
        return d

    def make_bar_chart(labels, values, bar_colors, w, h):
        """Barres verticales style v3 - fond blanc, valeurs au-dessus, labels en bas."""
        d = Drawing(w, h)
        mx   = max(v for v in values if v > 0) or 1
        bot  = 0.75 * cm
        topp = 0.65 * cm
        ch   = h - bot - topp
        n    = len(values)
        slot = w / n
        bw   = slot * 0.52
        for i, (lbl, val, col) in enumerate(zip(labels, values, bar_colors)):
            cx = slot * i + slot / 2
            bh = max(3, (val / mx) * ch)
            d.add(Rect(cx - bw / 2, bot, bw, bh,
                       fillColor=colors.HexColor(col), strokeColor=None, rx=2, ry=2))
            d.add(String(cx, bot + bh + 4, _fe_plain(val) + " EUR",
                         fontName="Helvetica-Bold", fontSize=7,
                         fillColor=colors.HexColor(NAVY), textAnchor="middle"))
            d.add(String(cx, 3, lbl,
                         fontName="Helvetica", fontSize=6,
                         fillColor=colors.HexColor(GRAY_TEXT), textAnchor="middle"))
        return d

    def make_pie_chart(slices_data, w, h):
        """
        Camembert style v3 avec legende a droite.
        slices_data = [(val, color_hex, label, val_str), ...]
        """
        d = Drawing(w, h)
        total = sum(v for v, *_ in slices_data) or 1
        cx    = w * 0.40
        cy    = h * 0.50
        r     = min(w * 0.38, h * 0.44)
        start = 90.0
        for val, col, lbl, val_str in slices_data:
            angle = (val / total) * 360.0
            end   = start - angle
            d.add(Wedge(cx, cy, r, end, start,
                        fillColor=colors.HexColor(col),
                        strokeColor=C_WHITE, strokeWidth=1.5))
            mid_rad = math.radians((start + end) / 2)
            px = cx + r * 0.60 * math.cos(mid_rad)
            py = cy + r * 0.60 * math.sin(mid_rad)
            pct = f"{val / total * 100:.0f}%"
            d.add(String(px, py - 4, pct,
                         fontName="Helvetica-Bold", fontSize=8,
                         fillColor=C_WHITE, textAnchor="middle"))
            start = end
        # Legende a droite
        leg_x = cx + r + 12
        leg_y = cy + (len(slices_data) - 1) * 13
        for i, (val, col, lbl, val_str) in enumerate(slices_data):
            ly = leg_y - i * 26
            d.add(Rect(leg_x, ly, 9, 9,
                       fillColor=colors.HexColor(col), strokeColor=None))
            d.add(String(leg_x + 13, ly + 1, lbl,
                         fontName="Helvetica", fontSize=6.5,
                         fillColor=colors.HexColor(GRAY_TEXT)))
            d.add(String(leg_x + 13, ly - 9, val_str,
                         fontName="Helvetica-Bold", fontSize=7,
                         fillColor=colors.HexColor(NAVY)))
        return d

    def make_funnel(labels, values, w, h):
        """Entonnoir - palette bleue uniquement."""
        d = Drawing(w, h)
        mx     = values[0] if values[0] > 0 else 1
        n      = len(labels)
        top_r  = 10
        bot_r  = 4
        area_h = h - top_r - bot_r
        slot   = area_h / n
        bar_h  = slot * 0.66
        max_bw = w * 0.55
        for i, (lbl, val) in enumerate(zip(labels, values)):
            col   = COL_FUN[i] if i < len(COL_FUN) else COL_BAR2
            top_y = h - top_r - i * slot
            bot_y = top_y - bar_h
            bw    = max(max_bw * 0.07, (val / mx) * max_bw)
            d.add(Rect(4, bot_y, bw, bar_h,
                       fillColor=colors.HexColor(col), strokeColor=None, rx=2, ry=2))
            pct_s = "100%" if i == 0 else f"{val / mx * 100:.0f}%"
            vd    = f"{int(round(val))}" if val >= 10 else f"{val:.1f}"
            d.add(String(4 + bw + 5, bot_y + bar_h * 0.28,
                         f"{lbl}: {vd}",
                         fontName="Helvetica-Bold", fontSize=6.5,
                         fillColor=colors.HexColor(NAVY)))
            d.add(String(w - 4, bot_y + bar_h * 0.28, pct_s,
                         fontName="Helvetica", fontSize=6,
                         fillColor=colors.HexColor(GRAY_TEXT), textAnchor="end"))
            if i < n - 1:
                mx_bx = 4 + max_bw * 0.28
                d.add(Line(mx_bx, bot_y, mx_bx, bot_y - (slot - bar_h) + 2,
                           strokeColor=C_BDR, strokeWidth=1))
        return d

    def chart_col_wrap(title_str, drawing, col_w):
        """Encapsule titre + graphique dans une colonne propre (identique v3)."""
        t = Table(
            [[Paragraph(title_str, sec_s)], [drawing]],
            colWidths=[col_w])
        t.setStyle(TableStyle([
            ("INNERGRID",     (0,0),(-1,-1), 0, C_WHITE),
            ("BOX",           (0,0),(-1,-1), 0, C_WHITE),
            ("TOPPADDING",    (0,0),(-1,-1), 0),
            ("BOTTOMPADDING", (0,0),(-1,-1), 0),
            ("LEFTPADDING",   (0,0),(-1,-1), 0),
            ("RIGHTPADDING",  (0,0),(-1,-1), 0),
            ("VALIGN",        (0,0),(-1,-1), "TOP"),
        ]))
        return t

    def make_data_table(data, lw, vw, highlight_last=False):
        """Tableau style v3 : fond alternance, en-tete fond BG_LIGHT, derniere ligne surlignable."""
        tbl_base = [
            ("FONTSIZE",      (0,0),(-1,-1), 7.5),
            ("BACKGROUND",    (0,0),(-1,0),  C_BG),
            ("TEXTCOLOR",     (0,0),(-1,0),  C_NAVY),
            ("FONTNAME",      (0,0),(-1,0),  "Helvetica-Bold"),
            ("FONTNAME",      (0,1),(-1,-1), "Helvetica"),
            ("ROWBACKGROUNDS",(0,1),(-1,-1), [C_WHITE, C_BG]),
            ("GRID",          (0,0),(-1,-1), 0.4, C_BDR),
            ("LEFTPADDING",   (0,0),(-1,-1), 6),
            ("RIGHTPADDING",  (0,0),(-1,-1), 6),
            ("TOPPADDING",    (0,0),(-1,-1), 3),
            ("BOTTOMPADDING", (0,0),(-1,-1), 3),
        ]
        if highlight_last:
            tbl_base += [
                ("FONTNAME",   (0,-1),(-1,-1), "Helvetica-Bold"),
                ("BACKGROUND", (0,-1),(-1,-1), C_BLUE),
                ("TEXTCOLOR",  (0,-1),(-1,-1), C_WHITE),
            ]
        t = Table(data, colWidths=[lw, vw])
        t.setStyle(TableStyle(tbl_base))
        return t

    def side_by_side(t1, t2, w1, w2):
        """Deux tableaux cote a cote sans bordure (identique v3)."""
        s = Table([[t1, t2]], colWidths=[w1, w2])
        s.setStyle(TableStyle([
            ("VALIGN",        (0,0),(-1,-1), "TOP"),
            ("LEFTPADDING",   (0,0),(-1,-1), 0),
            ("RIGHTPADDING",  (0,0),(-1,-1), 4),
            ("TOPPADDING",    (0,0),(-1,-1), 0),
            ("BOTTOMPADDING", (0,0),(-1,-1), 0),
            ("INNERGRID",     (0,0),(-1,-1), 0, C_WHITE),
            ("BOX",           (0,0),(-1,-1), 0, C_WHITE),
        ]))
        return s

    # ═════════════════════════════════════════════════════════════════════════
    # STORY
    # ═════════════════════════════════════════════════════════════════════════
    story = []

    # ─────────────────────────────────────────────────────────────────────────
    # PAGE 1 : Header · KPI Hero · Graphiques Relance · Tableaux Relance
    # ─────────────────────────────────────────────────────────────────────────
    story.append(make_header())
    story.append(HRFlowable(width="100%", thickness=2, color=C_BLUE,
                            spaceAfter=16, spaceBefore=8))

    # ── KPI Hero 3 blocs (1ere colonne "CA PERDU ANNUEL" supprimee) ──────────
    story.append(make_kpi_hero([
        (f"CA RECUPERABLE ({scenario[:8].upper()})",
         _fe_plain(ca_rel_sc * 12) + " EUR",
         f"{_fe_plain(ca_rel_sc)} EUR / mois"),
        ("CA ADDITIONNEL ACQUISITION",
         _fe_plain(acq.ca_additionnel * 12) + " EUR",
         f"ROAS: {acq.roas:.1f}x  |  {acq.ventes:.1f} ventes/mois"),
        ("GAIN NET ANNUEL ESTIME",
         _fe_plain(comb['gain_net_mensuel'] * 12) + " EUR",
         f"ROI: {comb['roi_global']:.1f}x  |  Payback: {payback_str}"),
    ]))
    story.append(Spacer(1, 20))

    # ── Graphiques Relance ────────────────────────────────────────────────────
    story.append(Paragraph(
        "MODULE 1  \u2013  RELANCE DEVIS  |  Situation actuelle & CA recuperable",
        sec_s))

    CHART_W = PW / 2 - 0.2 * cm
    CHART_H = 5.0 * cm

    bar_rel = make_bar_chart(
        ["Prudent", "Realiste", "Ambitieux"],
        [rel.ca_recuperable_prudent, rel.ca_recuperable_realiste, rel.ca_recuperable_ambitieux],
        [COL_BAR1, COL_BAR2, COL_BAR3],   # palette bleue uniquement
        CHART_W, CHART_H,
    )
    devis_relances = max(0, sit.devis_envoyes - rel.devis_sous_exploites)
    pie_rel = make_pie_chart([
        (rel.devis_sous_exploites, COL_PIE1, "Non relances", f"{rel.devis_sous_exploites:.0f} devis"),
        (devis_relances,           COL_PIE2, "Relances",     f"{devis_relances:.0f} devis"),
    ], CHART_W, CHART_H)

    charts_row1 = Table(
        [[chart_col_wrap("CA RECUPERABLE SELON SCENARIO (EUR)", bar_rel, CHART_W + 0.2*cm),
          chart_col_wrap("REPARTITION DES DEVIS", pie_rel, CHART_W + 0.2*cm)]],
        colWidths=[CHART_W + 0.2*cm, CHART_W + 0.2*cm])
    charts_row1.setStyle(TableStyle([
        ("INNERGRID",     (0,0),(-1,-1), 0, C_WHITE),
        ("BOX",           (0,0),(-1,-1), 0, C_WHITE),
        ("TOPPADDING",    (0,0),(-1,-1), 0),
        ("BOTTOMPADDING", (0,0),(-1,-1), 0),
        ("LEFTPADDING",   (0,0),(-1,-1), 0),
        ("RIGHTPADDING",  (0,0),(-1,-1), 4),
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
    ]))
    story.append(charts_row1)
    story.append(Spacer(1, 20))

    # ── Tableaux Relance ──────────────────────────────────────────────────────
    story.append(Paragraph("PARAMETRES  \u2013  RESULTATS RELANCE", sec_s))

    LW = 4.8 * cm
    VW = 3.4 * cm
    TW = LW + VW + 0.1 * cm

    sit_data = [
        ["Situation actuelle",  "Valeur"],
        ["Devis envoyes / mois",  str(sit.devis_envoyes)],
        ["Taux non relances",     _pct_str(sit.taux_devis_non_relances)],
        ["Devis sous-exploites",  f"{rel.devis_sous_exploites:.0f}"],
        ["Taux transfo actuel",   _pct_str(sit.taux_transfo_actuel)],
        ["CA mensuel actuel",     _fe_plain(sit.ca_mensuel) + " EUR"],
        ["Panier moyen",          _fe_plain(profil.panier_moyen) + " EUR"],
        ["Marge brute estimee",   _pct_str(profil.marge_brute_pct)],
    ]
    rel_data = [
        ["Resultats relance",     "Valeur"],
        ["CA perdu / mois",       _fe_plain(rel.ca_perdu_mensuel) + " EUR"],
        ["Recuperable Prudent",   _fe_plain(rel.ca_recuperable_prudent) + " EUR"],
        ["Recuperable Realiste",  _fe_plain(rel.ca_recuperable_realiste) + " EUR"],
        ["Recuperable Ambitieux", _fe_plain(rel.ca_recuperable_ambitieux) + " EUR"],
        ["Gain annuel scenario",  _fe_plain(ca_rel_sc * 12) + " EUR"],
        ["Forfait relance",       "249 EUR / mois"],
    ]

    story.append(side_by_side(
        make_data_table(sit_data, LW, VW),
        make_data_table(rel_data, LW, VW, highlight_last=True),
        TW, TW,
    ))
    story.extend(make_footer())

    # ─────────────────────────────────────────────────────────────────────────
    # PAGE 2 : Module Acquisition + Vision combinee + Conclusion
    # ─────────────────────────────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(make_header())
    story.append(HRFlowable(width="100%", thickness=2, color=C_BLUE,
                            spaceAfter=16, spaceBefore=8))

    # ── Graphiques Acquisition ────────────────────────────────────────────────
    story.append(Paragraph(
        "MODULE 2  \u2013  ACQUISITION CLIENT  |  Entonnoir & indicateurs",
        sec_s))

    FUNNEL_W = PW * 0.44
    PIE_W    = PW - FUNNEL_W - 0.4 * cm
    CHART_H2 = 5.2 * cm

    funnel = make_funnel(
        ["Clics", "Leads", "Qualifies", "Devis", "Ventes"],
        [acq.clics, acq.leads, acq.leads_qualifies, acq.devis, acq.ventes],
        FUNNEL_W, CHART_H2,
    )
    cout_annuel = comb['cout_total_mensuel'] * 12
    gain_annuel = comb['gain_net_mensuel'] * 12
    pie_acq = make_pie_chart([
        (cout_annuel,         COL_PIE1, "Cout annuel",   _fe_plain(cout_annuel) + " EUR"),
        (max(0, gain_annuel), COL_PIE2, "Gain net ann.", _fe_plain(max(0, gain_annuel)) + " EUR"),
    ], PIE_W, CHART_H2)

    charts_row2 = Table(
        [[chart_col_wrap("ENTONNOIR ACQUISITION CLIENT", funnel, FUNNEL_W + 0.2*cm),
          chart_col_wrap("COUT ANNUEL VS GAIN NET ANNUEL", pie_acq, PIE_W + 0.2*cm)]],
        colWidths=[FUNNEL_W + 0.2*cm, PIE_W + 0.2*cm])
    charts_row2.setStyle(TableStyle([
        ("INNERGRID",     (0,0),(-1,-1), 0, C_WHITE),
        ("BOX",           (0,0),(-1,-1), 0, C_WHITE),
        ("TOPPADDING",    (0,0),(-1,-1), 0),
        ("BOTTOMPADDING", (0,0),(-1,-1), 0),
        ("LEFTPADDING",   (0,0),(-1,-1), 0),
        ("RIGHTPADDING",  (0,0),(-1,-1), 4),
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
    ]))
    story.append(charts_row2)
    story.append(Spacer(1, 20))

    # ── Tableaux Acquisition + Vision combinee ────────────────────────────────
    story.append(Paragraph("ACQUISITION CLIENT  \u2013  VISION COMBINEE", sec_s))

    LW2 = 4.8 * cm
    VW2 = 3.4 * cm
    TW2 = LW2 + VW2 + 0.1 * cm

    acq_data = [
        ["Acquisition client",   "Valeur"],
        ["Budget pub / mois",    _fe_plain(budget_pub) + " EUR"],
        ["Clics generes",        f"{acq.clics:.0f}"],
        ["Leads generes",        f"{acq.leads:.1f}"],
        ["Leads qualifies",      f"{acq.leads_qualifies:.1f}"],
        ["Devis emis",           f"{acq.devis:.1f}"],
        ["Ventes / mois",        f"{acq.ventes:.1f}"],
        ["CA additionnel",       _fe_plain(acq.ca_additionnel) + " EUR"],
        ["Marge brute",          _fe_plain(acq.marge_brute) + " EUR"],
        ["Cout / lead",          _fe_plain(acq.cout_par_lead) + " EUR"],
        ["ROAS",                 f"{acq.roas:.1f}x"],
        ["Forfait acquisition",  "549 EUR / mois"],
    ]
    comb_data = [
        ["Vision combinee",      "Valeur"],
        ["CA relance / mois",    _fe_plain(comb['ca_relance_mensuel']) + " EUR"],
        ["CA acq. / mois",       _fe_plain(comb['ca_acquisition_mensuel']) + " EUR"],
        ["CA total / mois",      _fe_plain(comb['ca_total_mensuel']) + " EUR"],
        ["CA total annuel",      _fe_plain(comb['ca_total_annuel']) + " EUR"],
        ["Marge totale / mois",  _fe_plain(comb['marge_totale_mensuel']) + " EUR"],
        ["Cout mensuel total",   _fe_plain(comb['cout_total_mensuel']) + " EUR"],
        ["Gain net / mois",      _fe_plain(comb['gain_net_mensuel']) + " EUR"],
        ["Payback setup",        payback_str],
        ["ROI global",           f"{comb['roi_global']:.1f}x"],
        ["Forfait retenu",       forfait_nom],
        ["Setup",                "3 700 EUR" if "compl" in forfait_nom.lower() else "2 000 EUR"],
    ]

    story.append(side_by_side(
        make_data_table(acq_data,  LW2, VW2),
        make_data_table(comb_data, LW2, VW2, highlight_last=True),
        TW2, TW2,
    ))
    story.append(Spacer(1, 16))

    # ── Conclusion encadree ───────────────────────────────────────────────────
    story.append(Paragraph(
        "CONCLUSION  \u2013  SYNTHESE & RECOMMANDATION COMMERCIALE", sec_s))

    nom_affiche = profil.societe or "l'entreprise"
    concl_body  = (
        f"D'apres les donnees renseignees, {nom_affiche} perd environ "
        f"<b>{_fe_plain(rel.ca_perdu_mensuel)} EUR</b> de CA par mois faute de relance structuree "
        f"({_fe_plain(rel.ca_perdu_annuel)} EUR / an). "
        f"Un systeme de relance automatique permettrait de recuperer jusqu'a "
        f"<b>{_fe_plain(ca_rel_sc)} EUR / mois</b> (scenario {scenario}), "
        f"soit <b>{_fe_plain(ca_rel_sc * 12)} EUR</b> sur 12 mois.<br/><br/>"
        f"En parallele, un systeme d'acquisition avec {_fe_plain(budget_pub)} EUR de budget publicitaire "
        f"genererait <b>{acq.ventes:.1f} ventes supplementaires</b> et "
        f"<b>{_fe_plain(acq.ca_additionnel)} EUR de CA additionnel</b> par mois.<br/><br/>"
        f"Le gain net mensuel estime est de <b>{_fe_plain(comb['gain_net_mensuel'])} EUR</b> "
        f"pour un cout total de {_fe_plain(comb['cout_total_mensuel'])} EUR / mois "
        f"(abonnement {forfait_nom} + budget pub). "
        f"Retour sur l'investissement initial (setup) : <b>{payback_str}</b>. "
        f"ROI global estime : <b>{comb['roi_global']:.1f}x</b>."
    )
    concl_para = Paragraph(concl_body, concl_s)
    concl_tbl  = Table([[concl_para]], colWidths=[PW])
    concl_tbl.setStyle(TableStyle([
        ("BOX",           (0,0),(-1,-1), 1.2, C_BLUE),
        ("BACKGROUND",    (0,0),(-1,-1), colors.HexColor("#E8F6FB")),
        ("TOPPADDING",    (0,0),(-1,-1), 10),
        ("BOTTOMPADDING", (0,0),(-1,-1), 10),
        ("LEFTPADDING",   (0,0),(-1,-1), 12),
        ("RIGHTPADDING",  (0,0),(-1,-1), 12),
    ]))
    story.append(concl_tbl)
    story.extend(make_footer())

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
