#!/usr/bin/env python3
"""
Database Seeding Script
Populates initial sample conversations, grounded messages, and rendered artifacts.
"""
import asyncio
import os
import sys
import uuid
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from app.db.database import init_db, AsyncSessionLocal
from app.db.models import Session, Message, Artifact
from app.retrieval.ingestion import ingestion_service
from app.core.logging import logger

SAMPLE_INTERACTIVE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>B2B Growth Loop Simulator (Elena Verna Framework)</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #0f172a;
            color: #f8fafc;
            padding: 24px;
            margin: 0;
        }
        .card {
            background-color: #1e293b;
            border-radius: 12px;
            padding: 24px;
            border: 1px solid #334155;
            max-width: 600px;
            margin: 0 auto;
        }
        h2 { color: #f59e0b; margin-top: 0; }
        .control-group { margin-bottom: 20px; }
        label { display: block; font-size: 14px; color: #94a3b8; margin-bottom: 8px; }
        input[type="range"] {
            width: 100%;
            accent-color: #f59e0b;
        }
        .metric-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            margin-top: 24px;
        }
        .metric-box {
            background-color: #0f172a;
            padding: 16px;
            border-radius: 8px;
            border: 1px solid #334155;
            text-align: center;
        }
        .metric-val { font-size: 24px; font-weight: bold; color: #38bdf8; }
        .metric-label { font-size: 12px; color: #64748b; margin-top: 4px; }
    </style>
</head>
<body>
    <div class="card">
        <h2>🔄 B2B Compounding Growth Loop Simulator</h2>
        <p style="font-size: 14px; color: #cbd5e1;">Simulate compounding user acquisition based on Elena Verna's loop model (Invite Rate &times; Conversion Rate).</p>
        
        <div class="control-group">
            <label>Initial User Cohort: <span id="cohort-val" style="color: #f59e0b; font-weight: bold;">500</span></label>
            <input type="range" id="cohort" min="100" max="5000" step="100" value="500" oninput="calculateLoop()">
        </div>

        <div class="control-group">
            <label>Collaborator Invites per Active User (K-Factor): <span id="invite-val" style="color: #f59e0b; font-weight: bold;">2.4</span></label>
            <input type="range" id="invites" min="0.5" max="5.0" step="0.1" value="2.4" oninput="calculateLoop()">
        </div>

        <div class="control-group">
            <label>Invite-to-Signup Conversion Rate: <span id="conv-val" style="color: #f59e0b; font-weight: bold;">25%</span></label>
            <input type="range" id="conv" min="5" max="60" step="1" value="25" oninput="calculateLoop()">
        </div>

        <div class="metric-grid">
            <div class="metric-box">
                <div class="metric-val" id="viral-coeff">0.60</div>
                <div class="metric-label">Viral Coefficient (K)</div>
            </div>
            <div class="metric-box">
                <div class="metric-val" id="compounded-users">1,250</div>
                <div class="metric-label">Compounded Total Users (3 Cycles)</div>
            </div>
        </div>
    </div>

    <script>
        function calculateLoop() {
            const cohort = parseInt(document.getElementById('cohort').value);
            const invites = parseFloat(document.getElementById('invites').value);
            const conv = parseFloat(document.getElementById('conv').value) / 100.0;

            document.getElementById('cohort-val').innerText = cohort.toLocaleString();
            document.getElementById('invite-val').innerText = invites.toFixed(1);
            document.getElementById('conv-val').innerText = Math.round(conv * 100) + '%';

            const kFactor = invites * conv;
            document.getElementById('viral-coeff').innerText = kFactor.toFixed(2);
            document.getElementById('viral-coeff').style.color = kFactor >= 1.0 ? '#10b981' : '#38bdf8';

            let total = cohort;
            let currentGen = cohort;
            for(let i=0; i<3; i++) {
                currentGen = currentGen * kFactor;
                total += currentGen;
            }

            document.getElementById('compounded-users').innerText = Math.round(total).toLocaleString();
        }
        calculateLoop();
    </script>
</body>
</html>"""

SAMPLE_SHIP30_ESSAY = """# The Superhuman Product-Market Fit Engine: How to Systematically Increase PMF

Most early-stage startups fail not because their engineers couldn't ship code, but because they scaled acquisition before achieving true product-market fit. [S1]

Here is the sobering reality:

If fewer than 40% of your active users would be *"Very Disappointed"* if your product vanished tomorrow, spending money on paid growth is pouring water into a leaky bucket. [S1]

---

## 1. The Danger of Premature Scaling

When founders launch a product, they often treat Product-Market Fit as a binary, mystical moment. [S2]

They check Google Analytics, celebrate 1,000 initial signups, and immediately hire sales reps. But four weeks later, cohort retention curves plummet toward zero. 

Linear funnels lose energy at every transition. To achieve durable enterprise value, you must build **compounding growth loops** where the natural usage of one user pulls in the next cohort. [S3]

---

## 2. The 4-Step Optimization Protocol

Rahul Vohra (Founder & CEO of Superhuman) transformed their PMF score from a mediocre 22% to an industry-leading 58% using a repeatable 4-step framework [S4]:

- **Step 1: Survey your active cohort.** Ask: *"How would you feel if you could no longer use this product tomorrow?"*
- **Step 2: Isolate your High-Expectation Customers (HXC).** Filter exclusively for users who answered *'Very Disappointed'*. Study their exact persona, job title, and daily workflows.
- **Step 3: Analyze the 'Somewhat Disappointed' group.** Filter for those whose desired value aligns with your HXC persona. Uncover the 1 or 2 specific blockers preventing them from falling in love.
- **Step 4: Divide your roadmap 50/50.** Dedicate 50% of sprint capacity to doubling down on what HXC users love, and 50% to solving the objections of the 'Somewhat Disappointed' tier.

---

## 3. High-Agency Prioritization

Product leaders can't execute everything at once. Using Shreyas Doshi's **LNO Framework** [S5]:

1. **L Tasks (Leverage)**: Core PMF engines, positioning strategy, and high-impact PRDs require 10x excellence (60% effort).
2. **N Tasks (Neutral)**: Routine sprint updates require 80% good-enough quality.
3. **O Tasks (Overhead)**: Low-leverage status emails must be aggressively minimized.

---

### The Bottom Line

Don't guess whether you have PMF. Measure it quarterly, protect your high-expectation customers, and design an 11-star experience [S6] that creates natural word-of-mouth velocity."""

async def seed_data():
    logger.info("Initializing database...")
    await init_db()
    
    async with AsyncSessionLocal() as db:
        # Ingest transcripts first
        await ingestion_service.ingest_all_transcripts(db)

        # Create Demo Session 1: PMF Engine & Essay
        session_id_1 = "demo-session-pmf-engine"
        s1 = Session(
            id=session_id_1,
            title="Superhuman PMF Engine & Ship 30 Essay",
            created_at=datetime.utcnow() - timedelta(hours=2),
            updated_at=datetime.utcnow() - timedelta(hours=1)
        )
        db.add(s1)

        m1_user = Message(
            id=str(uuid.uuid4()),
            session_id=session_id_1,
            role="user",
            content="How did Rahul Vohra systematically optimize Superhuman's PMF score from 22% to 58%?",
            created_at=datetime.utcnow() - timedelta(minutes=90)
        )
        db.add(m1_user)

        m1_asst = Message(
            id=str(uuid.uuid4()),
            session_id=session_id_1,
            role="assistant",
            content="### The 4-Step Superhuman PMF Engine\n\nRahul Vohra shared the exact method Superhuman used on Lenny's Podcast [S1]:\n\n1. **Filter for High-Expectation Customers (HXC)** [S1]: Exclusively study users who answered 'Very Disappointed' on the Sean Ellis PMF survey.\n2. **Convert Borderline Promoters** [S1]: Look at users who answered 'Somewhat Disappointed' and address their specific product blockers.\n3. **50/50 Roadmap Allocation** [S1]: Spend half of engineering bandwidth deepening existing love, and half eliminating blockers.\n4. **Track the Trend**: Re-survey every quarter until the score passes 40%.",
            citations=[{
                "citation_id": "S1",
                "source_id": "rahul_vohra_superhuman",
                "episode_id": "EP-106",
                "speaker": "Rahul Vohra (Founder & CEO, Superhuman)",
                "title": "The Superhuman PMF Engine",
                "url": "https://www.lennyspodcast.com/rahul-vohra-superhuman/",
                "relevance_score": 0.96,
                "passage_quote": "We spent two years systematically building a machine to optimize that score from 22% to 58%..."
            }],
            created_at=datetime.utcnow() - timedelta(minutes=88)
        )
        db.add(m1_asst)

        # Artifact for Session 1
        art1 = Artifact(
            id="art-ship30-pmf-engine",
            session_id=session_id_1,
            message_id=m1_asst.id,
            title="Ship 30 Essay: The Superhuman PMF Engine",
            artifact_type="markdown",
            content=SAMPLE_SHIP30_ESSAY,
            sanitized_content=SAMPLE_SHIP30_ESSAY,
            created_at=datetime.utcnow() - timedelta(minutes=85),
            artifact_metadata={"skill": "ship30", "word_count": 480}
        )
        db.add(art1)

        # Demo Session 2: Growth Loops & Simulator
        session_id_2 = "demo-session-growth-loops"
        s2 = Session(
            id=session_id_2,
            title="Elena Verna Growth Loops & Simulator",
            created_at=datetime.utcnow() - timedelta(hours=1),
            updated_at=datetime.utcnow() - timedelta(minutes=30)
        )
        db.add(s2)

        m2_user = Message(
            id=str(uuid.uuid4()),
            session_id=session_id_2,
            role="user",
            content="Generate an interactive B2B Growth Loop simulator based on Elena Verna's framework.",
            created_at=datetime.utcnow() - timedelta(minutes=25)
        )
        db.add(m2_user)

        m2_asst = Message(
            id=str(uuid.uuid4()),
            session_id=session_id_2,
            role="assistant",
            content="I've generated an interactive **B2B Compounding Growth Loop Simulator** based on Elena Verna's collaboration and invite-loop mechanics [S1]. You can test different cohort sizes, K-factors, and conversion rates directly in the side Artifact Viewer.",
            citations=[{
                "citation_id": "S1",
                "source_id": "elena_verna_growth",
                "episode_id": "EP-102",
                "speaker": "Elena Verna (Growth Advisor)",
                "title": "The Ultimate Guide to PLG & Growth Loops",
                "url": "https://www.lennyspodcast.com/elena-verna-growth/",
                "relevance_score": 0.94,
                "passage_quote": "A Growth Loop is a closed system where the output of one cohort of users becomes the input for the next cohort..."
            }],
            created_at=datetime.utcnow() - timedelta(minutes=24)
        )
        db.add(m2_asst)

        art2 = Artifact(
            id="art-growth-loop-simulator",
            session_id=session_id_2,
            message_id=m2_asst.id,
            title="B2B Growth Loop Simulator",
            artifact_type="html",
            content=SAMPLE_INTERACTIVE_HTML,
            sanitized_content=SAMPLE_INTERACTIVE_HTML,
            created_at=datetime.utcnow() - timedelta(minutes=23),
            artifact_metadata={"skill": "artifact_builder", "type": "interactive_simulator"}
        )
        db.add(art2)

        await db.commit()
        print("\n" + "="*50)
        print(" DATABASE SEEDING COMPLETED SUCCESSFULLY")
        print(" Sample sessions and artifacts created.")
        print("="*50 + "\n")

if __name__ == "__main__":
    asyncio.run(seed_data())
