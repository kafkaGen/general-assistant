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

- [ ] In WebUI i want to see chat as user input, agent final output and hidden (or not) intermediate results with expand tools output
- [ ] I want my endpoints output the structure with list of new messages
- [ ] I want to stream messages to the WebUI (separate endpoints for stream and not stream)
- [ ] refactor endpoint inputs and outputs models
- [x] I want to observe graph with langgraph studio
- [x] I want to manage all prompts with langsmith
- [x] I want to configure GeneralWorkflow, Tools and AgentFactory with global Settings
- [x] I want to redo my Workflow to async and tools also

- [ ] fetch page tool can fetch to long page that blow the context window

- [ ] get back to ShortTerm memory implementation issue
- [ ] after come back to chat endpoint to improve the error handling from workflow and its output
- [ ] create postgress db with docker compose and add checkpoint to that to the agent (think how to visualize this also on web ui)
- [ ] add long term memory support to agent (add fact, delete fact, retrieve/ search fact)
- [ ] add promper short term memory support (some summarization after k messages)
- [ ] add meta learning (somehow auto update the prompt, tools description, etc., in reflection stage add some meaningful conclusion to long term memory on beter task completion)
- [ ] long term memory possible category: user facts, task/ workflow insights, general insights of agent about itself and world

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
