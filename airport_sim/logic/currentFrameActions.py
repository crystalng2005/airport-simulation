from dataclasses import dataclass, field



@dataclass
class CurrentFrameActions:
    """
    Class to store which frame actions have taken place last tick
    Stores a list in the form [[plane, "action"]] 
    """
    current_frame_actions: list[list[str]] = field(default_factory=list)

currentFrameActions = CurrentFrameActions()