from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from nodes_edges import (query_rewriter, story_ideas_generator, stories_human_feedback_handler,
                         character_outline_supervisor, character_generator, scene_outline_generator,
                         draft_writer, macro_editor, micro_editor, revision_orchestrator,
                         ideas_conditional_edge, character_outline_conditional_edge,
                         revision_orchestrator_conditional_edge)

from states import CreativeWritingAgentState

from IPython.display import display, Image

graph_builder = StateGraph(CreativeWritingAgentState)

graph_builder.add_node("query_rewriter", query_rewriter)
graph_builder.add_node("story_ideas_generator", story_ideas_generator)
graph_builder.add_node("stories_human_feedback_handler", stories_human_feedback_handler)
graph_builder.add_node("character_outline_supervisor", character_outline_supervisor)
graph_builder.add_node("character_generator", character_generator)
graph_builder.add_node("scene_outline_generator", scene_outline_generator)
graph_builder.add_node("draft_writer", draft_writer)
graph_builder.add_node("macro_editor", macro_editor)
graph_builder.add_node("micro_editor", micro_editor)
graph_builder.add_node("revision_orchestrator", revision_orchestrator)

graph_builder.add_edge(START, "query_rewriter")
graph_builder.add_edge("query_rewriter", "story_ideas_generator")
graph_builder.add_edge("story_ideas_generator", "stories_human_feedback_handler")
graph_builder.add_conditional_edges(
    "stories_human_feedback_handler",
    ideas_conditional_edge,
    {
        "character_outline_supervisor": "character_outline_supervisor",
        "story_ideas_generator": "story_ideas_generator"
    }
)

graph_builder.add_edge("character_generator", "character_outline_supervisor")
graph_builder.add_edge("scene_outline_generator", "character_outline_supervisor")
graph_builder.add_conditional_edges(
    "character_outline_supervisor",
    character_outline_conditional_edge,
    {
        "character_generator": "character_generator",
        "scene_outline_generator": "scene_outline_generator",
        "draft_writer": "draft_writer",
    }
)

graph_builder.add_edge("draft_writer", "macro_editor")
graph_builder.add_edge("draft_writer", "micro_editor")
graph_builder.add_edge("macro_editor", "revision_orchestrator")
graph_builder.add_edge("micro_editor", "revision_orchestrator")
graph_builder.add_conditional_edges(
    "revision_orchestrator",
    revision_orchestrator_conditional_edge,
    {
        "draft_writer": "draft_writer",
        END: END
    }
)

memory = MemorySaver()
graph= graph_builder.compile(interrupt_before=["stories_human_feedback_handler"], checkpointer=memory)
display(Image(graph.get_graph().draw_mermaid_png()))