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
