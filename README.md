# AI Agent Systems

This repository documents my experiments while learning and building **AI agent systems** using multiple modern agent frameworks.

The goal of this repository is to explore how agentic systems are designed, how LLMs interact with tools, and how different frameworks support building intelligent agents.

---

## Demo

Work in Progress

This repository is currently under active development.  
Agent demos and example interactions will be added as each framework section is implemented.

---

## Agent Architecture (Concept)

Typical agent workflow explored in this repository:

User Input  
↓  
LLM Agent  
↓  
Tool Selection  
↓  
Tool Execution (API / functions)  
↓  
Memory Update  
↓  
Final Response  

Different frameworks implement this loop in different ways.

---

## Repository Structure


ai-agent-systems/

01-agent-basics/ → fundamental agent concepts
02-openai-agents/ → OpenAI Agents SDK experiments
03-google-adk/ → Google Agent Development Kit experiments
04-langgraph/ → LangGraph agent workflows
05-final-agent-project/ → complete agent system


---

## Learning Path

This repository follows a structured exploration of modern agent frameworks.

### 1. Agent Basics
- understanding the **agentic loop**
- tool usage
- memory and reasoning

### 2. OpenAI Agents SDK
- building agents with OpenAI tools
- tool calling
- orchestration

### 3. Google ADK
- experiments with Google's agent development framework

### 4. LangGraph
- graph-based agent workflows
- state management
- multi-tool coordination

### 5. Final Agent Project
- complete agent system implementation
- tool usage
- multi-turn memory
- real API interaction

---

## Current Progress

- [x] Agent Basics (started)
- [ ] OpenAI Agents SDK
- [ ] Google ADK
- [ ] LangGraph
- [ ] Final Agent Project

---

## Technologies

- Python
- OpenAI API
- LangGraph
- Google ADK
- LLM-based agents

---

## Setup

Clone the repository:


git clone https://github.com/yourusername/ai-agent-systems


Create a virtual environment:


python -m venv venv
source venv/bin/activate


Install dependencies (if required):


pip install -r requirements.txt


Set your API key:


OPENAI_API_KEY=your_key


---

## Notes

This repository is an **ongoing learning and experimentation project** exploring modern AI agent architectures and frameworks.