"""
JARVIS Commander Adapter
Maintains backward compatibility while routing requests to the new IntentRouter.
"""
from engine.intent_router import intent_router

class Commander:
    def __init__(self):
        pass

    def process(self, text: str) -> str:
        """
        Processes text request and returns spoken response string.
        """
        result = intent_router.route_and_execute(text)
        return result.get("spoken", "")

    def process_structured(self, text: str):
        """
        Returns rich structured response dictionary for the upgraded HUD.
        """
        return intent_router.route_and_execute(text)

# Global singleton
commander = Commander()
