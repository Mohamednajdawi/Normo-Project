# Active Context

- Current focus: Docker deployment issues resolved - Python version fixed, app path corrected, port conflicts resolved.
- Issue: Backend failing to start due to missing OPENAI_API_KEY environment variable.
- Next: Configure OpenAI API key in docker-compose.yml to enable backend startup.
- Decisions: Use LangGraph with tool routing; keep tools simple (echo, add) initially.
