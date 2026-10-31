from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

OUT = "FINTECH_AI_Demo_Final_5_Slides.pptx"
prs = Presentation(); prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
NAVY=RGBColor(10,20,37); PANEL=RGBColor(20,35,56); PANEL2=RGBColor(25,45,67); TEAL=RGBColor(58,220,190); WHITE=RGBColor(240,246,250); MUTED=RGBColor(164,183,201); GOLD=RGBColor(255,193,94)

def bg(s):
    s.background.fill.solid(); s.background.fill.fore_color.rgb=NAVY
    sh=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,0,0, Inches(.12), Inches(7.5)); sh.fill.solid(); sh.fill.fore_color.rgb=TEAL; sh.line.fill.background()
def text(s,x,y,w,h,value,size=16,color=WHITE,bold=False,align=None):
    sh=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h)); tf=sh.text_frame; tf.clear(); tf.word_wrap=True
    tf.margin_left=Inches(.02);tf.margin_right=Inches(.02);tf.margin_top=Inches(.02);tf.margin_bottom=Inches(.02)
    p=tf.paragraphs[0];p.text=value;p.font.name="Aptos";p.font.size=Pt(size);p.font.bold=bold;p.font.color.rgb=color
    if align is not None:p.alignment=align
    return sh
def card(s,x,y,w,h,fill=PANEL):
    sh=s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h));sh.fill.solid();sh.fill.fore_color.rgb=fill;sh.line.color.rgb=fill;return sh
def bullets(s,x,y,w,items,size=14,step=.48):
    for i,item in enumerate(items):
        text(s,x,y+i*step,.22,.3,"•",size+2,TEAL,True);text(s,x+.27,y+i*step,w-.27,step+.02,item,size,WHITE)
def slide(kicker,heading,sub=None):
    s=prs.slides.add_slide(prs.slide_layouts[6]);bg(s);text(s,.65,.32,12,.25,kicker.upper(),10,TEAL,True);text(s,.65,.68,12,.65,heading,28,WHITE,True)
    if sub:text(s,.67,1.35,12,.4,sub,13,MUTED)
    n=len(prs.slides);text(s,.68,7.15,10,.2,"FINTECH AI  /  DIGITAL SURFERS",9,MUTED);text(s,12.1,7.12,.5,.2,f"{n}/5",9,TEAL,True,align=PP_ALIGN.RIGHT)
    return s

# 1: problem + users
s=slide("FINANCIAL AUDIT MVP","Find the signal. Keep the auditor in control.","FINTECH AI — Digital Surfers | Evidence-led investigation of unusual financial transactions")
card(s,.75,2.05,5.75,4.45,PANEL);text(s,1.05,2.35,5,.3,"THE PROBLEM",13,GOLD,True)
bullets(s,1.05,2.95,5.05,["High-volume transaction spreadsheets make unusual items hard to spot.","A raw anomaly flag lacks context and follow-up evidence.","Review decisions and investigation history need a consistent record."],16,.88)
card(s,6.8,2.05,5.75,4.45,PANEL2);text(s,7.1,2.35,5,.3,"INTENDED USERS",13,TEAL,True)
bullets(s,7.1,2.95,5.05,["Internal / external auditors", "Finance control and compliance teams", "Audit leads who need a review trail"],16,.88)
text(s,1.05,5.95,10.9,.4,"AI assists investigation; it does not decide fraud or replace professional judgment.",14,TEAL,True)

# 2: proposed solution
s=slide("PROPOSED SOLUTION","Import → screen → explain → review","Deterministic data checks work without AI. Gemma is an optional evidence-grounded explanation layer.")
steps=[("01  IMPORT","Validate CSV rows and persist transactions."),("02  SCREEN","Flag repeated references and supplier + amount + date matches."),("03  EXPLAIN","Gemma interprets server-supplied evidence; no database/tool access."),("04  REVIEW","Auditor confirms or dismisses; decision and timestamp are stored.")]
for i,(h,d) in enumerate(steps):
    x=.78+i*3.15;card(s,x,2.25,2.85,2.05,PANEL if i%2==0 else PANEL2);text(s,x+.2,2.52,2.5,.35,h,14,TEAL,True);text(s,x+.2,3.08,2.45,.95,d,14,WHITE)
    if i<3:text(s,x+2.86,3.05,.28,.35,"›",20,TEAL,True,align=PP_ALIGN.CENTER)
card(s,.78,4.75,11.8,1.55,RGBColor(23,53,62));text(s,1.05,5.0,11,.3,"EVIDENCE BOUNDARY",12,TEAL,True)
text(s,1.05,5.38,11,.65,"Observed evidence is persisted transaction / rule output. Gemma contributes interpretation and recommended checks—not new transaction facts or financial actions.",15,WHITE)

# 3: implementation + architecture
s=slide("IMPLEMENTATION / BOTH INFERENCE PATHS VERIFIED","One audit API. Cloud Gemma + local Gemma.","Next.js / React → FastAPI / Pydantic → SQLite. AI adds interpretation; deterministic screening remains independent.")
cols=[(.75,"FRONTEND",["Dashboard + CSV upload","Transactions + findings","Same-origin API proxy"]),(3.9,"API + DATABASE",["FastAPI / HTTPX / SQLite","Transactions + findings","Explanations + reviews"]),(7.05,"CLOUD: LIVE",["Google AI Studio","gemma-4-26b-a4b-it","App Explain uses cloud"]),(10.2,"LOCAL: LIVE",["Ollama: gemma4:latest","7.5B Q4_K_M / 6.6GB","Remote /ollama API access"])]
for x,h,lines in cols:
    card(s,x,2.15,2.35,2.6,PANEL);text(s,x+.17,2.42,2,.3,h,12,TEAL,True);bullets(s,x+.17,2.92,2.02,lines,12,.53)
for x in [3.25,6.4,9.55]:text(s,x,3.15,.4,.35,"→",19,TEAL,True,align=PP_ALIGN.CENTER)
card(s,.75,5.08,11.8,1.3,PANEL2);text(s,1.02,5.28,11,.3,"REPRODUCIBLE EVIDENCE",12,GOLD,True)
text(s,1.02,5.68,11.2,.5,"3 backend tests passed • public cloud explain + local generation succeeded • separate Pandas / Isolation Forest sample: 100 accepted, 6 duplicate rows, 34 anomaly rows (not yet wired into upload).",13,WHITE)

# 4: live demonstration
s=slide("LIVE DEMO / 90 SECONDS","CSV → duplicate evidence → Gemma explanation → review","Public app: ranks-atlanta-formerly-diverse.trycloudflare.com/dashboard")
card(s,.75,2.05,6.1,4.5,PANEL);text(s,1.05,2.35,5.4,.3,"SHOW THE END-TO-END FLOW",12,TEAL,True)
bullets(s,1.05,2.9,5.4,["Upload 01_mixed_office_transactions.csv (20 valid rows).", "Open Anomalies & AI; inspect a duplicate candidate.", "Explain: Google-hosted Gemma interprets the supplied evidence.", "Save review; refresh to show persisted status.", "Local model: POST /ollama/api/generate; Swagger: /backend/docs"],14,.64)
card(s,7.15,2.05,5.4,4.5,PANEL2);text(s,7.48,2.35,4.8,.3,"THREE SYNTHETIC DEMO FILES",12,GOLD,True)
bullets(s,7.48,2.9,4.75,["01 Office: 20 valid rows; varied costs + duplicate candidates.","02 Retail: 20 valid rows; inventory, logistics + duplicates.","03 Projects: 16 valid + 4 invalid rows; demonstrate rejection reporting.","Large payment ≠ fraud. Same-value invoices may be legitimate; auditor checks."],14,.77)
text(s,1.05,6.7,11.2,.25,"CSV downloads: /demo-data/ on the same host. Public smoke test passed upload → finding → saved review; local and cloud generation both succeeded.",10,MUTED)

# 5: impact, repository evidence and honest next steps
s=slide("IMPACT / PUBLIC SOURCE / NEXT STEPS","Faster triage is the goal. Traceable review is the deliverable.","Value: bring records, candidate findings, AI interpretation and recorded human decisions into one workflow.")
card(s,.75,2.0,5.75,4.6,PANEL);text(s,1.05,2.3,5,.3,"DELIVERED & REPRODUCIBLE",12,TEAL,True)
bullets(s,1.05,2.82,5.05,["github.com/kwisdomk/FintechClankerz — public source; main + mbr-3 synced for demo.","Frontend, FastAPI, SQLite, analysis pipeline, tests, reports + synthetic CSVs.","Cloud + local Gemma responses verified; upload and review persist without AI.","Measure next: triage time and review completeness versus spreadsheets; no savings claim yet."],14,.82)
card(s,6.8,2.0,5.75,4.6,PANEL2);text(s,7.1,2.3,5,.3,"LIMITATIONS & NEXT DEPLOYMENT",12,GOLD,True)
bullets(s,7.1,2.82,5.05,["Wire the full Isolation Forest pipeline into the upload API; current live screening is duplicate rules.","Add team-approved OSS license, access controls, rate limits and provider data policy.","DigitalOcean GPU + private Ollama: researched, NOT deployed. RTX 4000 Ada 20GB is a candidate to benchmark.","Demo is temporarily unauthenticated; synthetic records only. Cloud Explain sends evidence to Google."],13,.82)
text(s,.82,6.75,11.8,.23,"Cloud hosting today: Google AI Studio. Local inference today: developer machine + tunnel. DO research: digitalocean.com/products/gpu-droplets. Stop public access after the demo.",9,MUTED)

prs.core_properties.title="FINTECH AI — Digital Surfers: Financial Audit Investigation MVP"
prs.core_properties.subject="Five-minute, five-slide MVP: problem, workflow, cloud/local Gemma, live demo, impact and public-source evidence"
prs.core_properties.author="FINTECH AI / Digital Surfers"
# Exactly five slides, with a five-minute presenter script.
notes = [
    "0:00–0:45 | Problem and users. We built FINTECH AI for auditors and finance-control teams. Spreadsheets contain many ordinary expenses and a few items worth checking, but a flag alone is not an investigation. Our goal is to put the original record, the screening evidence and the human decision together. We do not claim to detect fraud or replace an auditor. Transition: here is the workflow we implemented.",
    "0:45–1:40 | Workflow. Import a CSV; accepted rows go into SQLite and rejected rows are reported. Screening is deterministic: repeated payment reference, or matching supplier, amount and date. These are possible duplicates, not proven duplicates. Gemma explains supplied evidence only; the server replaces any model-authored observed evidence with authoritative rule evidence before saving. The auditor chooses confirmed, dismissed or needs_review and the API persists the decision, reviewer, notes and time. AI failure does not stop importing or reviewing.",
    "1:40–2:40 | Technical implementation. Next.js and React call same-origin proxy routes into FastAPI, Pydantic, HTTPX and SQLite. The app is currently configured for Google AI Studio model gemma-4-26b-a4b-it; it is Gemma, not a Gemini substitution. Local Ollama also runs gemma4:latest, a 7.5B Q4 model with roughly 6.6 GB of weights, reachable through the tunnel's /ollama endpoint. Both paths returned successful public requests. Provider selection supports local, cloud and local_then_cloud. Keys stay server-side in ignored .env, not the repo. Three backend tests passed. Separate analysis reports show 100 accepted rows, 6 duplicate rows and 34 anomalies; these are sample outputs, not an accuracy benchmark, and that broader pipeline is not yet called by upload.",
    "2:40–4:10 | Live demo. Open https://ranks-atlanta-formerly-diverse.trycloudflare.com/dashboard and show the current summary. Upload 01_mixed_office_transactions.csv from demo-data. Go to Anomalies & AI; choose a new office-furniture or maintenance candidate. Show source evidence first, then click Explain to call Google-hosted Gemma. Allow around 35 seconds based on one earlier request, not an SLA. Save a review and refresh. If time permits, upload file 03: expect 16 accepted and 4 rejected for invalid amount, zero, negative and missing date. File 02 is an alternate retail example. Local-model request: POST /ollama/api/generate with JSON {\"model\":\"gemma4:latest\",\"prompt\":\"Explain duplicate payments briefly.\",\"stream\":false,\"think\":false}. A previous short local response took about 18 seconds; latency varies. Do not upload the same file repeatedly unless deliberately demonstrating repeated imports. If inference fails, show evidence and the review flow rather than claiming the AI succeeded. The tunnel is temporary and scheduled to stop an hour after launch.",
    "4:10–5:00 | Impact, source and next steps. The working deliverable is traceable review, not a measured productivity or fraud-accuracy claim. The public GitHub repo includes the UI, API, broader data pipeline, reports and demo data. An explicit team-approved license is still missing, so be precise: public source today; licensed open-source release is a remaining action. DigitalOcean is a researched self-hosted option, not deployed infrastructure. We would benchmark a 20 GB GPU, run Ollama privately and persist weights for occasional windows; Google-hosted cloud inference already works today. Next: full pipeline adapter, license, access controls and rate limits, then evaluate triage time and review completeness. Close: AI assists; evidence and the auditor decide."
]
assert len(prs.slides) == 5
for s, note in zip(prs.slides, notes):
    s.notes_slide.notes_text_frame.text = note
prs.save(OUT)
try:
    prs.save("FINTECH_AI_MVP_Pitch.pptx")
except PermissionError:
    print("Original deck is open; updated final deck saved separately.")
print(OUT)
