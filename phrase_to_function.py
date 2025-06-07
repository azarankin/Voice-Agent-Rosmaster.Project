
from adapt.engine import IntentDeterminationEngine
from adapt.intent import IntentBuilder
from typing import Callable, Dict
from thefuzz import process
from config import FUZZY_THRESHOLD

class PhraseToFunction:
    def __init__(self, commands: Dict[str, Callable], fuzzy_threshold: int = FUZZY_THRESHOLD):
        self.engine = IntentDeterminationEngine()
        self.commands_map = {}  # intent_name → (original_phrase, callback)
        self.commands_text = list(commands.keys())  # For fuzzy fallback
        self.commands_func = commands
        self.fuzzy_threshold = fuzzy_threshold
        self._register_commands(commands)

    def _register_commands(self, commands: Dict[str, Callable]):
        all_words = {word.lower() for cmd in commands for word in cmd.split()}
        for word in all_words:
            self.engine.register_entity(word, word)

        for idx, (cmd, callback) in enumerate(commands.items()):
            intent_name = f"Intent_{idx}"
            builder = IntentBuilder(intent_name)
            for word in cmd.split():
                builder.require(word.lower())
            self.engine.register_intent_parser(builder.build())
            self.commands_map[intent_name] = (cmd, callback)

    def execute(self, phrase: str) -> tuple[bool, any]:
        intents = list(self.engine.determine_intent(phrase))
        if intents:
            best_intent = intents[0]
            intent_name = best_intent.get("intent_type")
            confidence = best_intent.get("confidence", 0)

            if confidence > 0 and intent_name in self.commands_map:
                cmd_text, func = self.commands_map[intent_name]
                print(f"[Adapt] ✅ Matched intent: '{cmd_text}' (conf={confidence:.2f})")
                result = func()
                return True, result

        # No Adapt match → fallback to fuzzy
        print(f"[Adapt] ❌ No confident match for: '{phrase}' → trying fuzzy matching...")
        match, score = process.extractOne(phrase, self.commands_text)
        if score >= self.fuzzy_threshold:
            print(f"[Fuzzy] ✅ Matched '{match}' (score={score})")
            result = self.commands_func[match]()
            return True, result
        else:
            print(f"[Fuzzy] ❌ No match found (score={score})")
            return False, None



# -------------------------------------------------------
# Example usage
if __name__ == "__main__":
    sample_commands = {
        "register user": lambda: print("📥 User Registered!"),
        "turn on light": lambda: print("💡 Light turned on!"),
        "shutdown system": lambda: print("🛑 System shutting down!"),
    }

    recognizer = PhraseToFunction(sample_commands)

    test_phrases = [
        "register user",
        "turn on light",
        "shutdown system",
        "unknown command"
    ]

    for phrase in test_phrases:
        recognizer.execute(phrase)
