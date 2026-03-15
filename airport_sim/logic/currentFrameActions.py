from dataclasses import dataclass, field


# Class to store which frame actions have taken place last tick
# Stores a list in the form [[plane, "action"]]
@dataclass
class CurrentFrameActions:
    current_frame_actions: list[list[str]] = field(default_factory=list)

currentFrameActions = CurrentFrameActions()