
# Ali-Shadid-AiXplain-Certification-Project
# 🏛️ Government Regulations Agent
 
A powerful AI agent designed to assist users in querying and analyzing **government regulations**, **federal policies**, and **compliance documents**. This system uses Retrieval-Augmented Generation (RAG) techniques powered by `aiXplain`, integrates federal data APIs, and allows file-based indexing for grounded policy responses.
 
---
 
## 📌 What the Agent Does
 
This intelligent assistant specializes in:
 
- 🧾 Answering **federal policy questions** using the Federal Register API
- 🧾 Answering **Specifications for Electrical Installations** using internal knowledge
- 🧾 Answering **Firearms Provisions in US States** using internal knowledge
- 🗂️ Searching **uploaded PDF, CSV, XLSX documents** using chunked indexing and providing grounded responses with citations
- 🌐 Scraping **web content** for specific link provided by the user to answer via a web-scraper tool
- ✅ Enforcing **strict boundaries** to only answer regulation, law, policy, and compliance-related queries
 
---
 
## ⚙️ Setup Instructions
- At first, open Certification_Project.ipynb
- Add your API Key
- Run each cell, except for the 'index_delete' which is used to delete the index only (if you want)
- Change file names to the files you have
- In the last cell, you will see the agent ID and index ID
- Copy these and use them in the AiXplain_Project.py
- use `streamlit run AiXplain_Project.py` to start the UI
 
## 📚 Dataset / Source Links
- Firearms Provisions in US States: https://www.kaggle.com/datasets/jboysen/state-firearms
- Specifications for Electrical Installations: https://www.nationalgridus.com/media/pronet/constr_esb750.pdf
 
## 🛠 Tool Integration Steps
✅ 1. Federal Register Tool
  - A Python utility that queries https://www.federalregister.gov/api/v1/documents.json based on keywords.
✅ 2. Web Scraper Tool
  - Configured via aiXplain ModelFactory to extract the text from any public webpage provided by the user.
✅ 3. File Indexing Tool
  - Chunks files into customizable text segments
  - Converts PDF, CSV, and Excel files into queryable knowledge base
  - File content is embedded and stored using aiXplain.IndexFactory
 
## 💬 Example Inputs & Outputs
- 🔍 Input 1 (Federal Policy)
  - What is Executive Order 14067 about?
- ✅ Output:
  - Executive Order 14067 focuses on the promotion of economic growth and the establishment of a policy framework for digital assets.
 
- 🔍 Input 2 (Document Query)
  - What are the key firearm restrictions in California?
- ✅ Output:
  - Key firearm restrictions in California include: 1) No magazines with a capacity of more than 10 rounds are allowed. 2) Firearm possession is prohibited for individuals who have committed a violent misdemeanor. 3) A firearm safety certificate is required for the purchase of firearms.
 
- 🔍 Input 3 (Web Scrape)
  - What was the new law that was stated here? [https://www.bbc.com/news/articles/cxeey754r9eo](https://www.bbc.com/news/articles/cxeey754r9eo)
- ✅ Output:
  - New laws that will offer protection to pets and introduce tougher penalties for those guilty of animal cruelty will come into effect next month. Owners of cats, dogs, and other pets will be legally required to ensure their welfare, with increased penalties for animal cruelty up to five years in jail or an unlimited fine. 
## 🚀 Future Improvements
- 💡 Add More Agents:
	- Summarization agent for lengthy policy docs
	- Analytics agent for compliance gaps
- 🖥️ UI Enhancements:
	- File preview before indexing
	- Chat history management and export
- 🔗 Data Integrations:
	- Connect to government portals like data.gov or EPA APIs
- 🔐 Auth Layer:
	- Add user authentication for secure enterprise use
 
