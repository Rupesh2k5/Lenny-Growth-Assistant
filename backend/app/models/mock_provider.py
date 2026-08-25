import asyncio
import time
from typing import List, Dict, Any, AsyncGenerator, Optional
from app.models.provider import BaseLLMProvider, LLMResponse

class MockOfflineProvider(BaseLLMProvider):
    """
    Deterministic, high-quality offline provider for seamless local evaluation
    when Ollama daemon or cloud API keys are not locally active.
    """
    def __init__(self, model_name: str = "mock-offline:lenny"):
        super().__init__(model_name=model_name)

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> LLMResponse:
        start_time = time.time()
        user_query = messages[-1]["content"].lower() if messages else ""

        content = self._craft_grounded_response(user_query)
        latency_ms = round((time.time() - start_time) * 1000, 2)

        return LLMResponse(
            content=content,
            model=self.model_name,
            provider="mock",
            latency_ms=latency_ms,
            usage={"prompt_tokens": 150, "completion_tokens": 300, "total_tokens": 450}
        )

    async def stream_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        user_query = messages[-1]["content"].lower() if messages else ""
        content = self._craft_grounded_response(user_query)
        
        # Simulate realistic token streaming
        words = content.split(" ")
        for i in range(0, len(words), 3):
            chunk = " ".join(words[i:i+3]) + " "
            yield chunk
            await asyncio.sleep(0.02)

    def _craft_grounded_response(self, query: str) -> str:
        # Check for unsupported domain
        if any(w in query for w in ["quantum", "astrophysics", "crypto", "blockchain", "gardening", "plumbing"]):
            return (
                "### I couldn't find sufficient evidence\n\n"
                "I searched the available transcript knowledge base for concepts relating to your question, "
                "but Lenny's podcast corpus does not contain grounded discussions on this specific topic.\n\n"
                "**What you can ask about instead:**\n"
                "- **Product Strategy & Design**: Brian Chesky on 11-star experiences & founder mode\n"
                "- **Growth Loops & PLG**: Elena Verna on B2B product-led growth\n"
                "- **PM Work Prioritization**: Shreyas Doshi on the LNO framework\n"
                "- **Product-Market Fit**: Sean Ellis on the 40% PMF survey and Rahul Vohra's Superhuman engine\n"
                "- **Positioning**: April Dunford on obviously awesome product positioning"
            )

        if "ship 30" in query or "essay" in query:
            return (
                "# The Product-Market Fit Engine: How Great Companies Build What Customers Truly Crave\n\n"
                "Most startups fail not because they couldn't build their product, but because they built something nobody desperately cared about. [S1]\n\n"
                "Here is the brutal truth every founder and product manager must confront:\n\n"
                "If fewer than 40% of your users would be *'very disappointed'* if your product disappeared tomorrow, your business is a leaky bucket. [S1]\n\n"
                "---\n\n"
                "## 1. The Trap of False Traction\n\n"
                "Early traction often fools product teams. You run paid ads, acquire 1,000 signups, and celebrate. But three weeks later, your cohort curves plummet straight to zero. [S2]\n\n"
                "Linear acquisition funnels lose energy at every single stage. To build sustainable scale, you must replace linear funnels with **compounding Growth Loops**, where the output of one user naturally triggers the acquisition of the next. [S3]\n\n"
                "---\n\n"
                "## 2. The 4-Step Engine to Benchmark & Optimize PMF\n\n"
                "Rahul Vohra and Sean Ellis created an actionable, scientific protocol to move beyond gut feel [S1][S4]:\n\n"
                "- **Step 1: Survey your active cohort.** Ask: *'How would you feel if you could no longer use this product tomorrow?'*\n"
                "- **Step 2: Isolate your High-Expectation Customers (HXC).** Filter exclusively for the users who answered 'Very Disappointed'. Discover what makes them tick.\n"
                "- **Step 3: Analyze the 'Somewhat Disappointed' group.** Identify the specific friction points preventing them from becoming die-hard promoters.\n"
                "- **Step 4: Divide your roadmap 50/50.** Allocate half your engineering capacity to doubling down on core love, and the other half to eliminating the blockers of high-potential users.\n\n"
                "---\n\n"
                "## 3. High-Agency Execution\n\n"
                "Great product execution requires categorized energy. Using Shreyas Doshi's **LNO Framework**, high-agency PMs invest 60% of their creative intensity into high-leverage strategy memos [S5], ruthlessly batching administrative overhead.\n\n"
                "---\n\n"
                "### The Final Takeaway\n\n"
                "Stop chasing 20 incremental features. Focus on designing an 11-star core experience [S6] that turns users into evangelists."
            )

        if "loop" in query or "plg" in query or "elena" in query or "freemium" in query:
            return (
                "### Key Insights on Growth Loops & PLG Architecture\n\n"
                "Based on Lenny's conversations with **Elena Verna** and **Casey Winters**, here is the core breakdown [S1][S2]:\n\n"
                "1. **Growth Loops vs. Linear Funnels** [S1]:\n"
                "   - Traditional funnels lose energy at every transition and require continuous ad spend.\n"
                "   - A growth loop is a closed system where user activity produces shareable assets or invitations that automatically draw in the next cohort of users.\n\n"
                "2. **Freemium vs. Free Trial Decision** [S1]:\n"
                "   - **Freemium**: Best when the top of funnel is wide, marginal costs are low, and collaboration drives value.\n"
                "   - **Free Trial**: Best for high-touch, complex products requiring evaluation urgency.\n"
                "   - **Reverse Trial**: The modern hybrid—granting 14-day Pro access followed by a graceful downgrade to free.\n\n"
                "3. **Product-Led Sales (PLS)** [S1]:\n"
                "   - Sales teams focus on **Product Qualified Leads (PQLs)** who have already experienced the product's value, resulting in 3x–5x higher conversion."
            )

        if "priorit" in query or "shreyas" in query or "lno" in query or "agency" in query:
            return (
                "### The LNO Framework & High-Agency Product Leadership\n\n"
                "According to **Shreyas Doshi** on Lenny's Podcast [S1]:\n\n"
                "1. **The LNO Framework for PM Work**:\n"
                "   - **L (Leverage Work)**: Strategy memos, PRDs, core positioning. Standard: *10x perfection* (60% effort).\n"
                "   - **N (Neutral Work)**: Sprint planning, routine bug triage. Standard: *Good enough / 80%* (30% effort).\n"
                "   - **O (Overhead Work)**: Status update emails, administrative chores. Standard: *Deliberately fast / batch* (10% effort).\n\n"
                "2. **High-Agency Leadership**:\n"
                "   - High-agency PMs find creative paths through constraints rather than passively reporting blockers.\n\n"
                "3. **Pre-Mortems**:\n"
                "   - Run pre-mortems before launch by imagining the product failed catastrophically 6 months out, surfacing hidden risks early."
            )

        # Default grounded summary
        return (
            "### Core Product & Growth Insights from Lenny's Knowledge Base\n\n"
            "Here are the foundational principles from Lenny's podcast guests [S1][S2]:\n\n"
            "1. **The 11-Star Experience & Focus** [S1]:\n"
            "   - Brian Chesky emphasizes that startups die of *indigestion, not starvation*. Focus on executing the core product at an extraordinary level rather than spreading across 20 mediocre features.\n\n"
            "2. **The 40% PMF Survey Rule** [S2]:\n"
            "   - Sean Ellis explains that if 40%+ of users would be 'Very Disappointed' if your product disappeared, you have product-market fit and can scale acquisition.\n\n"
            "3. **Compounding Growth Loops** [S3]:\n"
            "   - Elena Verna highlights that sustainable scale comes from closed growth loops where user engagement generates new acquisition inputs.\n\n"
            "**Strategic Recommendation:**\n"
            "Focus 50% of your roadmap on deepening what your high-expectation customers love, and 50% on addressing specific objections of borderline promoters."
        )

    async def check_health(self) -> Dict[str, Any]:
        return {
            "status": "ready",
            "provider": "mock",
            "model": self.model_name,
            "message": "Deterministic offline mock provider is online and ready."
        }
