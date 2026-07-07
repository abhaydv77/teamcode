## 🚧 TeamCode

> Terminal-first AI software engineering team.

**Status:** Under active development.

TeamCode is an open-source experiment to build a local AI engineering team where multiple AI models collaborate through specialized roles instead of one model trying to do everything.

The project is not production-ready yet, but the architecture is actively being built in public.

# If you want to understand why I started building TeamCode and where I see it going, take a look at VISION.md.

## TeamCode

**Terminal-first, local AI software engineering team.**

TeamCode is an open-source orchestrator where multiple AI models collaborate as a software engineering team — Product Manager, Architect, Developer, Reviewer, Tester, and Coordinator — all through your terminal.

This is not another AI chat app or AI IDE. It's a framework for structured, role-based AI collaboration where you bring your own API keys and assign any model to any role.

---

## Quick Start

```bash
# Install
pip install teamcode

# Launch the TUI
teamcode run session

# Or with a task
teamcode run session "Build a REST API for a todo app"
```

Set your API keys in `.env` or export them:

```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

---

## How It Works

TeamCode replaces a single monolithic AI prompt with a **team of specialized agents**:

```
You ──> Coordinator ──> Product Manager ──> Architect
                                  │
                    ┌─────────────┼─────────────┐
                    ▼             ▼             ▼
              Developer       Reviewer       Tester
                    │             │             │
                    └─────────────┼─────────────┘
                                  ▼
                              Result
```

Each agent has a role-specific system prompt, can be powered by a different model, and passes context to the next agent through a shared session.

---

## Configuration

```yaml
# teamcode.yml
agents:
  product_manager:
    model: gemini/gemini-2.5-pro
  coordinator:
    model: groq/qwen-2.5-32b
  developer:
    model: anthropic/claude-sonnet-4-20250514
  reviewer:
    model: openai/gpt-4o
  tester:
    model: mistral/mistral-large-latest
```

---

## Key Features

- **Role-based agents** — Each agent has a defined responsibility and system prompt
- **Any model, any role** — Bring your own API keys (OpenAI, Anthropic, Gemini, Groq, Mistral, DeepSeek, OpenRouter)
- **Terminal-first** — Beautiful Textual TUI with command palette, chat area, and keyboard navigation
- **Slash commands** — `/help`, `/config`, `/agents`, `/session`, and more
- **Extensible** — Add new agents, tools, providers, or plugins with minimal code
- **Event-driven** — Typed event system for clean decoupling between components
- **Open source** — MIT license, built for contributors

---

## Architecture

```
teamcode/
├── domain/          # Core data models (Agent, Task, Message, Session)
├── agents/          # Role definitions + registry
├── providers/       # LLM interface (LiteLLM for all models)
├── orchestrator/    # Engine, router, scheduler, typed events
├── memory/          # Conversation history, context management
├── tools/           # Tool integrations (filesystem, git, etc.)
├── workspace/       # Project file operations
├── storage/         # Persistent storage (SQLite)
├── plugins/         # Plugin system for extensions
├── telemetry/       # Logging and event capture
├── prompts/         # Role system prompts (markdown files)
├── config/          # Settings and configuration
├── cli/             # CLI entry points (run, init, config)
└── ui/              # Terminal UI (Textual application)
```

---

## Project Status

TeamCode is in early development. The foundation is solid, and AI agent integration is the next milestone.

**Implemented:**
- Full project foundation with clean architecture
- Terminal UI with command palette
- Slash commands and keyboard navigation
- Provider, agent, tool, and plugin registries
- Typed event system
- Memory, storage, workspace, and telemetry layers
- Configuration management

**Coming soon:**
- AI agent implementations
- Multi-step orchestration workflows
- Tool integrations (filesystem, git, terminal)
- Plugin ecosystem
- Session persistence

---

## License

MIT
# teamcode
