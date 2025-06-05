# LangGraph Creative Writer

This project demonstrates a creative‑writing agent built with [LangGraph](https://github.com/langchain-ai/langgraph) and Google Gemini.
The graph coordinates multiple LLM driven nodes to iterate from a user query all
the way to a revised story draft.

## Architecture
- **ReAct style reasoning** powers decision making between nodes.
- **Human‑in‑the‑loop** feedback influences story ideas and outlines.
- A **Supervisor** node evaluates outlines before drafting.

The graph is rendered below and can also be explored in the
`writer.ipynb` notebook.

![Writer graph](writer_graph.png)

## Setup
1. Install Python 3.10+.
2. Install dependencies:
   ```bash
   pip install -e .
   ```
3. Set environment variables required by `langchain-google-genai` (e.g.
   `GOOGLE_API_KEY`). You can use a `.env` file which is loaded automatically.

## Running
Run the graph to compile and visualize it:

```bash
python graph.py
```

This will build the `StateGraph` and display the workflow image. From here you
can experiment by calling individual nodes or adapting the graph for your own
projects.

