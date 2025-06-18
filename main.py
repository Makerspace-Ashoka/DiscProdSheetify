from src.orchestrator import BotOrchestrator
from src.fetchers import BasicHtmlFetcher
from src.parsers import AiStudioParser, LocalLlmParser
from src.writers import GoogleSheetWriter

def main():
    """
    This is the assembly point of our application.
    Here, we decide which concrete implementations to use and
    "inject" them into the orchestrator.
    """
    # === Configuration for Run 1: Standard MVP setup ===
    print("ASSEMBLY 1: Using AI Studio Parser")
    # 1. Create the concrete, low-level components.
    fetcher = BasicHtmlFetcher()
    parser = AiStudioParser()
    writer = GoogleSheetWriter()

    # 2. Inject these dependencies into the high-level module.
    bot = BotOrchestrator(fetcher=fetcher, parser=parser, writer=writer)

    # 3. Run the business logic.
    bot.process_single_url("https://www.amazon.com/dp/B08J65S221")

    print("\n=======================================================\n")
    
    # === Configuration for Run 2: Swapping to a Local LLM ===
    print("ASSEMBLY 2: Substituting Local LLM Parser")
    # 1. We only need to create a different parser. Fetcher and Writer stay the same.
    local_parser = LocalLlmParser()

    # 2. Inject the new set of dependencies.
    bot_2 = BotOrchestrator(fetcher=fetcher, parser=local_parser, writer=writer)

    # 3. Run the same business logic. The orchestrator's code did not change.
    bot_2.process_single_url("https://robu.in/product/raspberry-pi-4-model-b-4-gb-ram/")


if __name__ == "__main__":
    main()