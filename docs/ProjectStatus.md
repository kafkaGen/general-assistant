# Project Status

## TO DO

- [x] Download GAIA dataset
- [x] Create Chat Endpoint
- [x] Create Chainlit Interface with chat history
- [x] update the Chainlit .md file
- [x] update the Chainlit to send the history of the chat with endpoint
- [x] code overview the api folder fully, make as good as possible
- [x] make the config folder as good as possible for usage
- [x] double check chainlit file is okay
- [x] refactor the AssistantClient
- [x] git push commit with webui updates
- [x] douple check all other code changes (uv, precommits)
- [x] add simple README.md
- [x] develop Agent Workflow with web search tool
- [x] add for agent two tools - search the web and Python interprenter (Calculator)

- [x] In WebUI i want to see chat as user input, agent final output and hidden (or not) intermediate results with expand tools output
    - [x] update chainlit to hide intermediat state, pretty print of jsons (showing intermediat step during streaming)
    - [x] issue with double response
    - [x] error on continued dialog
    - [x] deploy with docker and left
- [x] I want my endpoints output the structure with list of new messages
- [x] I want to stream messages to the WebUI (separate endpoints for stream and not stream)
- [x] refactor endpoint inputs and outputs models
- [x] I want to observe graph with langgraph studio
- [x] I want to manage all prompts with langsmith
- [x] I want to configure GeneralWorkflow, Tools and AgentFactory with global Settings
- [x] I want to redo my Workflow to async and tools also

- [x] restructed the src folder to make more modular and code-shareble
- [x] defined the logic of flexible configuration with BaseNamedSettings
- [x] add streaming support to the general assistant
- [x] update the api to proper call and process output from general assistant (invoke and stream)
- [x] create separate module 'models' with all data models and fill it
- [x] define proper settings from evaluators and api, assistant_client
- [x] update webui to receive new streaming from custom react assistant
- [x] check if assistant_client work correct
- [x] improve the tools, make them return the proper formatted string
- [x] create the dataset in langsmith with level 1 without files
- [x] update evaluators to not use the api but graph directly
- [x] create the set of evaluators (and summary evaluators) for current dataset
- [x] write the main script to run the evaluation on the dataset and evaluators
- [x] add cost and token traking on evaluation
- [x] (optional) create the datatset for evaluators (label result) to check of evaluators prompt works correct
- [x] improve the agent output to see the used tools, and trjactory
- [x] finish course on the langsmith to unialize it during evaluaiton
- [x] potentialy create own ReAct like agent, do not use prebuild
- [x] create tool to get current date or paste it with prompt
- [x] (optional) update the workflow to output more structured answer of some postprocessing (or invoke with structured, stream without)
- [x] use githup assistant for pr code review
- [x] fix review comments from copilot in pr

- [x] the configuration way
    - i need to have to variable of settings: app_settings, main_agent_settings
    - app_settings not changes after the start of the application
    - user with request can send the config that particaly change the configuration (change model provider, retrival method, etc)
    - main_agent created on every call and consume default pyndatic settings 
    merged with user passed config (dynamic changing and stateless)

---

# Project
- [x] create config folder where yaml configs stored, have ENV VAR that indicate to yaml conf or use default, raise error if wrong config
- [x] have default config in FastAPI that you pass to general_agent in endpoint (in future merge with client needs)
- [x] all models related stuff takes from config in workflow and use config to configure model and etc, pass config during invoke of the workflow
- [x] think of better approach of encapsulation the llm block with prompt/output/tools (if needed, or just send model_client and do all this stuff inside the workflow anyway)
- [ ] perform code review of the projects if AI
- [ ] add mutli user support in application
- [ ] add setting to application with some configuration
- [ ] review error handling in workflows and api
- [ ] write unit test for the code-base

# General Agent
- [x] create function that return current date that will call for each prompt
- [ ] make llm only function calling and instruct to think after each tool result and before answering to provide grounded answer
- [ ] use xml tags in each prompt, add tags output_schema, examples (also role, task, ...)
- [ ] update final answer prompt to generate very short, precise answer
- [ ] add steps limit for agent
- [ ] add the reflection node that check the final answer and if not match user requirements fallback with some recommendation, set limit for n reflections

- [ ] add option to pass as input to agent files of specific format
- [ ] add rag tool for agent

# Tools
- [x] create tool for producing thinking process in agent loop
- [x] create tool for producing final answer in agent loop
- [x] add tool for save math calculation

# Web Search Agent
- [ ] general agent should perform user query decomposition and reflection on result
- [ ] search query expansion (test, maybe pass this to general agent)
- [ ] search and retrieve top N documents with search engine to request
- [ ] iteratavely start from top to bottom urls
- [ ] fetch whole url, chunk and summarise, provide to llm (maybe with some loop if to long context)
- [ ] llm should choose if to continue processing next summary or to go to another url, or got final response
- [ ] set limit of such recursion or limit of max steps, instruct llm to also back to previous steps if no relevant info further
- [ ] agent should receive the enriched context, not the answer
- [ ] add tool to extract data from youtube
- [ ] add tool to extract data from (downloaded) web files

# RAG
- [ ] create indexing workflow as tool that will be trigered when document loaded to chat or user, store in qdrant
- [ ] add suport to process next files formats: {'pptx', 'docx', 'py', 'txt', 'mp3', 'xlsx', 'png'}
- [ ] create the rag search workflow that will be used as tool to search for user specified docs (docs can be per session and per user)
- [ ] indexing tool can be used in web search agent to index some large web pages
- [ ] creating summary of the document
- [ ] rewatch localGPT video as idea
- [ ] multimodal
- [ ] create also tool to search not for chunk, but for document summary to retrieve relevant documents names etc

# Evaluation
- [ ] test system with different models and providers
- [ ] create eval dataset for each workflow (or even blocks)
- [ ] create eval dataset for each llm-as-judge and align to human on 90%
- [ ] (optional) write script and evaluators for pairwise evaluation on experiments
- [ ] create the dataset for tool class (tool name and args, expected outputs) and evaluate it also (tool regression check)

# Memory
- [ ] create schema for qdrant to store the chat session (user_id, message_id, role, content, created_at, updated_at, is_summarised, metadata) + store summary for each chat session
- [ ] create chat memory nodes for extracting the summary and changing the messages order, appending all new messages to base, decide if to update the summary,
    you append this nodes at the beggining and the end of the workflow to add chat history compression (or create workflow that consume current and add this nodes automaticaly) (or somehow in another thread/parallel?),
    you add the tool for searching the full chat history
- [ ] provide option to retive messages by sim, id for session, get summary for session
- [ ] in qdrant collect human/agent persona profiles that will be inserted in system prompt (size limited) per user, provide function for extraction
- [ ] in qdrant collect memory blocks that can be some fact, instruction or experience per user (say memory schemas but different tags/type, etc)
- [ ] provide to agent with tools to extract memory and update memory

---

# Security
- [ ] add guardrails to input and output of agent (in another thread/parallel?)
- [ ] create secure dataset users
- [ ] add auth

# Audio
- [ ] add audio text input
- [ ] add audio answer output

# Deployment
- [ ] pass course on helm and kubernetis
- [ ] pass course on cloude deployment
- [ ] use kubernetes
- [ ] ECS on AWS multi-region
- [ ] add ci/cd (formmating test, unit test, regression test)
