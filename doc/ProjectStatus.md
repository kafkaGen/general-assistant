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
- [ ] update final answer prompt to generate very short, precise answer
- [ ] (optional) write script and evaluators for pairwise evaluation on experiments
- [x] (optional) create the datatset for evaluators (label result) to check of evaluators prompt works correct
- [ ] create the dataset for tool class (tool name and args, expected outputs) and evaluate it also (tool regression check)
- [x] improve the agent output to see the used tools, and trjactory
- [x] finish course on the langsmith to unialize it during evaluaiton
- [x] potentialy create own ReAct like agent, do not use prebuild
- [x] create tool to get current date or paste it with prompt
- [x] (optional) update the workflow to output more structured answer of some postprocessing (or invoke with structured, stream without)
- [x] use githup assistant for pr code review
- [x] fix review comments from copilot in pr
- [ ] if the system become milti agent or multi workflow for each new agent or workflow its own dataset and evaluation

- [x] the configuration way
    - i need to have to variable of settings: app_settings, main_agent_settings
    - app_settings not changes after the start of the application
    - user with request can send the config that particaly change the configuration (change model provider, retrival method, etc)
    - main_agent created on every call and consume default pyndatic settings 
    merged with user passed config (dynamic changing and stateless)
- [ ] add suport for agent to process next files formats: {'pptx', 'docx', 'py', 'txt', 'mp3', 'xlsx', 'png'}
- [ ] fetch page tool can fetch to long page that blow the context window
- [ ] add steps limit for agent


- [ ] use prompt caching
- [ ] use thinking model (also stream it thinking)
- [ ] test system with different models
- [ ] get back to ShortTerm memory implementation issue
- [ ] after come back to chat endpoint to improve the error handling from workflow and its output
- [ ] create postgress db with docker compose and add checkpoint to that to the agent (think how to visualize this also on web ui)
- [ ] add long term memory support to agent (add fact, delete fact, retrieve/ search fact)
- [ ] add promper short term memory support (some summarization after k messages)
- [ ] add rag support (workflow) for agent to store some info
- [ ] add meta learning (somehow auto update the prompt, tools description, etc., in reflection stage add some meaningful conclusion to long term memory on beter task completion)
- [ ] long term memory possible category: user facts, task/ workflow insights, general insights of agent about itself and world
- [ ] write unit test for the code-base
- [ ] add units test and agent test to ci/cd

- [ ] add guardrails to input and output of agent

# Tree

``` markdown
general-assistant/
├── src/
│   └── general_assistant/
│       ├── __init__.py
│       ├── main.py                    # FastAPI app entry point
│       ├── config/
│       │   ├── __init__.py
│       │   ├── settings.py            # Environment-based configuration
│       │   └── logging.py             # Logging configuration
│       ├── core/
│       │   ├── __init__.py
│       │   ├── agent.py               # Main AI Agent orchestrator
│       │   ├── memory.py              # Conversation memory management
│       │   ├── tools/                 # Agent tools/capabilities
│       │   │   ├── __init__.py
│       │   │   ├── base.py            # Base tool interface
│       │   │   ├── web_search.py      # Web search capability
│       │   │   ├── file_operations.py # File handling
│       │   │   └── calculator.py      # Math operations
│       │   └── llm/
│       │       ├── __init__.py
│       │       ├── client.py          # LLM client abstraction
│       │       ├── providers/         # Different LLM providers
│       │       │   ├── __init__.py
│       │       │   ├── openai.py
│       │       │   ├── anthropic.py
│       │       │   └── local.py
│       │       └── prompts.py         # System prompts
│       ├── api/
│       │   ├── __init__.py
│       │   ├── routes/
│       │   │   ├── __init__.py
│       │   │   ├── chat.py            # Chat endpoints
│       │   │   ├── health.py          # Health checks
│       │   │   └── admin.py           # Admin endpoints
│       │   ├── middleware/
│       │   │   ├── __init__.py
│       │   │   ├── auth.py            # Authentication
│       │   │   ├── rate_limit.py      # Rate limiting
│       │   │   └── cors.py            # CORS handling
│       │   └── schemas/
│       │       ├── __init__.py
│       │       ├── chat.py            # Chat request/response models
│       │       └── common.py          # Common schemas
│       ├── services/
│       │   ├── __init__.py
│       │   ├── chat_service.py        # Chat business logic
│       │   ├── user_service.py        # User management
│       │   └── session_service.py     # Session management
│       ├── storage/
│       │   ├── __init__.py
│       │   ├── database.py            # Database connections
│       │   ├── models/                # Database models
│       │   │   ├── __init__.py
│       │   │   ├── user.py
│       │   │   ├── conversation.py
│       │   │   └── session.py
│       │   └── repositories/          # Data access layer
│       │       ├── __init__.py
│       │       ├── user_repo.py
│       │       └── conversation_repo.py
│       └── utils/
│           ├── __init__.py
│           ├── security.py            # Security utilities
│           ├── validators.py          # Input validation
│           └── exceptions.py          # Custom exceptions
├── tests/
│   ├── __init__.py
│   ├── conftest.py                    # Pytest configuration
│   ├── unit/
│   │   ├── test_agent.py
│   │   ├── test_tools/
│   │   └── test_services/
│   ├── integration/
│   │   ├── test_api.py
│   │   └── test_database.py
│   └── e2e/
│       └── test_chat_flow.py
├── deployment/
│   ├── docker/
│   │   ├── Dockerfile
│   │   ├── docker-compose.yml
│   │   └── docker-compose.prod.yml
│   ├── kubernetes/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── ingress.yaml
│   └── terraform/                     # Infrastructure as code
├── docs/
│   ├── api.md                         # API documentation
│   ├── deployment.md                  # Deployment guide
│   └── architecture.md                # System architecture
├── scripts/
│   ├── setup.sh                       # Development setup
│   ├── migrate.py                     # Database migrations
│   └── seed_data.py                   # Sample data
├── .env.example                       # Environment variables template
├── .gitignore
├── .dockerignore
├── pyproject.toml                     # Dependencies and build config
├── README.md
└── CHANGELOG.md
```
