"""
RAG Pipeline for PDF processing and question answering using FAISS
"""

import os
from typing import List, Optional
from pathlib import Path
import pickle

# Try to import FAISS
try:
    import faiss
    from langchain_community.vectorstores import FAISS
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("⚠️ FAISS not installed. Install with: pip install faiss-cpu")

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain_community.embeddings import HuggingFaceEmbeddings

# Try different Document imports
try:
    from langchain_core.documents import Document
except ImportError:
    try:
        from langchain.docstore.document import Document
    except ImportError:
        # Simple fallback Document class
        class Document:
            def __init__(self, page_content: str, metadata: dict = None):
                self.page_content = page_content
                self.metadata = metadata or {}

import PyPDF2
from langchain_groq import ChatGroq

from app import config


class RAGPipeline:
    """RAG Pipeline for processing PDFs and answering questions using FAISS"""
    
    def __init__(self):
        self.embedding_model = None
        self.vector_store = None
        self.llm = None
        self.documents_loaded = False
        self.faiss_index_path = config.DATA_DIR / "faiss_index"
        self.faiss_index_path.mkdir(exist_ok=True, parents=True)
        
    def initialize(self):
        """Initialize the RAG pipeline components"""
        try:
            if not FAISS_AVAILABLE:
                print("⚠️ FAISS not available. RAG features will be limited.")
                # Still initialize Groq client for general responses
                if config.GROQ_API_KEY:
                    self.llm = ChatGroq(
                        groq_api_key=config.GROQ_API_KEY,
                        model_name=config.LLM_MODEL,
                        temperature=0.7
                    )
                return False
            
            print("🔄 Initializing RAG pipeline with FAISS...")
            
            # Initialize embeddings
            self.embedding_model = HuggingFaceEmbeddings(
                model_name=config.EMBEDDING_MODEL,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            
            print("✅ Embeddings model loaded")
            
            # Try to load existing FAISS index
            try:
                index_file = self.faiss_index_path / "index.faiss"
                pkl_file = self.faiss_index_path / "index.pkl"
                
                if index_file.exists() and pkl_file.exists():
                    self.vector_store = FAISS.load_local(
                        str(self.faiss_index_path),
                        self.embedding_model,
                        allow_dangerous_deserialization=True
                    )
                    self.documents_loaded = True
                    print("✅ Loaded existing FAISS index")
            except Exception as e:
                print(f"ℹ️ No existing index found: {e}")
            
            # Initialize Groq client
            if config.GROQ_API_KEY:
                self.llm = ChatGroq(
                    groq_api_key=config.GROQ_API_KEY,
                    model_name=config.LLM_MODEL,
                    temperature=0.7
                )
                print("✅ Groq LLM initialized")
            
            print("✅ RAG pipeline initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error initializing RAG pipeline: {e}")
            # Still try to initialize Groq for general responses
            if config.GROQ_API_KEY:
                self.llm = ChatGroq(
                    groq_api_key=config.GROQ_API_KEY,
                    model_name=config.LLM_MODEL,
                    temperature=0.7
                )
            return False
    
    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text from uploaded PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into chunks"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP,
            length_function=len,
        )
        chunks = text_splitter.split_text(text)
        return chunks
    
    def process_pdfs(self, pdf_files: List) -> dict:
        """
        Process uploaded PDF files and store in FAISS vector database
        
        Args:
            pdf_files: List of uploaded PDF files
            
        Returns:
            Dictionary with processing status
        """
        try:
            if not FAISS_AVAILABLE:
                return {'success': False, 'error': 'FAISS not installed. Please install faiss-cpu'}
            
            if not self.embedding_model:
                self.initialize()
            
            print("🔄 Processing PDFs...")
            all_documents = []
            
            for i, pdf_file in enumerate(pdf_files):
                print(f"  Processing {pdf_file.name}...")
                # Extract text
                text = self.extract_text_from_pdf(pdf_file)
                
                # Chunk text
                chunks = self.chunk_text(text)
                
                # Create Document objects
                for j, chunk in enumerate(chunks):
                    doc = Document(
                        page_content=chunk,
                        metadata={
                            'source': pdf_file.name,
                            'chunk_id': j,
                            'file_index': i
                        }
                    )
                    all_documents.append(doc)
            
            if not all_documents:
                return {'success': False, 'error': 'No text extracted from PDFs'}
            
            print(f"✅ Created {len(all_documents)} document chunks")
            
            # Create or update FAISS vector store
            if self.vector_store is None:
                print("🔄 Creating new FAISS index...")
                self.vector_store = FAISS.from_documents(
                    all_documents,
                    self.embedding_model
                )
            else:
                print("🔄 Adding to existing FAISS index...")
                self.vector_store.add_documents(all_documents)
            
            # Save the index
            self.vector_store.save_local(str(self.faiss_index_path))
            print("✅ FAISS index saved")
            
            self.documents_loaded = True
            
            return {
                'success': True,
                'num_chunks': len(all_documents),
                'num_files': len(pdf_files)
            }
            
        except Exception as e:
            print(f"❌ Error processing PDFs: {e}")
            return {'success': False, 'error': str(e)}
    
    def retrieve_context(self, query: str, top_k: int = None) -> List[str]:
        """Retrieve relevant context from vector store"""
        if top_k is None:
            top_k = config.TOP_K_RETRIEVAL
        try:
            if not self.documents_loaded or not self.vector_store:
                return []
            
            # Search in FAISS
            docs = self.vector_store.similarity_search(query, k=top_k)
            
            print(f"🔍 Retrieved {len(docs)} relevant chunks (top_k={top_k})")
            
            # Extract text content
            contexts = [doc.page_content for doc in docs]
            return contexts
            
        except Exception as e:
            print(f"❌ Error retrieving context: {e}")
            return []
    
    def generate_answer(self, query: str, context: List[str]) -> str:
        """Generate answer using Groq LLM"""
        try:
            if not self.llm:
                return "❌ LLM not configured. Please check your GROQ_API_KEY in the .env file."
            
            # Prepare context
            if context and len(context) > 0:
                context_text = "\n\n".join(context)
                has_context = True
            else:
                context_text = "No relevant context found in uploaded documents."
                has_context = False
            
            # Create hospital-specific prompt
            system_prompt = f"""You are an AI Medical Assistant for {config.APP_NAME}.

Your role:
1. Answer questions about hospital services, doctors, and medical information
2. Use the provided context from uploaded documents when available
3. Be professional, empathetic, and accurate
4. If the answer is not in the context, provide general helpful medical information
5. Always suggest booking an appointment if the user needs medical help

IMPORTANT: You are NOT booking appointments right now - just providing information.
If someone needs to book, tell them to say "I want to book an appointment"."""

            if has_context:
                prompt = f"""Based on the following information from our hospital documents, please answer the question.

Context from Documents:
{context_text}

Question: {query}

Please provide a clear, helpful answer. If the information is in the context, use it. 
If not, provide general medical guidance and suggest booking an appointment if needed."""
            else:
                prompt = f"""Question: {query}

No specific information was found in our uploaded documents about this topic.
Please provide general helpful information about this medical question.
If appropriate, suggest that the user book an appointment with a specialist."""
            
            # Generate response
            response = self.llm.invoke([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ])
            
            return response.content
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error generating RAG answer: {error_msg}")
            
            # Provide helpful error message
            if "api" in error_msg.lower() or "key" in error_msg.lower():
                return "❌ API error. Please check your GROQ_API_KEY configuration."
            elif "timeout" in error_msg.lower():
                return "⏱️ Request timed out. Please try again."
            else:
                return f"❌ Error generating answer: {error_msg}\n\nPlease try rephrasing your question or contact support."
    
    def query(self, question: str) -> str:
        """
        Main query method - retrieves context and generates answer
        
        Args:
            question: User question
            
        Returns:
            Generated answer
        """
        try:
            if not self.documents_loaded:
                return "Please upload PDF documents first to enable question answering."
            
            # Retrieve context
            context = self.retrieve_context(question)
            
            # Generate answer
            answer = self.generate_answer(question, context)
            
            return answer
            
        except Exception as e:
            return f"Error processing question: {str(e)}"
    
    def clear_database(self) -> bool:
        """Clear the FAISS vector store and reset components"""
        try:
            # Import shutil for directory removal
            import shutil
            
            # Reset memory state
            self.vector_store = None
            self.documents_loaded = False
            
            # Delete index files
            if self.faiss_index_path.exists():
                shutil.rmtree(self.faiss_index_path)
                # Re-create empty directory
                self.faiss_index_path.mkdir(exist_ok=True, parents=True)
            
            print("✅ RAG database cleared")
            return True
        except Exception as e:
            print(f"❌ Error clearing RAG database: {e}")
            return False
