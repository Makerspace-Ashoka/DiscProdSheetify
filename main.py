from src.orchestrator import BotOrchestrator
from src.parsers import AiStudioParser, LocalLlmParser

def main():
    """
    This function demonstrates the Liskov Substitution Principle.
    We can 'substitute' different parsers without changing the orchestrator's code.
    """
    # Create instances of our concrete parsers
    ai_studio_parser = AiStudioParser()
    local_llm_parser = LocalLlmParser()

    print("--- RUN 1: Using the AI Studio Parser ---")
    # Inject the AI Studio parser into the orchestrator
    bot = BotOrchestrator(parser=ai_studio_parser)
    bot.process_single_url("http://example.com/product/1")

    print("\n============================================\n")

    print("--- RUN 2: Using the Local LLM Parser ---")
    # Now, we create a new orchestrator and 'substitute' the local parser
    bot_2 = BotOrchestrator(parser=local_llm_parser)
    bot_2.process_single_url("http://example.com/product/2")


if __name__ == "__main__":
    main()