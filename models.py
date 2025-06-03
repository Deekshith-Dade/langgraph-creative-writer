from pydantic import BaseModel, Field



class QueryToDescription(BaseModel):
    """
    Used to Convert a simple query into quality description for later processing
    """
    description: str = Field(description = "A Quality Description for creative writing query which is build on later for creative writing")
    reasoning: str = Field(description = "Reasoning to explain the description being produced")
    

class StoryIdea(BaseModel):
    """
    Used to generate a story idea based on the description
    """
    title: str = Field(description = "A title for the story")
    synopsis: str = Field(description = "A synopsis for the story in about 100 words")
    genre: list[str] = Field(description = "a list of at most 4 genres that describe the story")
    tone: str = Field(description = "The tone of the story in a sentence")
    hook: str = Field(description = "A hook for the story in a sentence")

class StoryIdeaList(BaseModel):
    """
    Used to generate a list of story ideas based on the description
    """
    story_ideas: list[StoryIdea] = Field(description = "A list of story ideas")
    reasoning: str = Field(description = "Reasoning to explain the story ideas being produced or feedback incorporated")
    
class StoryIdeaFeedback(BaseModel):
    """
    Used to handle user's feedback on the story ideas
    """
    direction: str = Field(description = "Model's response direction based on the instructions")
    reasoning: str = Field(description = "Reasoning to explain the direction being produced")


class Characters(BaseModel):
    """
    Used to generate a character outline based on the story idea
    """
    character_name: str = Field(description = "The name of the character")
    character_description: str = Field(description = "The description of the character")
    character_backstory: str = Field(description = "The backstory of the character")
    character_goals: str = Field(description = "The goals of the character")
    character_quirks: str = Field(description = "The quirks of the character")
    character_traits: str = Field(description = "The traits of the character")
    character_appearance: str = Field(description = "The appearance of the character")
    character_personality: str = Field(description = "The personality of the character")

class CharactersList(BaseModel):
    """
    Used to generate a list of characters based on the story idea
    """
    characters: list[Characters] = Field(description = "A list of characters")
    reasoning: str = Field(description = "Reasoning to explain the characters being produced")
    
    
class SceneOutline(BaseModel):
    """
    Used to generate a scene outline based on the story idea
    """
    scene_outline: str = Field(description = "The outline of the scene")
    scene_description: str = Field(description = "The description of the scene")
    scene_characters: list[str] = Field(description = "The characters in the scene")
    scene_location: str = Field(description = "The location of the scene")
    scene_time: str = Field(description = "The time of the scene")
    scene_action: str = Field(description = "The action of the scene")
    scene_dialogue: str = Field(description = "The dialogue of the scene")

class SceneOutlineList(BaseModel):
    """
    Used to generate a list of scene outlines based on the story idea
    """
    scene_outlines: list[SceneOutline] = Field(description = "A list of scene outlines")
    reasoning: str = Field(description = "Reasoning to explain the scene outlines being produced")
    
class CharacterOutlineCritic(BaseModel):
    """
    Used to criticize the characters and scene outlines based on the story idea
    """
    character_feedback: str = Field(description = "The feedback on the characters")
    character_rating: str = Field(description = "Rating for the characters on a scale of 1 to 10")
    scene_feedback: str = Field(description = "The feedback on the scene outlines")
    scene_rating: str = Field(description = "Rating for the scene outlines on a scale of 1 to 10")
    overall_rating: str = Field(description = "The overall rating of the characters and scene outlines on a scale of 1 to 10")
    reasoning: str = Field(description = "Reasoning to explain the feedback being produced")
    
class MacroEditorFeedback(BaseModel):
    """
    Used to handle user's feedback on the macro editor
    """
    feedback: str = Field(description = "Feedback from the macro editor expert")

class MacroEditorFeedbackList(BaseModel):
    """
    Used to handle user's feedback on the macro editor
    """
    macro_editor_feedbacks: list[MacroEditorFeedback] = Field(description = "Feedback from the macro editor expert")
    reasoning: str = Field(description = "Reasoning to explain the feedback being produced")

class MicroEditorFeedback(BaseModel):
    """
    Used to handle user's feedback on the micro editor
    """
    feedback: str = Field(description = "Feedback from the micro editor expert")
    
class MicroEditorFeedbackList(BaseModel):
    """
    Used to handle user's feedback on the micro editor
    """
    micro_editor_feedbacks: list[MicroEditorFeedback] = Field(description = "Feedback from the micro editor expert")
    reasoning: str = Field(description = "Reasoning to explain the feedback being produced")

class OrchestratorDecision(BaseModel):
    """
    Used to handle the decision of the orchestrator
    """
    continue_with_draft: bool = Field(description = "Whether to continue with the draft or not. Continue with the rewriting : True, No rewriting needed: False")
    reasoning: str = Field(description = "Reasoning to explain the decision being made")
    
