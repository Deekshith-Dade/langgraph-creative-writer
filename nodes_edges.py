from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END

from IPython.display import display, Image, Markdown
from dotenv import load_dotenv

import os

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.5,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

load_dotenv()

from states import (CreativeWritingAgentState, StoryIdeaGeneratorState, CharacterOutlineGeneratorState,
                    DraftWriterState, MacroEditorState, MicroEditorState)
from models import (QueryToDescription, StoryIdeaList, StoryIdeaFeedback, CharactersList, SceneOutlineList,
                    CharacterOutlineCritic, MacroEditorFeedbackList, MicroEditorFeedbackList, OrchestratorDecision)

from prompts import (QUERY_PARSER_PROMPT, STORY_IDEAS_GENERATOR_PROMPT, STORY_IDEA_FEEDBACK_PROMPT,
                     CHARACTER_GENERATOR_PROMPT, SCENE_OUTLINE_GENERATOR_PROMPT, CHARACTER_OUTLINE_CRITIC_PROMPT,
                     DRAFT_WRITER_PROMPT, MACRO_EDITOR_PROMPT, MICRO_EDITOR_PROMPT)

def query_rewriter(state: CreativeWritingAgentState) -> CreativeWritingAgentState:
    query = state['query']
    
    system_prompt = QUERY_PARSER_PROMPT.format(query=query)
    llm_structured = llm.with_structured_output(QueryToDescription)
    
    response = llm_structured.invoke([SystemMessage(content=system_prompt), HumanMessage(content="Write a perfect description with reasoning")])
    
    return {"description": response.description, "messages": [AIMessage(content=response.reasoning)]}

def story_ideas_generator(state: StoryIdeaGeneratorState) -> StoryIdeaGeneratorState:
    description = state['description']
    max_story_ideas = state['max_story_ideas']
    story_ideas = state.get('story_ideas', [])
    human_feedback = state.get('human_feedback', '')
    
    previous_story_ideas = "\n".join([f"Story Title: {story.title}\nStory Synopsis: {story.synopsis}\nStory Genre: {story.genre}\nStory Tone: {story.tone}\nStory Hook: {story.hook}" for story in story_ideas])
    
    
    system_prompt = STORY_IDEAS_GENERATOR_PROMPT.format(description=description, 
                                                        max_story_ideas=max_story_ideas,
                                                        previous_story_ideas=previous_story_ideas,
                                                        human_feedback=human_feedback)
    
    structured_llm = llm.with_structured_output(StoryIdeaList)
    
    response = structured_llm.invoke(system_prompt)
    
    for index, story in enumerate(response.story_ideas):
        print(f"Story {index+1}:")
        print(f"Title: {story.title}")
        print(f"Synopsis: {story.synopsis}")
        print(f"Genre: {story.genre}")
        print(f"Tone: {story.tone}")
        print(f"Hook: {story.hook}")
        print("-"*100)
        print("\n")
    
    print(f"Let us know which one you like the most by mentioning the index of the story")
    print(f"Or Give us a feedback for the story or Let the agent pick one for you")
    
    
    return {"story_ideas": response.story_ideas, "messages": [AIMessage(content=response.reasoning)]}

def stories_human_feedback_handler(state: StoryIdeaGeneratorState) -> StoryIdeaGeneratorState:
    feedback = state.get('human_feedback', None)
    story_ideas_str = "\n".join([f"Story {index+1}:\nTitle: {story.title}\nSynopsis: {story.synopsis}\nGenre: {story.genre}\nTone: {story.tone}\nHook: {story.hook}" for index, story in enumerate(state['story_ideas'])])
    
    system_prompt = STORY_IDEA_FEEDBACK_PROMPT.format(story_ideas=story_ideas_str, 
                                                      human_feedback=feedback)
    
    llm_structured = llm.with_structured_output(StoryIdeaFeedback)
    response = llm_structured.invoke(system_prompt)
    
    reasoning = response.reasoning
    direction = response.direction
    
    if direction == "REGENERATE":
        return {"messages": [AIMessage(content=reasoning)], "final_story_idea": None}
    elif direction.startswith("SELECT"):
        if len(direction.split(",")) > 1:
            index = int(direction.split(",")[1]) - 1
            if index > len(state['story_ideas']) or index < 0:
                return {"messages": [AIMessage(content=f"Wrong Response from the model {direction}")], "final_story_idea": None}
            else:
                return {"final_story_idea": state['story_ideas'][index], "messages": [AIMessage(content=reasoning)]}
        else:
            return {"messages": [AIMessage(content=f"Wrong Response from the model {direction}")], "final_story_idea": None}
    else:
        return {"messages": [AIMessage(content=f"Wrong Response from the model {direction}")], "final_story_idea": None}
    

def ideas_conditional_edge(state: StoryIdeaGeneratorState) -> StoryIdeaGeneratorState:
    final_story_idea = state.get('final_story_idea', None)
    if final_story_idea is None:
        return "story_ideas_generator"
    else:
        return "character_outline_supervisor"
    

### Outline Generation and Iteration
def character_outline_supervisor(state: CharacterOutlineGeneratorState) -> CharacterOutlineGeneratorState:
    final_story_idea = state['final_story_idea']
    characters = state.get('characters', None)
    scenes = state.get('scenes', None)
    human_feedback = state.get('human_feedback', None)
    
    system_prompt = CHARACTER_OUTLINE_CRITIC_PROMPT.format(final_story_idea=final_story_idea,
                                                         previous_characters=characters,
                                                         scenes=scenes,
                                                         human_feedback=human_feedback)
    structured_llm = llm.with_structured_output(CharacterOutlineCritic)
    
    response = structured_llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content="Write a perfect character outline with reasoning")])
    
    character_feedback = (response.character_feedback, response.character_rating)
    scene_feedback = (response.scene_feedback, response.scene_rating)
    
    # print(f"Supervisor Character Rating: {character_feedback[1]} {character_feedback[0]}")
    # print(f"Supervisor Scene Rating: {scene_feedback[1]} {scene_feedback[0]}")
    
    return {
        "critic_character_feedback": character_feedback,
        "critic_scene_feedback": scene_feedback,
        "critic_overall_rating": response.overall_rating,
        "messages": [AIMessage(content=response.reasoning)]
    }
    
    
def character_generator(state: CharacterOutlineGeneratorState) -> CharacterOutlineGeneratorState:
    final_story_idea = state['final_story_idea']
    characters = state.get('characters', None)
    scenes = state.get('scenes', None)
    human_feedback = state.get('human_feedback', None)
    expert_feedback = state.get('critic_character_feedback', None)
    character_iterations = state.get('character_iterations', 0)
    
    
        
    
    system_prompt = CHARACTER_GENERATOR_PROMPT.format(final_story_idea=final_story_idea,
                                                      scenes=scenes,
                                                      previous_characters=characters,
                                                      human_feedback=human_feedback,
                                                      expert_feedback=expert_feedback)
    
    structured_llm = llm.with_structured_output(CharactersList)
    response = structured_llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content="Write a perfect character outline with reasoning")])
    
    return {"characters": response.characters, "messages": [AIMessage(content=response.reasoning)], "character_iterations": character_iterations + 1}
    
def scene_outline_generator(state: CharacterOutlineGeneratorState) -> CharacterOutlineGeneratorState:
    final_story_idea = state['final_story_idea']
    characters = state.get('characters', None)
    scenes = state.get('scenes', None)
    human_feedback = state.get('human_feedback', None)
    expert_feedback = state.get('critic_scene_feedback', None)
    scene_iterations = state.get('scene_iterations', 0)
    system_prompt = SCENE_OUTLINE_GENERATOR_PROMPT.format(final_story_idea=final_story_idea,
                                                          previous_characters=characters,
                                                          scenes=scenes,
                                                          human_feedback=human_feedback,
                                                          expert_feedback=expert_feedback)
    
    structured_llm = llm.with_structured_output(SceneOutlineList)
    response = structured_llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content="Write a perfect character outline with reasoning")])
    
    return {"scenes": response.scene_outlines, "messages": [AIMessage(content=response.reasoning)], "scene_iterations": scene_iterations + 1}
    

def character_outline_conditional_edge(state: CharacterOutlineGeneratorState) -> CharacterOutlineGeneratorState:
    characters = state.get('characters', None)
    scenes = state.get('scenes', None)
    
    if characters is None and scenes is None:
        return "scene_outline_generator"
    print(f"Conditinal Edge State: {state}")
    character_feedback = state.get('critic_character_feedback', None)
    scene_feedback = state.get('critic_scene_feedback', None)
    overall_rating = state.get('critic_overall_rating', None)
    # print(f"Character Feedback: {character_feedback}, Scene Feedback: {scene_feedback}, Overall Rating: {overall_rating}")
    if character_feedback is None and scene_feedback is None:
        return "character_generator"
    
    if character_feedback is not None:
        char_feedback, char_rating = character_feedback[0], int(character_feedback[1])
    else:
        char_feedback, char_rating = None, None
    
    if scene_feedback is not None:
        sce_feedback, scene_rating = scene_feedback[0], int(scene_feedback[1])
    else:
        sce_feedback, scene_rating = None, None
    
    character_iterations = state.get('character_iterations', 0)
    scene_iterations = state.get('scene_iterations', 0)
    if int(overall_rating) >= 7:
        return "draft_writer"
    
    print(f"Character Iterations: {character_iterations}, Scene Iterations: {scene_iterations}")
    print(f"Character Rating: {char_rating}, Scene Rating: {scene_rating}")
    if char_rating is not None and character_iterations < 4 and char_rating < 7:
        return "character_generator"
    elif scene_rating is not None and scene_iterations < 4 and scene_rating < 7:
        return "scene_outline_generator"
    else:
        return "draft_writer"


def draft_writer(state: DraftWriterState) -> DraftWriterState:
    final_story_idea = state['final_story_idea']
    characters = state['characters']
    scenes = state['scenes']
    
    initial_draft = state.get('draft', None)
    macro_editor_feedback = state.get('macro_editor_feedback', None)
    micro_editor_feedback = state.get('micro_editor_feedback', None)
    
    system_prompt = DRAFT_WRITER_PROMPT.format(final_story_idea=final_story_idea,
                                              characters=characters,
                                              scenes=scenes,
                                              initial_draft=initial_draft,
                                              macro_editor_feedback=macro_editor_feedback,
                                              micro_editor_feedback=micro_editor_feedback)
    
    response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content="Write a perfect first draft based on the instructions")])
    
    return {"draft": response.content}

def macro_editor(state: MacroEditorState) -> MacroEditorState:
    draft = state['draft']
    final_story_idea = state['final_story_idea']
    characters = state['characters']
    scenes = state['scenes']
    
    system_prompt = MACRO_EDITOR_PROMPT.format(draft=draft,
                                              final_story_idea=final_story_idea,
                                              characters=characters,
                                              scenes=scenes)
    
    structured_llm = llm.with_structured_output(MacroEditorFeedbackList)
    response = structured_llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content="Do your job based on the instructions")])
    
    return {"macro_editor_feedback": response.macro_editor_feedbacks, "messages": [AIMessage(content=response.reasoning)]}
    

def micro_editor(state: MicroEditorState) -> MicroEditorState:
    draft = state['draft']
    final_story_idea = state['final_story_idea']
    characters = state['characters']
    scenes = state['scenes']
    
    system_prompt = MICRO_EDITOR_PROMPT.format(draft=draft,
                                              final_story_idea=final_story_idea,
                                              characters=characters,
                                              scenes=scenes)
    
    structured_llm = llm.with_structured_output(MicroEditorFeedbackList)
    response = structured_llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content="Do your job based on the instructions")])
    
    return {"micro_editor_feedback": response.micro_editor_feedbacks, "messages": [AIMessage(content=response.reasoning)]}
    

def revision_orchestrator(state: DraftWriterState) -> DraftWriterState:
    macro_editor_feedback = state.get('macro_editor_feedback', None)
    micro_editor_feedback = state.get('micro_editor_feedback', None)
    
    max_orchestrator_iterations = state.get('max_orchestrator_iterations', 5)
    curr_orchestrator_iteration = state.get('curr_orchestrator_iteration', 0)
    
    system_prompt = f"""
    You are an expert editor who is given a draft and some feedback on the draft from macro editor and micro editor.
    You need to decide whether to continue with the draft or not. If you think the draft is bad, return True indicating that the writer should work on the draft. If you think the draft doesn't need more work, return False.
    
    Don't take the feedback very critically. If you think the editor's are nitpicking and not suggesting major changes, just return False. Let's go.
    
    Macro Editor Feedback:
    {macro_editor_feedback}
    
    Micro Editor Feedback:
    {micro_editor_feedback}
    """
    
    structured_llm = llm.with_structured_output(OrchestratorDecision)
    response = structured_llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content="Do your job based on the instructions")])
    result = response.continue_with_draft and curr_orchestrator_iteration < max_orchestrator_iterations
    
    return {"orchestrator_decision": result, "curr_orchestrator_iteration": curr_orchestrator_iteration + 1, "messages": [AIMessage(content=response.reasoning)]}
    
def revision_orchestrator_conditional_edge(state: DraftWriterState) -> DraftWriterState:
    continue_with_draft = state.get('orchestrator_decision', True)
    
    if continue_with_draft:
        return "draft_writer"
    else:
        return END
    
