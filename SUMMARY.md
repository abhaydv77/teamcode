# Architecture Summary

## The Problem

Single AI prompts are fragile. One model handles everything — requirements, design, code, testing, review — and a single weak output derails the whole result. There's no specialization, no iteration, no accountability.

## The Solution

TeamCode replaces the monolithic prompt with a **team of specialized agents**. Each agent has one job, a dedicated system prompt, and can be powered by a different model. An orchestrator manages the workflow, passes context between agents, and collects the results.

---

## Design Principles

### 1. Roles over models

A Product Manager should work the same way whether it runs on GPT-4o, Claude, or Gemini. Models are a configuration detail, not a design concern. Every agent receives a `(config, provider)` pair at construction — the agent never knows or cares which LLM is behind the provider.

### 2. Everything is a registry

Agents, tools, and plugins are discovered through registries, not imported directly. Adding a new agent means writing one class and registering it. The orchestrator, CLI, and UI depend on abstractions, not concrete implementations.

### 3. Events, not callbacks

Communication between components uses typed events (`SessionStarted`, `AgentFinished`, `TaskCreated`). Handlers subscribe to event types, not string names. This makes the system introspectable, testable, and extensible by plugins.

### 4. Prompts are data

System prompts live in `prompts/*.md` files, not in Python strings. Contributors can edit prompts without touching code. The prompt loader uses `importlib.resources` so prompts work in both development and production installs.

### 5. Separation of concerns

```
Domain models  →  Pure Pydantic, zero framework dependencies
Providers      →  Only know about CompletionRequest/Response
Agents         →  Only know about their role + context
Orchestrator   →  Only knows about registries + events
UI             →  Only knows about app state + commands
```

No layer imports from a layer above it. No circular dependencies.

---

## Layer-by-layer Breakdown

### Domain Layer (`domain/`)

Pure data models with no dependencies beyond Pydantic:

- `Agent` / `Role` — who the agents are
- `Task` / `TaskQueue` — what needs to be done
- `Message` — what was said
- `SessionContext` — the shared state for a session

Everything else in the project imports from domain. Domain never imports from anything else.

### Provider Layer (`providers/`)

The `BaseProvider` ABC defines one method: `complete(request) -> response`. The `LiteLLMProvider` wraps the `litellm` library to support every major model provider through a single interface. The `ProviderManager` adds retries with exponential backoff and API key validation.

To add a new provider: implement `BaseProvider`, register it. That's it.

### Agent Layer (`agents/`)

`BaseAgent` is the ABC. Each agent receives a config (which role, which model, which provider) and a session context. The `AgentRegistry` stores agents by role name and can instantiate them on demand.

The orchestrator calls `AgentRegistry.create(role, config, provider)` — it never touches concrete agent classes.

### Orchestrator Layer (`orchestrator/`)

Three responsibilities split across three files:

| File | Responsibility |
|------|---------------|
| `engine.py` | Execution loop: iterate agents, emit events, manage the session lifecycle |
| `router.py` | Decision logic: which agent should run next based on current context |
| `scheduler.py` | Task management: queue, dependency resolution, ordering |

The event system uses typed dataclasses (`SessionStarted`, `AgentFinished`, etc.) instead of string-keyed dictionaries. Handlers subscribe to types, not strings.

### Tool Layer (`tools/`)

`BaseTool` ABC with `name` and `execute()`. The `ToolRegistry` provides lookup. Future tools (filesystem, git, browser, codebox) will each be one file, one class, one registration call.

### Memory Layer (`memory/`)

`BaseMemory` ABC with `add()`, `get_context()`, `clear()`. Two stubs exist (`SQLiteMemory`, `SummaryMemory`). The `ConversationManager` wraps memory with higher-level operations: formatting messages for providers, token counting, context trimming.

### Workspace Layer (`workspace/`)

Central interface for all file operations: `read_file()`, `write_file()`, `glob()`, `file_exists()`. The rest of the codebase never calls `open()` or `Path.read_text()` directly.

### Storage Layer (`storage/`)

`BaseStorage` ABC for persistent key-value storage. `SQLiteStorage` implements it with `aiosqlite`. Future backends (PostgreSQL, Redis, file-based) swap in without changing any other code.

### Plugin Layer (`plugins/`)

`BasePlugin` ABC with `initialize(app)` and `shutdown()`. The `PluginRegistry` manages the lifecycle. Everything is ready for plugins — the event bus, the registries, and the app state are all accessible through the plugin interface.

### Telemetry Layer (`telemetry/`)

`BaseTelemetry` ABC with `capture(event, data)`. The `LoggingTelemetry` implementation writes structured log lines. Future: metrics dashboards, execution tracing, performance analysis.

### UI Layer (`ui/`)

A Textual application with:

- **Startup screen** — ASCII splash, auto-transitions to main
- **Chat area** — RichLog-based message display
- **Command palette** — Filtered list of slash commands, triggered by `/`
- **Input bar** — Keyboard-driven input with command dispatch
- **Status bar** — Reactive project/session state display

The UI is a client of the app state — it never manages sessions or tasks directly. All state lives on `TeamCodeApp` and commands operate through `app.run_command()`.

### CLI Layer (`cli/`)

Thin entry points: `teamcode run`, `teamcode init`, `teamcode config`. The `run` command launches the TUI. The CLI never contains business logic — it routes to the appropriate layer.

---

## Data Flow

```
User types "/session start"
  → InputBar detects submission
  → MainScreen dispatches to app.run_command()
  → App looks up "session" in CommandRegistry
  → SessionCommand.execute(app, ["start"])
    → Sets session_state["status"] = "active"
    → Posts CommandResult to MainScreen
  → MainScreen shows result in ChatArea
  → StatusBar updates via reactive

User types "Build a REST API"
  → InputBar detects non-command text
  → MainScreen calls _handle_message()
  → Message posted to ChatArea
  → ConversationManager.add() stores it
  → (future) Orchestrator picks up the task
    → Scheduler enqueues it
    → Router picks ProductManager
    → Engine runs PM → Architect → Developer → Reviewer → Tester
    → Each result streamed to ChatArea via events
```

---

## Extending TeamCode

### Add a new command

Create one file in `ui/commands/`:

```python
from teamcode.ui.commands.base import BaseCommand

class MyCommand(BaseCommand):
    name = "mycommand"
    description = "Does something useful"

    async def execute(self, app, args):
        await app.post_message(app.CommandResult("Done!"))
```

It's automatically discovered by `CommandRegistry.discover()`.

### Add a new agent role

Create one file in `agents/`:

```python
from teamcode.agents.base import BaseAgent

class SecurityAuditor(BaseAgent):
    async def execute(self, context):
        request = self.build_request(context)
        return await self.provider.complete(request)

# Register it
AgentRegistry.register("security_auditor", SecurityAuditor)
```

### Add a new tool

```python
from teamcode.tools.base import BaseTool, ToolResult

class GitTool(BaseTool):
    name = "git"
    async def execute(self, **kwargs):
        return ToolResult(success=True, data="git output")

ToolRegistry.register("git", GitTool)
```

### Add a new provider

```python
from teamcode.providers.base import BaseProvider, CompletionRequest, CompletionResponse

class CustomProvider(BaseProvider):
    name = "custom"
    supported_models = ["custom-model"]
    async def complete(self, request):
        ...

ProviderRegistry.register("custom", CustomProvider)
```
