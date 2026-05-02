# ai-customer-support-agent

# AI Customer Support Agent

A production-ready multi-turn AI support agent that handles customer queries 
through a natural conversation interface. The agent checks order status, logs 
complaints, retrieves business information, and escalates to human agents — 
all by deciding which tools to call based on the customer's message.

**Live Demo:** [your-app.streamlit.app](https://ai-customer-support-agent-ymriu4vigtikvtwksjvmwp.streamlit.app/)  
**API Docs:** [your-api.onrender.com/docs](https://ai-customer-support-agent-uf0z.onrender.com/docs)

---

## What Makes This an Agent (Not a Chatbot)

A chatbot follows a fixed script. An agent decides what to do next.

When a customer sends a message, this system does not follow a predetermined 
flow. The LLM reads the message, decides whether to answer directly or call 
a tool, executes that tool, reads the result, and decides what to do next — 
looping until it has a complete answer. This is the architecture behind every 
serious AI product being built today.

---

## What It Can Do

| Capability | How |
|---|---|
| Check order status | `check_order_status` tool → SQLite query |
| Retrieve order history | `get_orders_by_email` tool → SQLite query |
| Log complaints | `log_complaint` tool → persisted to database |
| Answer policy questions | `get_business_info` tool → structured responses |
| Escalate to human | `escalate_to_human` tool → escalation record created |
| Remember conversation | LangGraph MemorySaver → state persisted by session ID |

---

## System Architecture

```
User sends message
        │
        ▼
[FastAPI] receives message + session_id
        │
        ▼
[LangGraph StateGraph]
        │
        ▼
   [llm_node] ← LLM reads message + full conversation history
        │
        ├── Tool call requested → [tool_node] → executes tool → back to llm_node
        │
        └── No tool call → final answer → END
        │
        ▼
[MemorySaver] persists state by session_id
        │
        ▼
[FastAPI] returns response + tools_used
        │
        ▼
[Streamlit] displays message + tool activity
```

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Agent Framework | LangGraph | Stateful agent loop with memory |
| LLM | Groq — Llama 3 70B Tool Use | Fast inference, tool calling |
| Memory | LangGraph MemorySaver | Conversation persistence by session |
| Tools | Custom Python + LangChain @tool | Order lookup, complaints, escalation |
| Database | SQLite + SQLAlchemy | Order and complaint storage |
| Backend | FastAPI | REST API with session management |
| Frontend | Streamlit | Chat interface with tool activity display |
| Containerisation | Docker + Docker Compose | Local dev parity |
| Backend Hosting | Render | FastAPI deployment |
| Frontend Hosting | Streamlit Community Cloud | Streamlit deployment |

---

## Key Engineering Decisions

**Why LangGraph over a simple LLM call?**  
A single LLM call cannot maintain conversation history or conditionally call 
tools across multiple turns. LangGraph's StateGraph manages the full 
conversation state and routes between the LLM and tools automatically.

**Why tool docstrings matter:**  
The LLM reads each tool's docstring to decide whether to call it. A vague 
docstring causes wrong tool calls. A precise docstring makes the agent 
behave predictably. Docstrings here are functional code, not documentation.

**Why session_id = thread_id:**  
LangGraph's MemorySaver uses thread_id as the key to separate conversation 
histories. Each user gets a unique session_id — conversations never mix 
even under concurrent load.

**Why SQLite over PostgreSQL:**  
For a portfolio project demonstrating agent tool calling, SQLite needs zero 
infrastructure. The architecture supports swapping to PostgreSQL by changing 
one environment variable.

---

## Project Structure

```
ai-customer-support-agent/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── chat.py          # POST /chat/message, POST /chat/session
│   │   │   └── health.py        # GET /health
│   │   └── schemas.py           # Request/response Pydantic models
│   ├── core/
│   │   ├── agent.py             # LangGraph StateGraph agent
│   │   ├── tools.py             # Five agent tools with @tool decorator
│   │   └── prompts.py           # System prompt defining agent behaviour
│   ├── db/
│   │   ├── database.py          # SQLAlchemy engine and session management
│   │   ├── models.py            # Orders, complaints, escalations tables
│   │   └── queries.py           # Database operations called by tools
│   ├── services/
│   │   └── chat_service.py      # Session management and agent invocation
│   ├── config.py                # Single source of truth for all settings
│   └── main.py                  # FastAPI app factory and startup
├── frontend/
│   ├── app.py                   # Streamlit chat UI
│   ├── api_client.py            # HTTP client for backend communication
│   └── config.py                # Frontend configuration
├── scripts/
│   └── seed_data.py             # Populates database with mock orders
├── tests/
│   ├── test_tools.py
│   ├── test_api.py
│   └── test_agent.py
├── Dockerfile
├── Dockerfile.frontend
├── docker-compose.yml
├── runtime.txt                  # Pins Python 3.12.3 for Render
├── .env.example
└── requirements.txt
```

---

## Running Locally

### Prerequisites
- Python 3.12+
- A [Groq](https://console.groq.com) free API key

### Setup

**1. Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/ai-customer-support-agent.git
cd ai-customer-support-agent
```

**2. Create and activate virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure environment variables**
```bash
cp .env.example .env
# Add your GROQ_API_KEY to .env
```

**5. Seed the database**
```bash
python scripts/seed_data.py
```

**6. Start the backend**
```bash
uvicorn app.main:app --reload --port 8000
```

**7. Start the frontend** (new terminal)
```bash
cd frontend
streamlit run app.py
```

Visit `http://localhost:8501` and click **New Chat** to start.

### Test Orders Available
| Order ID | Customer | Status |
|---|---|---|
| ORD-001 | Amina Bello | Delivered |
| ORD-002 | Chukwuemeka Obi | Shipped |
| ORD-003 | Fatima Aliyu | Processing |
| ORD-004 | Taiwo Adeyemi | Pending |
| ORD-005 | Ngozi Eze | Cancelled |
| ORD-006 | Mubarak Oladipo | Shipped |

### Running with Docker
```bash
docker compose up --build
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/chat/message` | Send message, get agent response |
| `POST` | `/api/v1/chat/session` | Create new conversation session |
| `GET` | `/health` | Health check including database status |

Full interactive docs at `/docs`.

---

## Running Tests
```bash
python -m pytest tests/ -v
```

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `GROQ_API_KEY` | ✅ | — | Groq API key |
| `LLM_MODEL` | ❌ | `llama3-groq-70b-8192-tool-use-preview` | Groq model |
| `DATABASE_URL` | ❌ | `sqlite:///./data/support.db` | Database connection string |
| `TEMPERATURE` | ❌ | `0.1` | LLM temperature |
| `MAX_ITERATIONS` | ❌ | `10` | Max agent loop iterations |
| `APP_ENV` | ❌ | `development` | Environment name |

---

## Author

**Mubarak Olalekan Oladipo**  
AI Software Engineer  
[GitHub](https://github.com/Mubrix2) · [LinkedIn](https://linkedin.com/in/mubarak-oladipo/)
