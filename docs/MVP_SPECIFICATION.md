### **Project Specification: Google Chat Product Link Scraper (Version 1.0 - MVP, Rev 2)**

**1.0 Overview & Mission Statement**

To provide a team of interns and their project leads with a simple, automated way to track key information about product links shared in Google Chat, starting with the item name and model number, and logging this data to a central Google Sheet.

**2.0 Target Audience**

*   **Primary Users:** University interns working on various projects.
*   **Secondary Users:** Project leads overseeing the interns' work.

**3.0 Core Problem**

Product links for project components are shared frequently in a Google Chat space. Manually tracking these links, along with their associated project, price, availability, and specifications (like model numbers), is tedious, error-prone, and inefficient. This leads to lost information and wasted time.

**4.0 Key Terminology**

*   **Backend Service:** A locally-run or cloud-hosted application that will contain the core logic for this system. It receives data from the Google Chat API and orchestrates the fetching, parsing, and data submission processes.
*   **LLM (Large Language Model):** The AI model used for parsing. For the MVP, this will be accessed via an AI Studio API. In the future, this could be a locally hosted model.

**5.0 Functional Requirements (In Scope for MVP)**

The system **SHALL**:
*   **FR-1:** Authenticate with the Google Chat API to read messages from a designated space.
*   **FR-2:** Identify and extract URLs from messages posted in the space.
*   **FR-3:** For each extracted URL, the Backend Service **SHALL** fetch the full HTML content of the linked page.
*   **FR-4:** The Backend Service **SHALL** pass the HTML content to an LLM.
*   **FR-5 (Revised):** The LLM's primary task **SHALL** be to extract the **Item Name** and the most prominent **Product Identifier (Model Number or SKU)** from the HTML.
*   **FR-6 (Revised):** The system **SHALL** format the extracted data into a structured JSON object. The primary data field will be a concatenation of the two extracted values in the format: `item_name-product_identifier`.
*   **FR-7:** The system **SHALL** authenticate with the Google Sheets API.
*   **FR-8:** The system **SHALL** append the data from the JSON object as a new row in a specified Google Sheet.

**6.0 Out of Scope (Post-MVP)**

The following features are explicitly **NOT** part of the MVP and will be considered for future versions:
*   Extracting additional metadata from the Google Chat message (e.g., username, timestamp).
*   Extracting additional product information (e.g., price, availability, **vendor/platform**).
*   **Reliable distinction between manufacturer model number and vendor SKU.**
*   **Parsing of pricing metadata (e.g., tax information).**
*   Advanced data cleanup (e.g., sanitizing URLs).
*   Advanced formatting or categorization of data within the Google Sheet.
