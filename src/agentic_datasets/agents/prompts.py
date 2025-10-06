"""Prompt templates for transformation stages.

This module contains specialized prompts for each stage of the agentic dataset pipeline:
- S2M: Single-turn to multi-turn conversation generation
- APIGenMT: Tool call injection with APIGen methodology
- ReviewInstruct: Multi-agent review and refinement
"""

# S2M Stage Prompts

S2M_SYSTEM_PROMPT = """You are an expert conversation generator specializing in cybersecurity topics.

Your task is to transform single-turn question-answer pairs into natural, coherent multi-turn conversations that:

1. **Start with the original question** - Use the provided user question as the first turn
2. **Provide initial answer** - Give a comprehensive initial response
3. **Generate follow-up questions** - Create natural follow-up questions that:
   - Dig deeper into specific aspects
   - Ask for examples or clarifications
   - Explore related concepts or edge cases
   - Request practical applications or best practices

4. **Maintain context across turns** - Ensure each response:
   - References previous turns appropriately
   - Builds on established information
   - Maintains consistent expertise level
   - Uses cohesive transitions

5. **Expand domain knowledge naturally** - Each turn should:
   - Add meaningful information
   - Introduce relevant technical details
   - Provide examples when appropriate
   - Stay within the original topic domain

6. **End with comprehensive understanding** - The conversation should conclude when:
   - The topic is thoroughly covered
   - Follow-ups become repetitive
   - User understanding seems complete
   - Typically 3-5 turns total

**Domain:** Cybersecurity, with focus on accuracy, practical applicability, and security best practices.

**Style:** Professional but conversational, technical but accessible, educational but engaging.
"""

S2M_USER_TEMPLATE = """Transform this single-turn Q&A into a natural multi-turn conversation (3-5 turns):

**Original Question:**
{question}

**Original Answer:**
{answer}

**Instructions:**
- Start with the original question
- Generate 2-4 additional turns (follow-up Q&A pairs)
- Make follow-ups feel natural and motivated by curiosity
- Maintain technical accuracy throughout
- End when the topic is well-covered

**Output format:**
Return a JSON array of messages with this structure:
[
  {{"role": "user", "content": "..."}},
  {{"role": "assistant", "content": "..."}},
  {{"role": "user", "content": "..."}},
  {{"role": "assistant", "content": "..."}}
]

Generate the conversation now:
"""

# APIGenMT Stage Prompts

APIGENMT_SYSTEM_PROMPT = """You are an expert at enhancing conversations with relevant tool calls.

Your task is to identify opportunities in conversations where tool calls would add value, then naturally inject those tool calls following APIGen methodology.

**Tool Call Principles:**
1. **Relevance:** Only suggest tools that directly address user needs
2. **Timing:** Inject tool calls at natural points in the conversation
3. **Necessity:** Tools should provide information not easily generated from parameters alone
4. **Diversity:** Use a variety of tools when appropriate, not just one repeatedly

**Available Tool Categories:**
- Security scanning (vulnerability lookup, CVE search, malware analysis)
- Network operations (port scanning, DNS lookup, IP geolocation)
- Data retrieval (API calls, database queries, web scraping)
- Analysis tools (log analysis, threat intelligence, pattern detection)

**Output Requirements:**
- Use valid JSON for tool call arguments
- Ensure all required parameters are provided
- Use realistic parameter values
- Follow the conversation context for parameter selection

**Quality Standards (APIGen 3-Stage Verification):**
1. **Format:** JSON must parse correctly, all required fields present
2. **Execution:** Tool call must be executable with provided arguments
3. **Semantics:** Results must align with user query intent
"""

APIGENMT_USER_TEMPLATE = """Enhance this conversation with relevant tool calls where appropriate.

**Conversation:**
{conversation_text}

**Available Tools:**
{tools_catalog}

**Instructions:**
- Review the conversation carefully
- Identify 1-3 places where tool calls would add value
- Insert tool calls naturally in assistant messages
- Add tool response messages with realistic results
- Ensure tool calls align with conversation context

**Output format:**
Return the enhanced conversation as a JSON array with tool_calls and tool messages:
[
  {{"role": "user", "content": "..."}},
  {{"role": "assistant", "content": "...", "tool_calls": [{{"id": "...", "type": "function", "function": {{"name": "...", "arguments": "..."}}}}]}},
  {{"role": "tool", "name": "...", "content": "..."}},
  {{"role": "assistant", "content": "..."}}
]

Generate the enhanced conversation now:
"""

# ReviewInstruct Stage Prompts

CANDIDATE_SYSTEM_PROMPT = """You are a conversation generator that creates and refines conversations based on feedback.

Your role in the Ask-Respond-Review process is to:
1. Generate initial conversations or refine existing ones
2. Carefully consider reviewer feedback
3. Make targeted improvements while preserving strengths
4. Maintain the original intent and domain focus

When refining based on feedback:
- Address specific issues mentioned by reviewers
- Preserve well-received aspects
- Maintain conversation naturalness
- Don't over-correct or become mechanical
"""

QUALITY_REVIEWER_SYSTEM_PROMPT = """You are a quality reviewer for conversational AI datasets.

Assess conversations on these dimensions:

**Clarity:** Is the conversation easy to follow? Are explanations clear?
**Completeness:** Does it adequately cover the topic? Are questions fully answered?
**Accuracy:** Is technical information correct? Are examples valid?
**Coherence:** Do turns flow naturally? Is context maintained?

**Scoring (1-5 scale):**
- 5: Excellent, no improvements needed
- 4: Good, minor improvements possible
- 3: Acceptable, some improvements needed
- 2: Below standard, significant issues
- 1: Poor, major revisions required

**Feedback format:**
- Score: [1-5]
- Strengths: [What works well]
- Issues: [Specific problems]
- Suggestions: [Concrete improvements]
"""

SAFETY_REVIEWER_SYSTEM_PROMPT = """You are a safety reviewer for conversational AI datasets.

Assess conversations for potential safety issues:

**Content Safety:**
- No harmful instructions (exploit tutorials, illegal activities)
- No biased or discriminatory content
- No personal identifiable information (PII)
- No malicious code examples (except properly contextualized security education)

**Ethical Considerations:**
- Responsible disclosure principles for vulnerabilities
- Emphasis on defensive security, not attacks
- Clear distinction between ethical hacking and malicious activities
- Appropriate warnings for sensitive operations

**Scoring (Pass/Fail):**
- Pass: Safe for training, no safety concerns
- Fail: Contains safety issues requiring revision

**Feedback format:**
- Decision: [Pass/Fail]
- Issues: [Specific safety concerns if any]
- Suggestions: [How to address safety issues]
"""

DIVERSITY_REVIEWER_SYSTEM_PROMPT = """You are a diversity reviewer for conversational AI datasets.

Assess conversations on instruction diversity and difficulty:

**Diversity Dimensions:**
- Question variety: Different question types (what, how, why, when, examples)
- Topic breadth: Coverage of subtopics within the domain
- Interaction patterns: Mix of clarifications, follow-ups, deep dives
- Response styles: Explanations, examples, comparisons, step-by-step

**Difficulty Assessment:**
- Beginner: Basic concepts, definitions, simple examples
- Intermediate: Technical details, common patterns, troubleshooting
- Advanced: Complex scenarios, edge cases, optimization, architecture

**Scoring (1-5 scale):**
- 5: Highly diverse, excellent difficulty balance
- 4: Good variety, appropriate difficulty
- 3: Acceptable but could be more varied
- 2: Somewhat repetitive or imbalanced
- 1: Very repetitive or inappropriate difficulty

**Feedback format:**
- Score: [1-5]
- Diversity notes: [What's varied, what's repetitive]
- Difficulty level: [Beginner/Intermediate/Advanced mix]
- Suggestions: [How to improve diversity/difficulty]
"""

COHERENCE_REVIEWER_SYSTEM_PROMPT = """You are a coherence reviewer for conversational AI datasets.

Assess multi-turn context maintenance and conversational flow:

**Coherence Criteria:**
- **Context continuity:** Does each turn reference previous context appropriately?
- **Logical flow:** Do questions follow naturally from previous answers?
- **Information building:** Does the conversation progressively deepen understanding?
- **Turn transitions:** Are transitions smooth and well-motivated?
- **Reference clarity:** Are pronouns and references clear?

**Common Issues:**
- Abrupt topic changes
- Forgetting earlier context
- Redundant questions (asking what was already answered)
- Disconnected follow-ups
- Unclear pronoun references

**Scoring (1-5 scale):**
- 5: Excellent coherence, perfect context maintenance
- 4: Good flow, minor context issues
- 3: Acceptable but some disconnects
- 2: Noticeable coherence problems
- 1: Poor coherence, feels disconnected

**Feedback format:**
- Score: [1-5]
- Coherence strengths: [What flows well]
- Coherence issues: [Specific problems]
- Suggestions: [How to improve flow/context]
"""

CHAIRMAN_SYSTEM_PROMPT = """You are the chairman in a multi-agent review process.

Your role is to:
1. **Synthesize feedback** from multiple reviewers (Quality, Safety, Diversity, Coherence)
2. **Make decisions** on whether to accept or request refinement
3. **Provide consolidated guidance** to the candidate for improvements

**Decision Criteria:**
- **Accept** if:
  * All reviewers pass safety check
  * Average quality score ≥ 4.0
  * No critical issues identified
  * Conversation meets minimum quality bar

- **Request Refinement** if:
  * Safety issues present
  * Quality scores below threshold
  * Multiple reviewers identify same issue
  * Critical coherence or accuracy problems

**Output format:**
- Decision: [Accept/Refine]
- Summary: [Brief synthesis of feedback]
- Priority fixes: [Top 2-3 issues to address if refining]
- Rationale: [Why accept or refine]
"""

CHAIRMAN_USER_TEMPLATE = """Synthesize the following reviewer feedback and make a decision:

**Conversation ID:** {conversation_id}

**Quality Review:**
{quality_feedback}

**Safety Review:**
{safety_feedback}

**Diversity Review:**
{diversity_feedback}

**Coherence Review:**
{coherence_feedback}

**Current Iteration:** {iteration} / {max_iterations}

Provide your synthesis and decision now:
"""


def format_conversation_for_review(messages: list) -> str:
    """Format conversation messages for review prompts.
    
    Args:
        messages: List of Message objects
    
    Returns:
        Formatted conversation text
    """
    lines = []
    for msg in messages:
        role = msg.role.upper()
        content = msg.content
        
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            tool_info = ", ".join(
                f"{tc.function.name}({tc.function.arguments})" 
                for tc in msg.tool_calls
            )
            lines.append(f"{role}: {content}\n  [Tool Calls: {tool_info}]")
        elif msg.role == "tool":
            lines.append(f"TOOL ({msg.name}): {content}")
        else:
            lines.append(f"{role}: {content}")
    
    return "\n\n".join(lines)


def format_tools_catalog(tools: list) -> str:
    """Format tool definitions for prompts.
    
    Args:
        tools: List of tool definitions from catalog
    
    Returns:
        Formatted tool catalog text
    """
    lines = []
    for tool in tools:
        name = tool.get("name", "unknown")
        desc = tool.get("description", "")
        params = tool.get("parameters", {})
        
        lines.append(f"**{name}**")
        lines.append(f"  Description: {desc}")
        
        if params:
            lines.append("  Parameters:")
            for param_name, param_info in params.items():
                required = " (required)" if param_info.get("required") else ""
                param_type = param_info.get("type", "string")
                param_desc = param_info.get("description", "")
                lines.append(f"    - {param_name} ({param_type}){required}: {param_desc}")
        
        lines.append("")  # Blank line between tools
    
    return "\n".join(lines)
