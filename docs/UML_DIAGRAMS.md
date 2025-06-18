### Actors

*   **Team Member:** The human user who posts messages in a Discord channel.
*   **Discord API:** The external service our bot listens to for message events.
*   **Web Server:** The server hosting the product page.
*   **LLM API:** The AI Studio service.
*   **Google Sheets API:** The data destination.

### Use Case Diagram Flow

The flow is now initiated by a Discord event.

[Team Member] --(Posts Message)--> [Discord Bot]
                                          |
                                          | (Notifies our system)
                                          V
+----------------------- OUR SYSTEM BOUNDARY ------------------------+
|                                                                    |
|  (Receive Message & Extract URL) --uses--> [Web Server]            |
|      |                                    (Fetch Page HTML)        |
|      |                                                             |
|      +-----> (Parse HTML for Info) --uses--> [LLM API]              |
|                   |                                                |
|                   |                                                |
|                   +-----> (Append to Google Sheet) --uses--> [Google Sheets API]
|                                                                    |
+--------------------------------------------------------------------+

**Class Diagram**

+------------------+      uses      +--------------------+
| BotOrchestrator  |--------------->| DiscordReader   |
|------------------|                |--------------------|
| + run()          |                | + get_new_messages()|
+------------------+                +--------------------+
        |
        | uses
        V
+------------------+      uses      +--------------------+
| HtmlFetcher      |--------------->| LlmParser          |
|------------------|                |--------------------|
| + fetch(url)     |                | + parse(html)      |
+------------------+                +--------------------+
        |
        | uses
        V
+------------------+
| SheetWriter      |
|------------------|
| + write(data)    |
+------------------+

(Note: This text diagram simplifies the connections. In reality, the BotOrchestrator would hold instances of all the other "expert" classes).