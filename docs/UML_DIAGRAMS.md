**Use Case Diagram**

[Team Member] --(Posts Message)--> [Google Chat API]
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
| BotOrchestrator  |--------------->| GoogleChatReader   |
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