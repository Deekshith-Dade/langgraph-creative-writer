from typing import (
    TypedDict,
    Annotated
)
from langgraph.graph.message import add_messages
from models import StoryIdea, CharactersList, SceneOutlineList, MacroEditorFeedbackList, MicroEditorFeedbackList

class CreativeWritingAgentState(TypedDict):
    messages: Annotated[list, add_messages]
    query: str
    description: str
    max_story_ideas: int
    final_story_idea: StoryIdea
    scenes: SceneOutlineList
    characters: CharactersList
    max_orchestrator_iterations: int
    
    
class QueryRewriterState(TypedDict):
    messages: Annotated[list, add_messages]
    query: str
    description: str
    
class StoryIdeaGeneratorState(TypedDict):
    messages: Annotated[list, add_messages]
    description: str
    story_ideas: list[StoryIdea]
    final_story_idea: StoryIdea
    human_feedback: str
    max_story_ideas: int
    
class StoryIdeaFeedbackState(TypedDict):
    messages: Annotated[list, add_messages]
    story_ideas: list[StoryIdea]
    human_feedback: str
    final_story_idea: StoryIdea
    
class CharacterOutlineGeneratorState(TypedDict):
    messages: Annotated[list, add_messages]
    final_story_idea: StoryIdea
    characters: CharactersList
    scenes: SceneOutlineList
    critic_character_feedback: tuple[str, str]
    critic_scene_feedback: tuple[str, str]
    critic_overall_rating: str
    human_feedback: str
    character_iterations: int
    scene_iterations: int
    
class DraftWriterState(TypedDict):
    messages: Annotated[list, add_messages]
    final_story_idea: StoryIdea
    characters: CharactersList
    scenes: SceneOutlineList
    draft: str
    
    macro_editor_feedback: MacroEditorFeedbackList
    micro_editor_feedback: MicroEditorFeedbackList
    
    curr_orchestrator_iteration: int
    max_orchestrator_iterations: int
    orchestrator_decision: bool
    
class MacroEditorState(TypedDict):
    messages: Annotated[list, add_messages]
    final_story_idea: StoryIdea
    characters: CharactersList
    scenes: SceneOutlineList
    draft: str
    
    macro_editor_feedback: MacroEditorFeedbackList

class MicroEditorState(TypedDict):
    messages: Annotated[list, add_messages]
    final_story_idea: StoryIdea
    characters: CharactersList
    scenes: SceneOutlineList
    draft: str
    
    micro_editor_feedback: MicroEditorFeedbackList
    