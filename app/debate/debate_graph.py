from langgraph.graph import StateGraph, START, END

from app.debate.debate_state import DebateState
from app.debate.debate_nodes import DebateNodes
from app.debate.stopping_rules import route_after_verification


class DebateEngine:

    def __init__(self, max_rounds: int = 3):

        self.max_rounds = max_rounds
        self.nodes = DebateNodes()

        graph = StateGraph(DebateState)

        graph.add_node(
            "initial_audit",
            self.nodes.initial_audit,
        )

        graph.add_node(
            "verify",
            self.nodes.verify,
        )

        graph.add_node(
            "rebuttal",
            self.nodes.rebuttal,
        )

        graph.add_node(
            "record_round",
            self.nodes.record_round,
        )

        graph.add_node(
            "finish",
            self.nodes.finish,
        )

        graph.add_edge(
            START,
            "initial_audit",
        )

        graph.add_edge(
            "initial_audit",
            "verify",
        )

        graph.add_edge(
            "verify",
            "record_round",
        )

        graph.add_conditional_edges(
            "record_round",
            route_after_verification,
            {
                "finish": "finish",
                "rebuttal": "rebuttal",
            },
        )

        graph.add_edge(
            "rebuttal",
            "verify",
        )

        graph.add_edge(
            "finish",
            END,
        )

        self.graph = graph.compile()

    def run(self, query: str) -> dict:

        initial_state: DebateState = {
            "query": query,
            "finding": None,
            "evidence": [],
            "verification": None,
            "history": [],
            "round_number": 1,
            "max_rounds": self.max_rounds,
            "final_status": "UNKNOWN",
            "finished": False,
        }

        return self.graph.invoke(initial_state)