# Running TeamCode

## Prerequisites

- Python 3.11+
- API keys for the LLM providers you want to use

## Installation

### From source (development)

```bash
git clone <repo-url>
cd teamcode

# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate  # or: .venv\Scripts\activate on Windows

# Install with dev dependencies
pip install -e ".[dev]"
```

### Optional dependencies

```bash
# LiteLLM support (for multi-provider API access)
pip install -e ".[litellm]"

# SQLite storage (for session persistence)
pip install -e ".[storage]"

# Everything
pip install -e ".[dev,litellm,storage]"
```

## Setup

### 1. Configure API keys

Copy the example env file and add your keys:

```bash
cp .env.example .env
```

Edit `.env`:

```env
OPENAI_API_KEY="sk-..."
ANTHROPIC_API_KEY="sk-ant-..."
GEMINI_API_KEY="..."
GROQ_API_KEY="gsk_..."
MISTRAL_API_KEY="..."
DEEPSEEK_API_KEY="sk-..."
OPENROUTER_API_KEY="sk-or-..."
```

You can also export them as environment variables instead.

### 2. Verify the installation

```bash
# Run the test suite
pytest -v

# Check the CLI
teamcode --help

# Check linting
ruff check src/
```

## Running the Application

### Launch the TUI

```bash
teamcode run session
```

This opens the Textual terminal UI with:

```
╔═══════════════════════════════════════╗
║           T E A M C O D E            ║
╚═══════════════════════════════════════╝

Terminal-First AI Software Engineering Team v0.1.0

Type /help to see available commands.
```

### With a task description

```bash
teamcode run session "Build a CRUD API for a task manager"
```

The task is stored in the session context for future agent workflows.

## Using the TUI

### Keyboard shortcuts

| Key | Action |
|-----|--------|
| `Type /` | Open command palette |
| `↑` / `↓` | Navigate command palette list |
| `Enter` | Execute selected command / send message |
| `Escape` | Close command palette / quit application |
| `Ctrl+C` | Quit application |

### Slash commands

| Command | Description |
|---------|-------------|
| `/help` | Show available commands and usage |
| `/config` | View current configuration and API key status |
| `/agents` | List agent roles and assignments |
| `/models` | Show available models by provider |
| `/session start` | Start a new session |
| `/session stop` | Stop the current session |
| `/usage` | Display token usage and cost estimates |
| `/history [n]` | Show last N command/message entries |
| `/clear` | Clear the chat area |
| `/exit` | Exit the application |

### Command palette

Type `/` in the input bar to open the command palette. Continue typing to filter commands:

```
> /co
  ┌──────────────────────────────────┐
  │ /config    View configuration    │
  │ /coordinator  Coordinator agent  │
  └──────────────────────────────────┘
```

Use `↑`/`↓` to select and `Enter` to execute.

### Regular messages

Type text without a leading `/` to post a message to the chat area:

```
> Let's build a user authentication system
```

Messages are stored in the conversation history and will be sent to the AI team in future sessions.

## Configuration

### Viewing config

```bash
teamcode config show
```

### Setting config values

```bash
teamcode config set log_level DEBUG
```

### Project initialization

```bash
teamcode init project my-ai-project
```

## Development

### Running tests

```bash
# All tests
pytest -v

# Specific test file
pytest tests/unit/domain/test_agent.py -v

# With coverage
pip install pytest-cov
pytest --cov=src/teamcode
```

### Code quality

```bash
# Lint checking
ruff check src/

# Auto-fix lint issues
ruff check --fix src/

# Format checking
ruff format --check src/

# Auto-format
ruff format src/

# Type checking
mypy src/teamcode
```

### Adding a new command

1. Create a file in `src/teamcode/ui/commands/`
2. Extend `BaseCommand` with `name`, `description`, and `execute()`
3. Restart the app — it's auto-discovered

### Adding a new agent role

1. Create a file in `src/teamcode/agents/`
2. Extend `BaseAgent` with `execute()`
3. Register with `AgentRegistry.register("role_name", AgentClass)`

## Project structure

```
teamcode/
├── src/teamcode/       # Main package
│   ├── domain/         # Core data models
│   ├── agents/         # Agent roles + registry
│   ├── providers/      # LLM providers + manager
│   ├── orchestrator/   # Execution engine + events
│   ├── tools/          # Tool integrations
│   ├── memory/         # Conversation management
│   ├── workspace/      # File system operations
│   ├── storage/        # Persistent storage
│   ├── plugins/        # Plugin system
│   ├── telemetry/      # Logging + metrics
│   ├── prompts/        # System prompt files
│   ├── config/         # Settings
│   ├── cli/            # CLI entry points
│   └── ui/             # Terminal UI
├── tests/              # Test suite
├── pyproject.toml      # Project configuration
├── .env.example        # API key template
└── .gitignore
```

## Troubleshooting

**`ModuleNotFoundError: No module named 'litellm'`**
The LiteLLM provider is available but not installed. Run `pip install teamcode[litellm]` or `pip install litellm`.

**`teamcode: command not found`**
Make sure your virtual environment is activated and the package is installed: `pip install -e .`

**TUI doesn't render properly**
Make sure your terminal supports Unicode and 24-bit color. Most modern terminals (iTerm2, Kitty, Alacritty, Windows Terminal) work well. The `TERM` environment variable should be set to `xterm-256color` or similar.

**Port already in use**
TeamCode doesn't use network ports. If you see an address-in-use error, check for other processes.
