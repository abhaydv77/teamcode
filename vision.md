# VISION: TeamCode (v1.0 MVP)

## Purpose

TeamCode is a terminal-first operating system for AI software engineering teams.

The goal is not to build another AI coding assistant.

The goal is to coordinate multiple AI models and coding agents so each one focuses on a single responsibility instead of asking one model to do everything.

Every architectural decision should support this idea.

---

# The Problem

Current AI coding workflows usually look like this:

User
↓
One AI
↓
Planning
Coding
Review
Debugging
Documentation

This works for small tasks, but large software projects become difficult because one model has to constantly switch responsibilities and consume unnecessary context and tokens.

Different models also have different strengths.

Some reason better.

Some are much faster.

Some write better code.

Some review better than they generate.

TeamCode exists to orchestrate those strengths instead of replacing them.

---

# The Goal

The user builds an AI software engineering team.

Each member has exactly one responsibility.

Example:

Product Manager
↓
Coordinator
↓
Developer
↓
Reviewer
↓
Tester
↓
Documentation

The user decides:

- which provider powers every role
- which model every role uses
- how every role behaves
- how much budget should be spent
- which tools every role can access

Nothing should be hardcoded.

Everything should be configurable.

---

# Product Principles

## 1. Terminal First

The terminal is the product.

No web dashboard.

No unnecessary UI.

Everything should be keyboard driven.

Speed is more important than animations.

The interface should feel closer to Claude Code than a traditional application.

---

## 2. Human Always Controls The Team

TeamCode never hides decisions.

The user should always understand

- why an agent was chosen
- what prompt was generated
- what tools were used
- what files changed
- how many tokens were consumed

Visibility is more important than automation.

---

## 3. One Responsibility Per Agent

Every role should solve one problem only.

Examples

- Product Manager
- Developer
- Reviewer
- Researcher
- Token Manager
- Documentation Writer

Do not combine unrelated responsibilities.

Small focused agents are preferred over one giant prompt.

---

## 4. Runtime Should Be Fast

Agent communication should happen entirely in memory.

Use:

- EventBus
- Task Objects
- Shared Context

Avoid using markdown files for runtime communication.

Disk should never become the message bus.

---

## 5. Documentation Is A Side Effect

Documentation exists for humans.

It should never slow down runtime execution.

After important work finishes, TeamCode automatically generates project history inside:

.teamcode/

tasks/
reviews/
plans/
decisions/
progress.md
sessions/

This history should help both humans and future AI sessions understand why decisions were made.

---

## 6. Adapters Instead Of Tight Coupling

TeamCode should never depend on a single coding agent.

The Developer role should work with interchangeable adapters.

Examples:

OpenCode

Claude Code

Codex CLI

Gemini CLI

Aider

Future coding agents

Changing the developer backend should not require changes to the orchestrator.

---

## 7. Context Is Shared

All agents should work from the same project context.

Project context includes:

- conversation history
- project files
- git state
- current task
- previous decisions
- workspace metadata

No agent should maintain isolated knowledge.

---

# Engineering Rules

Prefer composition over inheritance.

Prefer interfaces over implementations.

Prefer configuration over hardcoded behavior.

Prefer events over direct dependencies.

Prefer small independent modules.

Never optimize prematurely.

Never build infrastructure that the MVP does not use.

Every new abstraction must solve an existing problem.

---

# Communication Model

Runtime

User

↓

UI

↓

Orchestrator

↓

EventBus

↓

Agents

↓

Provider

↓

Result

↓

UI

↓

Background Persistence

Documentation

↓

.teamcode/

tasks/

reviews/

progress.md

Runtime communication should never depend on disk I/O.

Documentation is generated asynchronously.

---

# MVP Scope

Version 1 should only solve the following problems:

✓ Terminal UI

✓ Slash commands

✓ Multi-provider configuration

✓ Custom agent roles

✓ LiteLLM integration

✓ Shared conversation context

✓ Event-driven orchestration

✓ Developer adapter

✓ Automatic project documentation

Everything else belongs in a future version.

---

# What TeamCode Is NOT

TeamCode is NOT another chatbot.

TeamCode is NOT another code editor.

TeamCode is NOT another wrapper around an LLM.

TeamCode is an orchestration layer that allows multiple AI models and coding agents to work together as one software engineering team.

---

# Decision Framework

Before implementing any feature, ask:

Does this make the engineering team better?

Does this simplify the user experience?

Can this be implemented later?

Does this belong in the MVP?

If the answer is "no", do not build it yet.

---

# Instructions For AI Contributors

Before making changes:

1. Read this document completely.
2. Read the current repository structure.
3. Read existing architecture before introducing new abstractions.
4. Do not redesign the product without updating this vision.
5. Protect the MVP.
6. Prefer shipping working software over building perfect architecture.
7. If implementation conflicts with this document, explain why before changing the architecture.

Your job is not only to write code.

Your job is to help build TeamCode according to this vision.

## Current Priority

The current objective is to build a usable MVP.

Every completed feature should immediately make TeamCode more usable.

Avoid adding features that only prepare for future functionality.

Ship first.

Iterate second.

Perfect later.