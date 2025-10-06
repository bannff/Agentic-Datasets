# Migration Plan: Agentic Multi-Turn Datasets Pipeline

**Project:** agentic-datasets v0.1.0  
**Status:** Infrastructure Complete ✓ | Transformations Pending ⚠️  
**Last Updated:** 2025-01-22  
**Next Milestone:** Implement S2M, APIGenMT, ReviewInstruct with Strands SDK

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Current State Assessment](#current-state-assessment)
3. [Research Findings](#research-findings)
4. [Implementation Roadmap](#implementation-roadmap)
5. [Technical Architecture](#technical-architecture)
6. [Next Steps](#next-steps)
7. [Acceptance Criteria](#acceptance-criteria)

---

## Executive Summary

### Vision
Transform single-turn cybersecurity Q&A datasets into high-quality, multi-turn agentic conversations with tool-calling capabilities through an automated, verifiable pipeline.

### Current Reality
- **Infrastructure:** ✅ Complete (CLI, pipeline, chunking, schema, HF publishing, CI/CD, Docker)
- **Transformations:** ⚠️ Stubs only (S2M, APIGenMT, ReviewInstruct set metadata flags but perform no actual transformations)
- **CI/CD:** ✅ Fixed (Black 24.10.0 formatting, 10 workflows operational)
- **Libraries:** ✅ Mature (langchain-text-splitters + tiktoken for chunking, NOT bespoke)
- **Orchestration:** 🟡 Strands SDK available (docs retrieved), not yet integrated

### Key Insight
The pipeline **infrastructure works perfectly**. What's missing is **LLM-powered transformation logic** in the three core stages. With Strands SDK now confirmed available, we can implement actual multi-turn generation, tool injection, and review-driven refinement.

---

## Current State Assessment

### ✅ What Works (Proven in CI/CD)

#### Package & CLI Infrastructure
- **Package:** agentic-datasets v0.1.0, Python ≥3.9, Pydantic 2.4+
- **CLI:** 7 commands operational
  ```bash
  agentic-ds run              # Execute pipelines
  agentic-ds chunk            # Token-aware splitting
  agentic-ds run-config       # YAML-driven execution
  agentic-ds transforms       # List registered stages
  agentic-ds catalog:list     # View dataset catalog
  agentic-ds catalog:show     # Dataset details
  agentic-ds hf:push          # Publish to Hugging Face
  ```

#### Schema & Validation
- **ConversationRecord:** Pydantic v2 models with strict validation
- **Message:** role (system/user/assistant/tool), content, name, tool_calls
- **ToolCall:** id, type, function (name + arguments as JSON)
- **Metadata:** Source tracking, agentic flags, review status

#### Transforms (Production-Ready)
- **Token-Aware Chunking:** Uses `langchain-text-splitters.TokenTextSplitter`
  - Encoding: cl100k_base (OpenAI standard)
  - Splitting: Configurable chunk_size, chunk_overlap
  - Quality: **MATURE LIBRARY** ✓ (not bespoke)
  - Testing: tiktoken 0.11.0 for accurate token counting

#### Publishing & Catalog
- **HF Hub Integration:** Dataset card generation, git LFS support
- **Catalog System:** YAML-based dataset registry with metadata
- **CLI Publishing:** `agentic-ds hf:push` with validation
- **Workflow:** Manual-dispatch GitHub Action (`publish_hf.yml`) with secrets

#### CI/CD (10 Workflows)
1. **ci.yml:** Lint (ruff), format (Black 24.10.0), type check (mypy), tests (pytest)
2. **docker.yml:** Build multi-platform images
3. **smoke.yml:** Docker smoke tests
4. **devcontainer.yml:** Dev container validation
5. **run_pipeline.yml:** Manual pipeline execution
6. **nightly.yml:** Scheduled full test suite
7. **publish_hf.yml:** Manual HF publishing
8. **publish_hf_on_tag.yml:** Auto-publish on version tags
9. **release.yml:** PyPI publishing on releases
10. **e2e_test.yml:** End-to-end pipeline validation

**Status:** Black formatting fixed (commit c2706c6), workflow #7 validating

#### Containerization
- **Dockerfile:** Multi-stage builds, pinned dependencies
- **GHCR:** Auto-publish to ghcr.io/<org>/<name>
- **Devcontainer:** VS Code development environment

### ⚠️ What's Stubbed (Needs Implementation)

#### Stage 1: S2M (Single → Multi-Turn)
**Current Behavior:**
```python
# Just adds a placeholder message
record.messages.append(
    Message(role="assistant", content="[Multi-turn conversation would go here]")
)
```

**What It Should Do:**
- Use Strands Agent with multi-turn conversation prompts
- Generate coherent follow-up questions/answers from single Q&A
- Maintain context and expand domain knowledge naturally
- Preserve conversation state across turns

**Dependencies:** strands-agents, model provider (Bedrock/Anthropic/OpenAI)

#### Stage 2: APIGenMT (Tool Call Injection)
**Current Behavior:**
```python
# Just sets a flag
record.metadata.agentic = True
```

**What It Should Do:**
- Parse tool catalog into Strands `@tool` decorated functions
- Register tools with agent for LLM accessibility
- Let agent naturally inject tool calls via LLM reasoning
- Apply APIGen 3-stage verification:
  1. **Format Checker:** Validate JSON parsing, correct arguments
  2. **Execution Checker:** Simulate/test function calls
  3. **Semantic Checker:** Verify results align with query intent

**Methodology:** [APIGen](https://apigen-pipeline.github.io/) - 3,673 executable APIs, 60k verified entries
**Reference Dataset:** [Salesforce/xlam-function-calling-60k](https://huggingface.co/datasets/Salesforce/xlam-function-calling-60k)

#### Stage 3: ReviewInstruct (Quality Refinement)
**Current Behavior:**
```python
# Just sets a flag
record.metadata.reviewed = True
```

**What It Should Do:**
- Implement "Ask-Respond-Review" multi-agent pattern
- **Candidate Agent:** Generates initial conversation
- **Reviewer Agents:** Provide diverse feedback (quality, safety, diversity)
- **Chairman Agent:** Synthesizes feedback, decides on refinement
- Iterate until quality thresholds met
- Ensure conversational naturalness, safety, contextual coherence

**Methodology:** [ReviewInstruct](https://arxiv.org/abs/2505.11010) (ACL 2025)
- Multi-agent framework with 3 roles
- Iterative refinement with feedback loops
- Achieves +2.9% on MMLU-Pro, +2% on MT-Bench vs baselines

#### Orchestrator: Strands SDK Integration
**Current State:** Scaffolded but not implemented
```python
# Empty orchestrator class in strands.py
```

**What It Should Do:**
- Register transformation stages as Strands agents
- Use Graph pattern for pipeline DAG (S2M → APIGenMT → ReviewInstruct)
- Enable observability (metrics, traces, logs via OpenTelemetry)
- Handle state management across stages
- Support multi-agent patterns (Graph, Workflow)

### 🚫 What's Outdated (Remove from Plan)

- ~~"Strands SDK not available (404)"~~ → **FALSE:** SDK docs retrieved successfully
- ~~"Need alternative orchestration"~~ → **FALSE:** Strands SDK provides everything needed
- ~~"Bespoke chunking code"~~ → **FALSE:** Uses langchain-text-splitters (mature) ✓

---

## Research Findings

### Strands SDK (Agent Framework)

**Status:** ✅ Available and comprehensive

**Installation:**
```bash
pip install strands-agents strands-agents-tools strands-agents-builder
```

**Core Capabilities:**

1. **Agent Loop (Recursive Execution)**
   ```
   Input → LLM Reasoning → Tool Selection → Tool Execution → Response
                ↑_______________|
   ```
   - Agentic reasoning with tool use
   - State management across turns
   - Conversation context preservation

2. **Model Providers** (Flexible LLM Backend)
   - **Bedrock (AWS):** Claude 4 (default), Titan, Cohere
   - **Anthropic:** Direct Claude 3/4 API
   - **OpenAI:** GPT-4, GPT-3.5
   - **Open Source:** Ollama, LiteLLM
   - **Others:** Mistral, Writer, Cohere direct
   - **Custom:** Implement provider interface

3. **Tool System**
   ```python
   from strands.tools import tool
   
   @tool
   def search_vulnerabilities(cve_id: str) -> dict:
       """Search CVE database for vulnerability details."""
       # Tool logic here
       return {"cve": cve_id, "severity": "high"}
   ```
   - Automatic LLM schema generation
   - Type-safe argument validation
   - MCP protocol support
   - Tool composition and chaining

4. **Multi-Agent Patterns**
   - **Graph:** Complex workflows with conditional routing
   - **Workflow:** Sequential pipeline with handoffs
   - **Agents as Tools:** Hierarchical composition (agent calls other agents)

5. **Observability**
   - Metrics: latency, token usage, success rates
   - Traces: Full execution path with timing
   - Logs: Structured logging with context
   - Export: OpenTelemetry compatible

**Documentation Sources:**
- Quickstart: Installation, basic agent setup
- Agent Loop: Detailed execution model
- Tools: @tool decorator, MCP integration
- Multi-Agent: Graph/Workflow patterns
- Providers: Model configuration

### APIGen Methodology (Tool-Calling Dataset Generation)

**Paper:** [APIGen: Automated Pipeline for Generating Verifiable and Diverse Function-Calling Datasets](https://arxiv.org/abs/2406.18518)

**Key Innovations:**

1. **Executable API Collection**
   - 3,673 verified APIs across 21 categories
   - Sources: ToolBench (REST APIs from RapidAPI), Python functions
   - Quality filters: documentation parsing, accessibility testing, parameter validation

2. **Three-Stage Verification** (Quality Assurance)
   
   **Stage 1: Format Checker**
   - Validate JSON structure (query, answer fields)
   - Parse function calls for correct syntax
   - Verify arguments exist in API definitions
   - Reject hallucinated functions/parameters
   
   **Stage 2: Execution Checker**
   - Execute function calls against backends
   - Capture execution results or errors
   - Filter out non-executable calls
   - Provide fine-grained error messages
   
   **Stage 3: Semantic Checker**
   - Use LLM to assess result alignment with query intent
   - Verify multi-request queries get complete answers
   - Ensure execution results match user needs
   - Add verified data back to seed for diversity

3. **Diversity Strategies**
   - **Query Style Diversity:** simple, multiple, parallel, parallel-multiple
   - **API Sampling:** Random selection from 3,673 executable APIs
   - **Example Sampling:** Varied seed data combinations
   - **Prompt Sampling:** Multiple template variations
   - **Temperature:** 0.7 for generation diversity

4. **Dataset Release**
   - **60,000 verified entries** on Hugging Face
   - **95%+ human-evaluated correctness**
   - **State-of-the-art performance:** xLAM-7b (#3 on Berkeley Function-Calling Leaderboard)
   - **Tiny model success:** xLAM-1b outperforms GPT-3.5-Turbo

**Implementation Approach for APIGenMT Stage:**
1. Parse `catalog.yaml` tool definitions into Strands `@tool` functions
2. Sample tools based on conversation context
3. Generate function-calling conversations with LLM + Strands agent
4. Apply three-stage verification:
   - Format check with JSON parsing
   - Execution check with simulated/real API calls
   - Semantic check with reviewer LLM
5. Add verified conversations to output dataset

### ReviewInstruct Methodology (Conversation Refinement)

**Paper:** [ReviewInstruct: A Review-Driven Multi-Turn Conversations Generation Method for Large Language Models](https://arxiv.org/abs/2505.11010) (ACL 2025)

**Key Innovations:**

1. **Multi-Agent "Ask-Respond-Review" Framework**
   
   **Candidate Agent:**
   - Generates initial conversation turns
   - Responds to user queries
   - Attempts to follow instructions and maintain coherence
   
   **Reviewer Agents (Multiple, Diverse Perspectives):**
   - Quality Reviewer: Assesses clarity, completeness, accuracy
   - Safety Reviewer: Checks for harmful/biased content
   - Diversity Reviewer: Evaluates instruction variety and difficulty
   - Coherence Reviewer: Verifies multi-turn context maintenance
   
   **Chairman Agent:**
   - Synthesizes feedback from all reviewers
   - Decides whether to accept or request refinement
   - Provides consolidated improvement guidance
   - Iterates until quality thresholds met

2. **Iterative Refinement Loop**
   ```
   Candidate → Generate Conversation
        ↓
   Reviewers → Provide Feedback (parallel)
        ↓
   Chairman → Synthesize & Decide (accept/refine)
        ↓
   [If refine] → Candidate receives feedback → Loop
   [If accept] → Add to final dataset
   ```

3. **Performance Gains**
   - **+2.9% absolute** on MMLU-Pro (LLaMA2-13B baseline)
   - **+2% absolute** on MT-Bench (multi-turn benchmark)
   - Outperforms prior SOTA on LLaMA2-13B base
   - Ablation studies confirm critical role of Review stage and multiple reviewers

4. **Dataset Construction**
   - Applied to Alpaca dataset (single-turn seed)
   - Generated multi-turn conversations via review-driven iteration
   - Increased instruction diversity and difficulty
   - Fine-tuned LLaMA2-13B with improved conversational coherence

**Implementation Approach for ReviewInstruct Stage:**
1. Create Candidate agent (generates/refines conversations)
2. Create multiple Reviewer agents with specialized prompts:
   - Quality: "Assess clarity, accuracy, completeness"
   - Safety: "Check for harmful content, bias, PII"
   - Diversity: "Evaluate instruction variety and difficulty"
   - Coherence: "Verify context maintenance across turns"
3. Create Chairman agent with synthesis prompt
4. Implement iterative loop with configurable thresholds
5. Use Strands Graph pattern for multi-agent coordination
6. Track refinement metrics (iterations, feedback types, acceptance rate)

---

## Implementation Roadmap

### Phase 0: ✅ Foundation (COMPLETE)
- [x] Package structure (src/agentic_datasets/)
- [x] CLI with Typer (7 commands operational)
- [x] Pydantic schemas (ConversationRecord, Message, ToolCall)
- [x] CI/CD (10 workflows, Black 24.10.0 fixed)
- [x] Docker + devcontainer
- [x] Token-aware chunking (langchain + tiktoken)
- [x] HF Hub publishing
- [x] Catalog system (catalog.yaml)
- [x] Documentation (README, README_AGENTIC)

### Phase 1: 🟡 Strands SDK Integration (IN PROGRESS)

**Goal:** Add Strands SDK dependencies and set up model provider authentication

**Tasks:**
1. Update `pyproject.toml` dependencies
   ```toml
   [project.dependencies]
   strands-agents = ">=1.0.0"
   strands-agents-tools = ">=0.2.0"
   strands-agents-builder = ">=0.1.0"
   
   # Model provider (choose one or support multiple)
   boto3 = ">=1.26.0"  # For AWS Bedrock (Claude 4)
   anthropic = ">=0.28.0"  # For direct Anthropic API
   openai = ">=1.0.0"  # For OpenAI API
   ```

2. Configure model provider authentication
   - **Bedrock (AWS):** Configure AWS credentials, enable Claude 4 in Bedrock console
   - **Anthropic:** Set `ANTHROPIC_API_KEY` environment variable
   - **OpenAI:** Set `OPENAI_API_KEY` environment variable
   - Add configuration to `config.yaml` schema

3. Create base agent utilities
   - `src/agentic_datasets/agents/base.py`: Agent factory, provider setup
   - `src/agentic_datasets/agents/prompts.py`: Prompt templates for each stage
   - `src/agentic_datasets/agents/tools.py`: Tool decorator wrappers

4. Test basic agent creation and LLM calls
   - Write unit test with simple agent conversation
   - Verify model provider authentication works
   - Test tool registration and execution

**Acceptance Criteria:**
- Strands SDK installed and importable
- Model provider authenticated and working
- Basic agent can respond to prompts
- Tool registration and execution verified

**Estimated Effort:** 2-3 days

### Phase 2: 🔴 S2M Implementation (NEXT)

**Goal:** Transform single-turn Q&A into coherent multi-turn conversations

**Approach:**
1. Create S2M agent with specialized prompt:
   ```
   You are an expert conversation generator. Given a single-turn question-answer pair,
   generate a natural multi-turn conversation that:
   - Starts with the original question
   - Includes follow-up questions that dig deeper
   - Maintains context across turns
   - Expands on domain knowledge naturally
   - Ends with a comprehensive understanding of the topic
   
   Single-turn input: {question} -> {answer}
   Generate 3-5 turns of conversation.
   ```

2. Implement conversation state management
   - Track conversation history
   - Maintain domain context
   - Ensure coherent turn transitions

3. Add quality controls
   - Minimum/maximum turn counts
   - Context relevance checks
   - Domain consistency validation

4. Update `src/agentic_datasets/stages/s2m.py`
   ```python
   from strands.agents import Agent
   from strands.providers import get_provider
   
   async def process_s2m(record: ConversationRecord, config: S2MConfig) -> ConversationRecord:
       """Convert single-turn to multi-turn using Strands agent."""
       # Create agent with multi-turn generation prompt
       provider = get_provider(config.model_provider)
       agent = Agent(provider=provider, system_prompt=S2M_SYSTEM_PROMPT)
       
       # Extract single-turn Q&A
       question = record.messages[0].content
       answer = record.messages[1].content
       
       # Generate multi-turn conversation
       result = await agent.run(
           f"Original Q&A:\nQ: {question}\nA: {answer}\n\nGenerate multi-turn:"
       )
       
       # Parse result into messages
       new_messages = parse_conversation_turns(result.content)
       
       # Return updated record
       return ConversationRecord(
           messages=new_messages,
           metadata={**record.metadata, "stage": "s2m", "original_turns": len(record.messages)}
       )
   ```

5. Add tests with cybersecurity Q&A fixtures

**Acceptance Criteria:**
- Single-turn cybersec Q&A → coherent 3-5 turn conversation
- Context maintained across turns
- Natural follow-up questions
- Domain knowledge expanded appropriately
- Tests pass with >90% coherence (human eval on sample)

**Estimated Effort:** 5-7 days

### Phase 3: 🔴 APIGenMT Implementation

**Goal:** Inject tool calls into conversations using APIGen methodology

**Approach:**
1. Implement tool catalog parser
   ```python
   def parse_catalog_tools(catalog_path: str) -> List[Tool]:
       """Parse catalog.yaml and create Strands @tool functions."""
       catalog = yaml.safe_load(open(catalog_path))
       tools = []
       
       for tool_def in catalog.get("tools", []):
           @tool(name=tool_def["name"], description=tool_def["description"])
           def tool_func(**kwargs):
               # Tool implementation or mock
               pass
           tools.append(tool_func)
       
       return tools
   ```

2. Create APIGen agent with tool access
   ```python
   agent = Agent(
       provider=provider,
       system_prompt=APIGEN_SYSTEM_PROMPT,
       tools=catalog_tools
   )
   ```

3. Implement three-stage verification pipeline
   
   **Stage 1: Format Checker**
   ```python
   def verify_format(tool_call: ToolCall, tool_schemas: dict) -> bool:
       """Verify JSON parsing and argument validity."""
       # Check JSON structure
       # Verify function exists in catalog
       # Validate arguments match schema
       # Reject hallucinated parameters
   ```
   
   **Stage 2: Execution Checker**
   ```python
   async def verify_execution(tool_call: ToolCall, executor: ToolExecutor) -> tuple[bool, Any]:
       """Execute tool call and capture results."""
       try:
           result = await executor.execute(tool_call)
           return True, result
       except Exception as e:
           return False, str(e)
   ```
   
   **Stage 3: Semantic Checker**
   ```python
   async def verify_semantics(
       query: str, tool_call: ToolCall, result: Any, reviewer: Agent
   ) -> bool:
       """Use LLM to verify result aligns with query intent."""
       prompt = f"""
       Query: {query}
       Tool Call: {tool_call}
       Result: {result}
       
       Does this result appropriately address the query? Yes/No and explain.
       """
       response = await reviewer.run(prompt)
       return parse_yes_no(response.content)
   ```

4. Update `src/agentic_datasets/stages/apigenmt.py` with full verification

5. Add tests with mock tool catalog and execution

**Acceptance Criteria:**
- Multi-turn conversations → natural tool call injection
- Three-stage verification catches invalid calls
- Semantic alignment verified by reviewer LLM
- >90% execution success rate on verified tools
- Tests with mock cybersecurity tools pass

**Estimated Effort:** 7-10 days

### Phase 4: 🔴 ReviewInstruct Implementation

**Goal:** Multi-agent review and refinement for quality assurance

**Approach:**
1. Create agent roles with Strands
   
   **Candidate Agent:**
   ```python
   candidate = Agent(
       provider=provider,
       system_prompt="Generate and refine conversations based on feedback."
   )
   ```
   
   **Reviewer Agents:**
   ```python
   quality_reviewer = Agent(provider=provider, system_prompt=QUALITY_REVIEW_PROMPT)
   safety_reviewer = Agent(provider=provider, system_prompt=SAFETY_REVIEW_PROMPT)
   diversity_reviewer = Agent(provider=provider, system_prompt=DIVERSITY_REVIEW_PROMPT)
   coherence_reviewer = Agent(provider=provider, system_prompt=COHERENCE_REVIEW_PROMPT)
   ```
   
   **Chairman Agent:**
   ```python
   chairman = Agent(provider=provider, system_prompt=CHAIRMAN_SYNTHESIS_PROMPT)
   ```

2. Implement review graph with Strands Graph pattern
   ```python
   from strands.multi_agent import Graph
   
   review_graph = Graph()
   review_graph.add_node("candidate", candidate)
   review_graph.add_node("quality_review", quality_reviewer)
   review_graph.add_node("safety_review", safety_reviewer)
   review_graph.add_node("diversity_review", diversity_reviewer)
   review_graph.add_node("coherence_review", coherence_reviewer)
   review_graph.add_node("chairman", chairman)
   
   # Define edges (parallel reviews → chairman synthesis)
   review_graph.add_edge("candidate", "quality_review")
   review_graph.add_edge("candidate", "safety_review")
   review_graph.add_edge("candidate", "diversity_review")
   review_graph.add_edge("candidate", "coherence_review")
   review_graph.add_edge("quality_review", "chairman")
   review_graph.add_edge("safety_review", "chairman")
   review_graph.add_edge("diversity_review", "chairman")
   review_graph.add_edge("coherence_review", "chairman")
   
   # Conditional edge: accept or refine
   review_graph.add_conditional_edge(
       "chairman",
       route_decision,  # Function returns "accept" or "refine"
       {"accept": "end", "refine": "candidate"}
   )
   ```

3. Implement iterative refinement loop
   ```python
   async def review_and_refine(
       record: ConversationRecord, 
       config: ReviewInstructConfig
   ) -> ConversationRecord:
       """Iteratively refine conversation through multi-agent review."""
       max_iterations = config.max_iterations
       
       for iteration in range(max_iterations):
           # Run review graph
           result = await review_graph.run({"conversation": record})
           
           if result["decision"] == "accept":
               record.metadata.review_iterations = iteration + 1
               record.metadata.reviewed = True
               return result["conversation"]
           
           # Refine with feedback
           record = result["refined_conversation"]
       
       # Max iterations reached, accept with flag
       record.metadata.review_iterations = max_iterations
       record.metadata.max_iterations_reached = True
       return record
   ```

4. Add observability metrics
   - Track iteration counts
   - Log reviewer feedback
   - Measure refinement success rates
   - Export metrics via OpenTelemetry

5. Update `src/agentic_datasets/stages/reviewinstruct.py`

**Acceptance Criteria:**
- Multi-agent review provides diverse feedback
- Chairman synthesizes and makes accept/refine decisions
- Iterative refinement improves quality (human eval on sample)
- Achieves target quality thresholds (>85% reviewer consensus)
- Observability metrics captured and exportable
- Tests with mock reviewers pass

**Estimated Effort:** 10-14 days

### Phase 5: 🔴 Strands Orchestrator Implementation

**Goal:** Production-ready orchestration with observability

**Approach:**
1. Implement `src/agentic_datasets/orchestrators/strands.py`
   ```python
   from strands.multi_agent import Workflow
   from strands.observability import configure_observability
   
   class StrandsOrchestrator:
       def __init__(self, config: OrchestratorConfig):
           self.config = config
           configure_observability(
               export_traces=config.export_traces,
               export_metrics=config.export_metrics
           )
       
       async def run_pipeline(
           self, 
           records: List[ConversationRecord]
       ) -> List[ConversationRecord]:
           """Orchestrate full pipeline with Strands Workflow."""
           # Create sequential workflow
           workflow = Workflow()
           workflow.add_stage("normalize", normalize_stage)
           workflow.add_stage("chunk", chunk_stage)
           workflow.add_stage("s2m", s2m_stage)
           workflow.add_stage("apigenmt", apigenmt_stage)
           workflow.add_stage("reviewinstruct", reviewinstruct_stage)
           workflow.add_stage("validate", validate_stage)
           
           # Execute workflow
           results = []
           for record in records:
               result = await workflow.run({"record": record})
               results.append(result["record"])
           
           return results
   ```

2. Add state management across stages
   - Persist intermediate results
   - Enable stage restart on failure
   - Track pipeline progress

3. Implement observability
   - Capture stage latencies
   - Track token usage per stage
   - Log errors with context
   - Export to OpenTelemetry collector

4. Add configuration options
   ```yaml
   # config.yaml
   orchestrator:
     type: strands
     observability:
       export_traces: true
       export_metrics: true
       otlp_endpoint: "http://localhost:4317"
     state:
       persist_intermediate: true
       checkpoint_dir: "./checkpoints"
   ```

**Acceptance Criteria:**
- Full pipeline executes via Strands Workflow
- State persisted at each stage boundary
- Observability metrics exported (traces, metrics, logs)
- Pipeline restarts from checkpoint on failure
- Configuration flexible and well-documented

**Estimated Effort:** 5-7 days

### Phase 6: 🔴 End-to-End Testing & Dataset Production

**Goal:** Validate full pipeline with real cybersecurity data

**Setup:**
1. Configure GitHub LFS for test datasets
   ```bash
   git lfs install
   git lfs track "*.jsonl"
   git lfs track "tests/fixtures/*.json"
   ```

2. Create private output directory (not HF yet)
   ```
   outputs/
     private/
       single_turn_cybersec_raw.jsonl        # Input
       multi_turn_cybersec_processed.jsonl   # After S2M
       agentic_cybersec_tools.jsonl          # After APIGenMT
       refined_cybersec_final.jsonl          # After ReviewInstruct
   ```

3. Add to `.gitignore`:
   ```
   outputs/private/
   ```

**Testing Approach:**
1. Use `primus_seed` dataset or curated cybersecurity Q&A
   - Filter for quality (remove "mostly sucks" entries via manual curation)
   - Create 100-entry test set with diverse topics

2. Run full pipeline with observability enabled
   ```bash
   agentic-ds run-config --config configs/cybersec_full_pipeline.yaml \
     --input tests/fixtures/cybersec_seed_100.jsonl \
     --output outputs/private/refined_cybersec_final.jsonl \
     --enable-observability
   ```

3. Manual quality inspection
   - Random sample 20 conversations
   - Human evaluation rubric:
     * Multi-turn coherence: 1-5 scale
     * Tool call relevance: Yes/No per call
     * Safety/quality: Pass/Fail
     * Overall: Accept/Reject
   - Target: >80% acceptance rate

4. Automated quality checks
   - Schema validation (all records valid)
   - Tool call format verification
   - Token counts within limits
   - Metadata completeness

5. Performance benchmarking
   - Measure latency per stage
   - Track token usage and costs
   - Identify bottlenecks
   - Optimize as needed

**Acceptance Criteria:**
- 100-entry test set → 100 refined conversations
- >80% human acceptance rate
- <5% schema validation failures
- Pipeline completes in <2 hours (with reasonable LLM provider)
- Observability data captures full execution
- Output dataset privately inspectable, not yet published

**Estimated Effort:** 7-10 days (includes iteration on quality)

---

## Technical Architecture

### Pipeline Stages (Execution Order)

```
Input (Single-Turn JSONL)
         ↓
    [Normalize]        # Clean, standardize schema
         ↓
     [Validate]        # Pydantic validation
         ↓
      [Chunk]          # Token-aware splitting (langchain + tiktoken)
         ↓
       [S2M]           # Single → Multi-turn (Strands agent)
         ↓
    [APIGenMT]         # Tool call injection (APIGen 3-stage verification)
         ↓
 [ReviewInstruct]      # Multi-agent refinement (Ask-Respond-Review)
         ↓
     [Validate]        # Final schema + quality check
         ↓
      [Export]         # JSONL or HF Hub publishing
         ↓
Output (Agentic Multi-Turn Dataset)
```

### Data Flow Schema

**Input (Single-Turn):**
```json
{
  "messages": [
    {"role": "user", "content": "What is SQL injection?"},
    {"role": "assistant", "content": "SQL injection is..."}
  ],
  "metadata": {"source": "cybersec_qa", "domain": "web_security"}
}
```

**After S2M (Multi-Turn):**
```json
{
  "messages": [
    {"role": "user", "content": "What is SQL injection?"},
    {"role": "assistant", "content": "SQL injection is... Would you like an example?"},
    {"role": "user", "content": "Yes, show me an example."},
    {"role": "assistant", "content": "Here's a vulnerable query: SELECT * FROM users WHERE..."},
    {"role": "user", "content": "How do I prevent it?"},
    {"role": "assistant", "content": "Use parameterized queries..."}
  ],
  "metadata": {
    "source": "cybersec_qa",
    "domain": "web_security",
    "stage": "s2m",
    "original_turns": 2,
    "generated_turns": 6
  }
}
```

**After APIGenMT (Tool Calls):**
```json
{
  "messages": [
    {"role": "user", "content": "What is SQL injection?"},
    {"role": "assistant", "content": "SQL injection is...", "tool_calls": [
      {
        "id": "call_1",
        "type": "function",
        "function": {"name": "search_cve", "arguments": "{\"keyword\": \"sql injection\"}"}
      }
    ]},
    {"role": "tool", "name": "search_cve", "content": "{\"cves\": [\"CVE-2023-1234\", ...]}"},
    {"role": "assistant", "content": "I found recent CVEs related to SQL injection..."}
  ],
  "metadata": {
    "source": "cybersec_qa",
    "domain": "web_security",
    "stage": "apigenmt",
    "agentic": true,
    "tool_calls_count": 1,
    "tools_used": ["search_cve"],
    "verification": {
      "format_check": "pass",
      "execution_check": "pass",
      "semantic_check": "pass"
    }
  }
}
```

**After ReviewInstruct (Refined):**
```json
{
  "messages": [...],  // Potentially modified for clarity/safety
  "metadata": {
    "source": "cybersec_qa",
    "domain": "web_security",
    "stage": "reviewinstruct",
    "reviewed": true,
    "review_iterations": 2,
    "reviewer_feedback": {
      "quality": "pass",
      "safety": "pass",
      "diversity": "pass",
      "coherence": "pass"
    },
    "chairman_decision": "accept"
  }
}
```

### Technology Stack

**Core Dependencies:**
- **Python:** ≥3.9
- **Pydantic:** ≥2.4 (schema validation)
- **Typer:** ≥0.9 (CLI framework)
- **PyYAML:** ≥6.0 (configuration)

**Strands SDK:**
- **strands-agents:** ≥1.0.0 (agent framework)
- **strands-agents-tools:** ≥0.2.0 (tool system + MCP)
- **strands-agents-builder:** ≥0.1.0 (agent builders)

**Model Providers (Choose One or Multiple):**
- **boto3:** ≥1.26 (AWS Bedrock - Claude 4 default)
- **anthropic:** ≥0.28 (Direct Anthropic API)
- **openai:** ≥1.0 (OpenAI GPT-4)

**Text Processing:**
- **langchain-text-splitters:** ≥0.3.0 (token-aware chunking)
- **tiktoken:** ≥0.11.0 (token counting)

**Dataset Publishing:**
- **datasets:** ≥2.14 (HF Hub integration)
- **huggingface-hub:** ≥0.16 (git LFS support)

**Development:**
- **ruff:** ≥0.1 (linting)
- **black:** >=24.4,<25 (formatting - pinned to avoid 25.x)
- **mypy:** ≥1.5 (type checking)
- **pytest:** ≥7.4 (testing)
- **pytest-asyncio:** ≥0.21 (async tests)

### Directory Structure

```
agentic-datasets/
├── src/agentic_datasets/
│   ├── cli.py                    # Typer CLI with 7 commands
│   ├── pipeline.py               # Pipeline orchestration
│   ├── config.py                 # YAML configuration loader
│   ├── schemas/
│   │   ├── messages.py           # ConversationRecord, Message, ToolCall
│   │   └── config_schemas.py    # Configuration Pydantic models
│   ├── stages/
│   │   ├── normalize.py          # Input normalization
│   │   ├── validate.py           # Schema validation
│   │   ├── s2m.py                # ⚠️ Single → Multi-turn (STUB → IMPLEMENT)
│   │   ├── apigenmt.py           # ⚠️ Tool injection (STUB → IMPLEMENT)
│   │   └── reviewinstruct.py    # ⚠️ Refinement (STUB → IMPLEMENT)
│   ├── transforms/
│   │   └── chunking.py           # ✅ Token-aware chunking (langchain + tiktoken)
│   ├── agents/                   # 🆕 ADD: Strands agent utilities
│   │   ├── base.py               # Agent factory, provider setup
│   │   ├── prompts.py            # Stage-specific prompts
│   │   └── tools.py              # Tool catalog parser, @tool wrappers
│   ├── orchestrators/
│   │   ├── in_process.py         # ✅ Registry-based execution (works)
│   │   └── strands.py            # ⚠️ Strands SDK orchestrator (IMPLEMENT)
│   ├── export/
│   │   ├── jsonl.py              # ✅ JSONL export
│   │   └── huggingface.py        # ✅ HF Hub publishing
│   └── utils/
│       ├── registry.py           # ✅ Transform registration
│       └── catalog.py            # ✅ Catalog management
├── tests/
│   ├── fixtures/
│   │   ├── cybersec_seed_100.jsonl   # 🆕 ADD: Test dataset with LFS
│   │   └── mock_tools.yaml           # 🆕 ADD: Mock tool catalog
│   ├── test_s2m.py                   # 🆕 ADD: S2M stage tests
│   ├── test_apigenmt.py              # 🆕 ADD: APIGenMT tests
│   ├── test_reviewinstruct.py        # 🆕 ADD: ReviewInstruct tests
│   └── test_end_to_end.py            # 🆕 ADD: Full pipeline test
├── configs/
│   ├── default.yaml                  # Basic config
│   ├── cybersec_full_pipeline.yaml   # 🆕 ADD: Full transformation config
│   └── bedrock_claude.yaml           # 🆕 ADD: AWS Bedrock config
├── outputs/
│   └── private/                      # 🆕 ADD: Private output (gitignored)
├── catalog.yaml                      # ✅ Dataset catalog with tools
├── pyproject.toml                    # ✅ Dependencies (needs Strands SDK added)
├── Dockerfile                        # ✅ Multi-stage build
├── .github/workflows/                # ✅ 10 workflows operational
├── README.md                         # ✅ User-facing docs
└── README_AGENTIC.md                 # ✅ Agentic quickstart
```

---

## Next Steps

### Immediate Actions (This Week)

1. **Update Dependencies** (Day 1)
   - Add strands-agents, strands-agents-tools to pyproject.toml
   - Choose model provider (Bedrock recommended for enterprise)
   - Run `pip install -e .[dev]` to verify installation

2. **Configure Model Provider** (Day 1-2)
   - Set up AWS credentials for Bedrock OR Anthropic/OpenAI API keys
   - Enable Claude 4 in Bedrock console (if using AWS)
   - Test authentication with basic agent creation
   - Document setup in README_AGENTIC.md

3. **Implement S2M Stage** (Day 3-7)
   - Create agent prompts for multi-turn generation
   - Implement conversation state management
   - Add quality controls (turn counts, coherence checks)
   - Write tests with cybersecurity Q&A fixtures
   - Validate with manual inspection of generated conversations

4. **Set Up GitHub LFS** (Parallel with S2M)
   - Configure LFS for `*.jsonl` in tests/fixtures/
   - Add 100-entry cybersecurity test dataset
   - Document LFS setup in README

5. **Create Private Output Directory** (Parallel)
   - Add `outputs/private/` to .gitignore
   - Document inspection workflow
   - Set up local quality review process

### Short-Term Milestones (Next 2-4 Weeks)

1. **APIGenMT Implementation** (Week 2)
   - Parse catalog.yaml to Strands @tool functions
   - Implement three-stage verification pipeline
   - Test with mock cybersecurity tools
   - Validate tool call quality with manual review

2. **ReviewInstruct Implementation** (Week 3-4)
   - Create multi-agent review system with Strands Graph
   - Implement iterative refinement loop
   - Add observability metrics
   - Test refinement quality improvements

3. **Strands Orchestrator** (Week 4)
   - Implement production-ready orchestration
   - Add state management and checkpointing
   - Enable observability export
   - Document configuration options

4. **End-to-End Testing** (Week 4)
   - Run full pipeline on 100-entry test set
   - Manual quality inspection with rubric
   - Performance benchmarking
   - Iterate on quality issues

### Medium-Term Goals (1-2 Months)

1. **Production Deployment**
   - Deploy to AWS with Bedrock integration
   - Set up observability infrastructure (OpenTelemetry collector)
   - Configure auto-scaling for batch processing
   - Monitor costs and optimize

2. **Dataset Production**
   - Process larger cybersecurity datasets (1k+ entries)
   - Human evaluation at scale (contract reviewers)
   - Iterate on quality based on feedback
   - Prepare for public release

3. **Community Release**
   - Publish refined datasets to Hugging Face Hub
   - Write dataset cards with methodology
   - Submit to Berkeley Function-Calling Benchmark
   - Blog post on methodology and results

4. **Advanced Features**
   - Multi-domain support (beyond cybersecurity)
   - Custom tool catalog builder UI
   - Quality prediction models (skip ReviewInstruct if high confidence)
   - Active learning loop (improve from production data)

---

## Acceptance Criteria

### Infrastructure (✅ COMPLETE)
- [x] CLI with 7 commands operational
- [x] Pydantic schema validation working
- [x] Token-aware chunking with langchain + tiktoken
- [x] HF Hub publishing with dataset cards
- [x] CI/CD with 10 workflows passing
- [x] Docker builds producing consistent outputs
- [x] Black formatting fixed (24.10.0)

### Transformation Stages (🔴 PENDING)
- [ ] S2M generates coherent 3-5 turn conversations from single Q&A
- [ ] APIGenMT injects tool calls with >90% execution success rate
- [ ] APIGenMT three-stage verification catches invalid calls
- [ ] ReviewInstruct achieves >85% reviewer consensus on quality
- [ ] ReviewInstruct produces <10% rejection rate after max iterations

### End-to-End Pipeline (🔴 PENDING)
- [ ] 100-entry test set → 100 refined agentic conversations
- [ ] >80% human acceptance rate on quality rubric
- [ ] <5% schema validation failures
- [ ] Pipeline completes in <2 hours (with Bedrock Claude 4)
- [ ] Observability data exported (traces, metrics, logs)

### Documentation (🟡 IN PROGRESS)
- [x] README.md with quickstart
- [x] README_AGENTIC.md with CLI usage
- [ ] Add Strands SDK setup guide
- [ ] Add model provider authentication docs
- [ ] Add end-to-end pipeline tutorial
- [ ] Add contribution guidelines for new stages

### Quality Benchmarks (🔴 FUTURE)
- [ ] Submit to Berkeley Function-Calling Leaderboard
- [ ] Achieve >80% on BFCL (if training models)
- [ ] Human eval on MT-Bench shows improvement over baselines
- [ ] Safety review shows <1% harmful content

---

## Development Preferences

All implementation must follow these principles:

1. **Single Responsibility:** Each stage does one thing well (S2M only does multi-turn, APIGenMT only does tools)
2. **Taxonomy:** Clear package structure (stages/, orchestrators/, agents/, transforms/)
3. **Pure Functions:** Stages return new ConversationRecords without side effects
4. **Mature Libraries:** Prefer established solutions (Strands SDK, langchain, HF datasets)
5. **Comments/Naming:** Docstrings, type hints, descriptive variable names
6. **Tests:** Unit tests for each stage, integration tests for pipeline
7. **Version Control:** Small commits, clear messages, deprecation warnings
8. **Modularity:** Registry-based stages, YAML-driven config, optional containerization
9. **Self-Contained:** One command to install, one command to run
10. **Containers:** Docker for reproducibility, optional per-stage images
11. **CI/CD:** Automated lint/test/build/publish workflows
12. **Mature Solutions:** Reuse proven libraries, don't reinvent wheels

---

## Risk Mitigation

### Technical Risks

**Risk:** LLM costs exceed budget during testing  
**Mitigation:** Use smaller models (Claude 3 Haiku) for initial testing, sample datasets, monitor costs with alerts

**Risk:** Three-stage verification rejects too many tool calls  
**Mitigation:** Iteratively tune verification prompts, collect rejection reasons, adjust thresholds

**Risk:** ReviewInstruct loops exceed max iterations frequently  
**Mitigation:** Tune reviewer prompts for realism, adjust quality thresholds, log iteration reasons

**Risk:** Strands SDK has breaking changes or bugs  
**Mitigation:** Pin versions, maintain fallback to in-process execution, contribute fixes upstream

**Risk:** Model provider rate limits block pipeline  
**Mitigation:** Implement exponential backoff, batch requests, use multiple providers

### Data Risks

**Risk:** Input datasets contain PII or harmful content  
**Mitigation:** Add PII filter stage, safety classifier, document data provenance

**Risk:** Generated conversations are factually incorrect  
**Mitigation:** Add fact-checking stage (optional), document limitations, human review sample

**Risk:** Tool calls execute dangerous operations  
**Mitigation:** Sandbox tool execution, whitelist safe operations, add human-in-loop for sensitive tools

### Operational Risks

**Risk:** Pipeline failures lose progress on large batches  
**Mitigation:** Checkpoint at each stage boundary, enable restart from checkpoint

**Risk:** Observability overhead impacts performance  
**Mitigation:** Make observability optional, sample traces, use async export

**Risk:** Output datasets are too large for git  
**Mitigation:** Use git LFS for test data, publish finals to HF Hub, document storage policy

---

## Conclusion

The infrastructure is **production-ready**. The path forward is clear:

1. Add Strands SDK dependencies
2. Configure model provider authentication
3. Implement transformation stages with proven methodologies (APIGen, ReviewInstruct)
4. Test end-to-end with cybersecurity datasets
5. Iterate on quality, then scale to production

**Estimated Timeline:** 4-6 weeks to first production-quality dataset

**Key Success Metric:** >80% human acceptance rate on refined agentic multi-turn cybersecurity conversations with verified tool calls

**Blocker Resolution:** Strands SDK is available ✓, model providers are accessible ✓, methodologies are documented ✓

**Next Action:** Update pyproject.toml with Strands SDK dependencies and configure model provider authentication.
