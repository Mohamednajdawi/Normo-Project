# LLM Gate Implementation

This document describes the LLM Gate system that intelligently routes queries between simple LLM responses and the full agentic workflow.

## Overview

The LLM Gate is a smart routing system that determines whether a user query requires the full agentic workflow (with document retrieval, analysis, and citations) or can be answered with a simple LLM response.

## Architecture

```
User Query → LLM Gate → Decision
                        ├── Simple LLM Response (for general queries)
                        └── Full Agent Workflow (for architectural queries)
```

## Decision Logic

### Simple LLM Response (No Agent)

Used for:
- General greetings ("Hello", "How are you", "Hi")
- System status questions ("What can you do", "Help")
- General explanations about the system
- Non-technical questions
- Simple clarifications or confirmations
- General conversation summaries

### Full Agent Workflow

Used for:
- Building requirements, codes, regulations
- Architectural planning, calculations, measurements
- Fire safety, accessibility, energy efficiency
- Legal compliance, permits, standards
- Specific technical questions about construction
- Questions requiring document retrieval and analysis
- Any query that might need to search through legal documents

## Implementation

### Core Components

1. **LLMGate Class** (`src/normo_backend/agents/llm_gate.py`):
   - `should_use_agent()`: Determines routing decision
   - `get_simple_response()`: Generates simple LLM responses

2. **API Integration** (`src/normo_backend/api/app.py`):
   - Modified `/chat` endpoint to use LLM gate
   - Automatic routing based on gate decision

### Decision Process

```python
# 1. Analyze query with LLM
gate_decision = llm_gate.should_use_agent(user_query, conversation_history)

# 2. Route based on decision
if gate_decision["use_agent"]:
    # Use full agentic workflow
    result = graph.invoke(agent_state)
else:
    # Use simple LLM response
    response = llm_gate.get_simple_response(user_query, conversation_history)
```

## Performance Benefits

### Efficiency Gains

1. **Faster Response Times**:
   - Simple queries: ~1-2 seconds (vs 30-60 seconds for agent)
   - No document retrieval for general questions
   - Reduced API calls and processing

2. **Cost Optimization**:
   - Fewer LLM calls for simple queries
   - No vector store queries for general questions
   - Reduced computational overhead

3. **Better User Experience**:
   - Immediate responses for greetings and general questions
   - Appropriate level of detail for each query type
   - Clear distinction between system capabilities

## Test Results

The LLM Gate achieves **100% accuracy** in test scenarios:

### Test Cases (18/18 Correct)

**General Queries (8/8 Correct)**:
- ✅ "Hello" → Simple LLM
- ✅ "How are you?" → Simple LLM
- ✅ "What can you do?" → Simple LLM
- ✅ "Help" → Simple LLM
- ✅ "Thank you" → Simple LLM
- ✅ "Goodbye" → Simple LLM
- ✅ "What is your name?" → Simple LLM
- ✅ "Summarize our conversation" → Simple LLM

**Architectural Queries (10/10 Correct)**:
- ✅ "What are the building requirements in Austria?" → Agent
- ✅ "I need to know about playground area requirements" → Agent
- ✅ "What are the fire safety regulations?" → Agent
- ✅ "How do I calculate the minimum room height?" → Agent
- ✅ "What are the OIB guidelines for accessibility?" → Agent
- ✅ "I'm building a 5-flat apartment building in Linz" → Agent
- ✅ "What are the energy efficiency standards?" → Agent
- ✅ "Can you help me with building codes?" → Agent
- ✅ "What are the minimum dimensions for stairs?" → Agent
- ✅ "I need information about Austrian construction law" → Agent

## Configuration

### Gate Prompt

The gate uses a carefully crafted system prompt that:

1. **Defines Clear Criteria**: Explicit rules for when to use each path
2. **Provides Examples**: Concrete examples of each query type
3. **Ensures Safety**: Defaults to agent workflow for uncertain cases
4. **Maintains Context**: Considers conversation history

### Response Format

The gate returns structured JSON:

```json
{
  "use_agent": true/false,
  "reason": "Brief explanation of decision"
}
```

## Error Handling

### Fallback Strategy

1. **JSON Parse Errors**: Default to agent workflow
2. **LLM Errors**: Default to agent workflow
3. **Connection Issues**: Graceful degradation

### Safety Measures

- **Conservative Approach**: When in doubt, use agent workflow
- **Error Logging**: All gate decisions are logged
- **Monitoring**: Track decision accuracy and performance

## Usage Examples

### General Query (Simple LLM)

**Input**: "Hello, how are you?"

**Gate Decision**: `{"use_agent": false, "reason": "General greeting, no architectural content"}`

**Response**: "Hello! I'm here to assist you with questions about the Normo architectural legal document analysis system. How can I help you today?"

**Processing Time**: ~1-2 seconds
**Source Citations**: 0

### Architectural Query (Full Agent)

**Input**: "What are the building height requirements in Austria?"

**Gate Decision**: `{"use_agent": true, "reason": "Requires specific legal document analysis for building requirements in Austria"}`

**Response**: Comprehensive answer with specific regulations, calculations, and citations from Austrian legal documents.

**Processing Time**: ~30-60 seconds
**Source Citations**: 12+ detailed citations

## Monitoring and Analytics

### Metrics Tracked

1. **Decision Accuracy**: Percentage of correct routing decisions
2. **Response Times**: Average time for each path
3. **User Satisfaction**: Based on query appropriateness
4. **Cost Analysis**: API usage and computational costs

### Logging

All gate decisions are logged with:
- Query text
- Decision made
- Reasoning provided
- Response time
- User feedback (if available)

## Future Enhancements

### Planned Improvements

1. **Learning System**: Adapt based on user feedback
2. **Context Awareness**: Better conversation history analysis
3. **Custom Rules**: User-defined routing criteria
4. **Performance Optimization**: Caching and pre-computation
5. **Analytics Dashboard**: Real-time monitoring interface

### Advanced Features

1. **Multi-Modal Gates**: Handle images, documents, etc.
2. **Dynamic Thresholds**: Adjustable sensitivity settings
3. **A/B Testing**: Compare different gate strategies
4. **User Preferences**: Personalized routing rules

## Troubleshooting

### Common Issues

1. **Incorrect Routing**:
   - Check gate prompt clarity
   - Review decision examples
   - Analyze user feedback

2. **Performance Issues**:
   - Monitor response times
   - Check LLM API latency
   - Optimize prompt length

3. **Edge Cases**:
   - Ambiguous queries
   - Multi-part questions
   - Context-dependent decisions

### Debug Commands

```bash
# Test gate decisions
python test_llm_gate.py

# Check API integration
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hello"}]}'

# Monitor logs
tail -f logs/gate_decisions.log
```

## Conclusion

The LLM Gate significantly improves system efficiency by:

- **Reducing Response Times** for simple queries
- **Optimizing Resource Usage** through intelligent routing
- **Enhancing User Experience** with appropriate response levels
- **Maintaining Accuracy** for complex architectural queries

The system achieves 100% accuracy in test scenarios and provides a robust foundation for handling diverse user queries efficiently.
