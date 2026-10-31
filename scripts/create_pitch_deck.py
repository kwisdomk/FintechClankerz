from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

OUT = "FINTECH_AI_Updated_5_Slides.pptx"
DEMO_HOST = "first-reseller-flows-statutes.trycloudflare.com"
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
card(s,6.8,2.05,5.75,4.45,PANEL2);text(s,7.1,2.35,5,.3,"BEYOND BANKS: 10 BUSINESS CATEGORIES",13,TEAL,True)
bullets(s,7.1,2.9,5.05,["Retail + e-commerce: supplier / fulfilment payments","Restaurants / hotels + logistics: operating expenses","Schools + hospitals: procurement invoices","NGOs + construction: project / contractor costs","Manufacturers + audit firms: vendor / client review"],14,.56)
text(s,7.13,5.81,4.9,.5,"Users: auditors, finance-control teams and business owners.",12,MUTED)
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
text(s,1.02,5.68,11.2,.5,"7 backend / SDK tests passed • SDK wheel built • frontend TypeScript check passed • cloud + local inference verified. Separate pipeline sample: 100 accepted, 6 duplicate rows, 34 anomalies; full API hookup pending.",13,WHITE)

# 4: live demonstration
s=slide("LIVE DEMO / 90 SECONDS","CSV → duplicate evidence → Gemma explanation → review",f"Public app: {DEMO_HOST}/dashboard")
for shape in s.shapes:
    if shape.has_text_frame and shape.text.startswith("Public app:"):
        shape.text_frame.paragraphs[0].runs[0].hyperlink.address = f"https://{DEMO_HOST}/dashboard"
card(s,.75,2.05,6.1,4.5,PANEL);text(s,1.05,2.35,5.4,.3,"SHOW THE END-TO-END FLOW",12,TEAL,True)
bullets(s,1.05,2.9,5.4,["Upload 01_mixed_office_transactions.csv (20 valid rows).", "Open Anomalies & AI; inspect a duplicate candidate.", "Explain: Google-hosted Gemma interprets the supplied evidence.", "Save review; refresh to show persisted status.", "Local model: POST /ollama/api/generate; Swagger: /backend/docs"],14,.64)
card(s,7.15,2.05,5.4,4.5,PANEL2);text(s,7.48,2.35,4.8,.3,"THREE SYNTHETIC DEMO FILES",12,GOLD,True)
bullets(s,7.48,2.9,4.75,["01 Office: 20 valid rows; varied costs + duplicate candidates.","02 Retail: 20 valid rows; inventory, logistics + duplicates.","03 Projects: 16 valid + 4 invalid rows; demonstrate rejection reporting.","Large payment ≠ fraud. Same-value invoices may be legitimate; auditor checks."],14,.77)
text(s,1.05,6.7,11.2,.25,"CSV downloads: /demo-data/ on the same host. Public smoke test passed upload → finding → saved review; local and cloud generation both succeeded.",10,MUTED)

# 5: impact, repository evidence and honest next steps
s=slide("MIT OPEN SOURCE / INTEGRATION / NEXT STEPS","Built to review payments. Open for others to integrate.","Impact target: reduce spreadsheet hunting and improve review traceability; time savings and accuracy are not yet measured.")
card(s,.75,2.0,5.75,4.6,PANEL);text(s,1.05,2.3,5,.3,"DELIVERED: REUSABLE APPLICATION CODE",12,TEAL,True)
bullets(s,1.05,2.82,5.05,["MIT LICENSE • github.com/kwisdomk/FintechClankerz • main + mbr-3.","API v0.4.0: typed OpenAPI 3.1 contract, Swagger / ReDoc and stable operation IDs.","Python SDK: pip install ./sdk/python; JavaScript + curl integration examples.","docs/INTEGRATION.md • docs/openapi.json • CONTRIBUTING.md • tests + synthetic data."],14,.82)
card(s,6.8,2.0,5.75,4.6,PANEL2);text(s,7.1,2.3,5,.3,"HONEST LIMITATIONS / WHAT COMES NEXT",12,GOLD,True)
bullets(s,7.1,2.82,5.05,["Current screening: duplicate rules. Wire full Isolation Forest pipeline into upload next.","Pre-1.0 MVP: add authentication, rate limits, tenant isolation and robust currency/date handling.","DigitalOcean GPU + private Ollama: researched, NOT deployed. Benchmark a 20GB GPU before committing.","Synthetic public demo only. Cloud sends evidence to Google; model / provider terms are separate from MIT."],13,.82)
text(s,.82,6.75,11.8,.23,"Cloud hosting today: Google AI Studio. Local inference today: developer machine + tunnel. DO research: digitalocean.com/products/gpu-droplets. Stop public access after the demo.",9,MUTED)

prs.core_properties.title="FINTECH AI — Digital Surfers: Financial Audit Investigation MVP"
prs.core_properties.subject="Five-minute, five-slide MVP: ten business use cases, workflow, local/cloud Gemma, live demo, MIT license and integration SDK"
prs.core_properties.author="FINTECH AI / Digital Surfers"
# Exactly five slides, with a five-minute presenter script.
notes = [
    "0:00–0:45 | Good day. We are Digital Surfers and this is FINTECH AI. Finance teams need to find transactions worth checking and record what happens next. This is not just for banks. Ten potential customer categories are retailers, e-commerce businesses, restaurants and hotels, logistics firms, schools, hospitals, NGOs, construction companies, manufacturers, and accounting or audit firms. Examples include supplier invoices, procurement and contractor payments. These are potential use cases, not ten deployed customers. Our initial users are auditors and finance-control teams. We assist investigations, not determine fraud.",
    "0:45–1:40 | The workflow is import, screen, explain and review. A CSV upload saves accepted transactions and reports rejected rows. Deterministic checks flag repeated references or matching supplier, amount and date. These are possible duplicates, not proof. Gemma interprets the supplied context; the backend preserves server-owned evidence. The auditor confirms, dismisses or selects needs_review. The API stores decision, reviewer, notes and timestamp. Inference failure does not block CSV processing or human review. Re-uploading a file appends data, so do not retry blindly.",
    "1:40–2:40 | Next.js and React proxy requests to FastAPI, Pydantic, HTTPX and SQLite. The application Explain action is configured for Google AI Studio model gemma-4-26b-a4b-it. A separate local Ollama model, gemma4:latest, is 7.5B Q4_K_M with about 6.6 GB of weights. Both inference paths were verified publicly. Local-only, cloud-only and local-then-cloud provider selection are supported. Cloud use sends transaction context and evidence to Google; credentials stay in ignored server-side .env. Seven backend/SDK tests passed, the SDK wheel built and the frontend TypeScript check passed. A separate Pandas/Isolation Forest sample reported 100 accepted rows, 6 possible duplicate rows and 34 anomaly rows; these are sample counts, not a performance benchmark. The full pipeline is not yet invoked by upload.",
    f"2:40–4:10 | Open https://{DEMO_HOST}/dashboard. Upload demo-data/01_mixed_office_transactions.csv: 20 valid synthetic office expenses. Open Anomalies & AI and select an office-furniture or maintenance candidate. Show evidence, request Explain, then save a human review and refresh. If the UI lacks a control, use Swagger at https://{DEMO_HOST}/backend/docs with an actual finding ID. File 02_mixed_retail_transactions.csv has 20 valid retail rows. File 03_mixed_projects_with_validation.csv has 16 valid and 4 deliberately invalid rows. Files are downloadable under /demo-data/ on the same host. Direct local generation is POST /ollama/api/generate with model gemma4:latest, prompt, stream=false and think=false; it is distinct from persisted audit explanations. Prior short local/cloud requests took roughly 18/35 seconds, not an SLA. If AI is slow, show evidence and saved review instead. Temporary tunnel, unauthenticated synthetic demo only; do not claim this hostname is permanent.",
    "4:10–5:00 | Our deliverable is traceable review, not an unmeasured promise of fraud accuracy or time savings. The code now has an MIT license. Others can clone github.com/kwisdomk/FintechClankerz and install the SDK with pip install ./sdk/python. API version 0.4.0 provides typed OpenAPI 3.1 responses and operation IDs, live Swagger and ReDoc, and an exported docs/openapi.json. docs/INTEGRATION.md has Python, JavaScript and curl examples plus error and CORS guidance; CONTRIBUTING.md supports contributions. Model licenses and hosted-provider terms remain separate. Next: full pipeline hookup, authentication, rate limits, tenant isolation and currency/date hardening. DigitalOcean GPU hosting is researched, not deployed; a 20 GB GPU is a candidate to benchmark. Evaluate triage time and review completeness with users. Close: evidence first, AI assistance second, human judgment always."
]
assert len(prs.slides) == 5
for s, note in zip(prs.slides, notes):
    s.notes_slide.notes_text_frame.text = note
prs.save(OUT)
for alias in ["FINTECH_AI_Demo_Final_5_Slides.pptx", "FINTECH_AI_MVP_Pitch.pptx"]:
    try:
        prs.save(alias)
    except PermissionError:
        print(f"{alias} is open; updated deck saved as {OUT}.")
print(OUT)
