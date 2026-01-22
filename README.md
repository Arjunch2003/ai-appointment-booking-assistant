# 🏥 AI Booking Assistant for Amrita Hospital

![Status: Active](https://img.shields.io/badge/Status-Active-success.svg)
![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Framework-Streamlit-red.svg)
![LangChain](https://img.shields.io/badge/Library-LangChain-green.svg)
![LLM](https://img.shields.io/badge/LLM-Llama3-orange.svg)

An intelligent, conversational AI assistant designed to streamline medical appointment bookings and patient inquiries for Amrita Hospital. This application uses Large Language Models (LLM) and Retrieval-Augmented Generation (RAG) to provide a seamless user experience.

---

## 📑 Table of Contents
- [✨ Key Features](#-key-features)
- [🛠️ Tech Stack](#-tech-stack)
- [🧩 Architecture & Methodology](#-architecture--methodology)
  - [1. Conversational Flow (Intent Detection)](#1-conversational-flow-intent-detection)
  - [2. Booking System (Regex + LLM)](#2-booking-system-regex--llm)
  - [3. RAG Pipeline (Knowledge Base)](#3-rag-pipeline-knowledge-base)
  - [4. Admin Dashboard](#4-admin-dashboard)
- [🚀 Setup & Installation](#-setup--installation)
- [📂 Project Structure](#-project-structure)
- [🔮 Future Roadmap](#-future-roadmap)

---

## ✨ Key Features

1.  **🤖 Conversational AI Interface**
    - Natural language understanding to handle diverse user queries.
    - Context-aware responses that maintain conversation history.
    - Friendly and empathetic tone appropriate for healthcare.

2.  **📅 Smart Appointment Booking**
    - **Step-by-step guidance**: Collects Name, Email, Phone, Specialty, Date, and Time.
    - **Intelligent Extraction**: Uses LLM and Regex to extract details from natural language (e.g., "Book for next Monday at 2 PM").
    - **Validation**: Ensures valid emails, phone numbers (10 digits), and future dates.
    - **Confirmation**: Summarizes details before finalizing.

3.  **📧 Automated Notifications**
    - Sends real-time email confirmations to patients upon successful booking (SMTP configured).

4.  **📚 RAG-Powered Knowledge Base**
    - **PDF Upload**: Admins or users can upload hospital brochures/PDFs.
    - **Q&A**: The bot answers general queries (e.g., "What are the visiting hours?", "Who is the head cardiologist?") based strictly on uploaded documents.

5.  **👮 Admin Dashboard**
    - **Secure Login**: Access controlled via credentials.
    - **Analytics**: Real-time stats on total appointments, pending requests, and unique patients.
    - **Appointment Management**: View, filter, and update status (Pending/Confirmed/Cancelled) of bookings.
    - **Search & Filter**: Powerful filtering by status, date, and patient details.

---

## 🛠️ Tech Stack

-   **Frontend**: [Streamlit](https://streamlit.io/) (Python-based web framework)
-   **LLM Engine**: [Groq API](https://groq.com/) (using Llama-3-8b-instant for fast inference)
-   **Orchestration**: [LangChain](https://www.langchain.com/) for managing prompts and chains.
-   **Vector Database**: [FAISS](https://github.com/facebookresearch/faiss) (local vector store for RAG).
-   **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` (via HuggingFace).
-   **Database**: SQLite (local lightweight relational DB for bookings/users).
-   **Data Processing**: PyPDF2 (PDF parsing) and pandas (Data manipulation).

---

## 🧩 Architecture & Methodology

### 1. Conversational Flow (Intent Detection)
The system uses a hybrid approach to understand user intent:
-   **Keyword Matching**: Rapidly detects explicit commands (e.g., "cancel", "stop").
-   **LLM Classification**: Analyzes context to determine if the user wants to **Book an Appointment** or has a **General Query**.
-   **State Management**: Uses `Streamlit Session State` to track if a user is currently in a booking flow or asking general questions.

### 2. Booking System (Regex + LLM)
To ensure high accuracy in data collection:
-   **Regex First**: Uses regular expressions for definitive patterns (Email, Phone, Date formats).
-   **LLM Fallback**: If Regex fails coverage (e.g., "next Friday afternoon"), the LLM extracts structured data (JSON) from the text.
-   **Missing Information Loop**: The `BookingFlow` class identifies missing fields and prompts the user specifically for them.

### 3. RAG Pipeline (Knowledge Base)
For answering hospital-related questions:
1.  **Ingestion**: PDFs are uploaded via the sidebar.
2.  **Chunking**: Text is split into manageable chunks (1000 characters) using `RecursiveCharacterTextSplitter`.
3.  **Embedding**: Chunks are converted to vector embeddings.
4.  **Retrieval**: When a question is asked, the system performs a similarity search in FAISS to find the top 4 relevant chunks.
5.  **Generation**: The LLM generates an answer using ONLY the retrieved context.

### 4. Admin Dashboard
A dedicated tab for hospital administrators:
-   Connects directly to the SQLite database.
-   Provides an interactive `st.data_editor` to change booking statuses inline.
-   Protected by simple credential authentication (configurable in `.env`).

---

## 🚀 Setup & Installation

### Prerequisites
-   Python 3.9 or higher
-   A [Groq API Key](https://console.groq.com/) (Free tier available)
-   (Optional) Gmail App Password for sending real emails.

### Installation Steps

1.  **Clone the Repository** (or download source)
    ```bash
    git clone https://github.com/your-username/ai-booking-assistant.git
    cd ai-booking-assistant
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment Variables**
    Create a `.env` file in the `app` directory (or root) with the following structure:
    ```env
    # API Keys
    GROQ_API_KEY=your_groq_api_key_here

    # App Settings
    APP_NAME="Amrita Hospital"
    DEBUG=True

    # Email (Optional - for real emails)
    EMAIL_SENDER=your_email@gmail.com
    EMAIL_PASSWORD=your_app_password

    # Admin Login
    ADMIN_USERNAME=admin
    ADMIN_PASSWORD=password123
    ```

4.  **Run the Application**
    ```bash
    streamlit run app/main.py
    ```

5.  **Access the App**
    Open your browser and navigate to `http://localhost:8501`.

---

## 📂 Project Structure

```
project-root/
├── app/
│   ├── main.py              # Entry point (UI & Routing)
│   ├── chat_logic.py        # Core conversation handler (Intent, History)
│   ├── booking_flow.py      # Slot-filling logic for appointments
│   ├── rag_pipeline.py      # RAG implementation (PDF -> FAISS -> LLM)
│   ├── admin_dashboard.py   # Admin UI & Logic
│   ├── tools.py             # Utilities (Email, DB helpers)
│   ├── config.py            # Environement config & constants
│   └── .env                 # API Keys & Secrets (GitIgnored)
├── data/                    # Storage for Vector DB & Uploads
├── db/
│   ├── database.py          # SQLite connection manager
│   └── models.py            # Data models (optional)
├── logs/                    # Application logs
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation
```

---

## 🔮 Future Roadmap

-   [ ] **Voice Interface**: Add speech-to-text for voice bookings.
-   [ ] **Doctor Availability**: Integrate with a real calendar API (Google Calendar/Outlook) to check actual slot availability.
-   [ ] **Multi-language Support**: Enable booking in Hindi, Malayalam, etc.
-   [ ] **Authentication**: Add proper user accounts for patients to view their history.

---
**Developed for Amrita Hospital** | 2026
