# Development Principles

## 1. Single Responsibility Principle (SRP)
Every component, function, and file should have one clear purpose. 

## 2. <200 LOC per File
Files should be kept small to respect limited context windows and cognitive load. Refactor files approaching 200 lines by extracting logic.

## 3. MCP-First
Tools and interfaces accessed by agents should adhere strictly to the Model Context Protocol (MCP).

## 4. Agnosticism
Isolate external dependencies (LLMs, databases) behind adapter interfaces.
