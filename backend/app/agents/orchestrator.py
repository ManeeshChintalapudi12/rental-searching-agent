from uuid import uuid4

from app.agents.intent_agent import IntentAgent
from app.agents.ranking_agent import RankingAgent
from app.agents.response_agent import ResponseAgent
from app.agents.search_agent import SearchAgent
from app.agents.verification_agent import VerificationAgent
from app.config import Settings
from app.models import AgentTrace, ChatRequest, ChatResponse, RentalIntent
from app.services.search_service import SearchService


class RentalAssistantOrchestrator:
    """Bounded multi-agent workflow with server-owned session memory."""

    def __init__(self, settings: Settings, search_service: SearchService) -> None:
        self.intent_agent = IntentAgent(settings)
        self.search_agent = SearchAgent(search_service)
        self.ranking_agent = RankingAgent()
        self.response_agent = ResponseAgent(settings)
        self.verification_agent = VerificationAgent()
        self.sessions: dict[str, RentalIntent] = {}

    async def run(self, request: ChatRequest) -> ChatResponse:
        session_id = request.session_id or str(uuid4())
        trace: list[AgentTrace] = []
        intent = await self.intent_agent.run(request.message, self.sessions.get(session_id))
        self.sessions[session_id] = intent
        trace.append(AgentTrace(agent="intent", status="completed", detail="Extracted validated search requirements"))

        if intent.missing_fields:
            answer = await self.response_agent.run(intent, [], [])
            trace.append(AgentTrace(agent="clarification", status="required", detail=", ".join(intent.missing_fields)))
            return ChatResponse(session_id=session_id, answer=answer, intent=intent, listings=[], recommendations=[], citations=[], grounded=True, needs_clarification=True, agent_trace=trace)

        search_result = await self.search_agent.run(intent)
        trace.append(AgentTrace(agent="search", status="completed", detail=f"Retrieved {search_result.count} provider-backed listings"))
        recommendations = self.ranking_agent.run(search_result.listings)
        trace.append(AgentTrace(agent="ranking", status="completed", detail="Calculated transparent deal scores"))
        draft = await self.response_agent.run(intent, search_result.listings, recommendations)
        trace.append(AgentTrace(agent="response", status="completed", detail="Generated a listing-grounded explanation"))
        answer, grounded, citations = self.verification_agent.run(draft, search_result.listings, recommendations)
        trace.append(AgentTrace(agent="verification", status="passed" if grounded else "failed", detail="Checked prices and listing citations"))
        return ChatResponse(session_id=session_id, answer=answer, intent=intent, listings=search_result.listings, recommendations=recommendations, citations=citations, grounded=grounded, needs_clarification=False, agent_trace=trace)
