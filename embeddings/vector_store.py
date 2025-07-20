import os
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter


class LaravelDocsVectorStore:
    """Handles vector store operations for Laravel documentation."""
    
    def __init__(self, model_name="text-embedding-3-small"):
        self.embeddings = OpenAIEmbeddings(model=model_name)
        self.vector_store = None
        
    def create_vector_store(self, raw_contents, chunk_size=1000, chunk_overlap=200):
        """Create vector store from raw content."""
        print(f"Processing {len(raw_contents)} documents...")
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, 
            chunk_overlap=chunk_overlap
        )
        raw_documents = [Document(page_content=content) for content in raw_contents]
        documents = text_splitter.split_documents(raw_documents)
        print(f"Split into {len(documents)} chunks.")
        
        self.vector_store = FAISS.from_documents(documents, self.embeddings)
        return self.vector_store
    
    def save_local(self, path="laravel_faiss_index"):
        """Save vector store to local storage."""
        if self.vector_store is None:
            raise ValueError("No vector store to save. Create one first.")
        
        self.vector_store.save_local(path)
        print(f"Saved FAISS index locally as '{path}'.")
    
    def load_local(self, path="laravel_faiss_index"):
        """Load vector store from local storage."""
        self.vector_store = FAISS.load_local(path, self.embeddings, allow_dangerous_deserialization=True)
        print(f"Loaded FAISS index from '{path}'.")
        return self.vector_store
    
    def similarity_search(self, query, k=3):
        """Perform similarity search on the vector store."""
        if self.vector_store is None:
            raise ValueError("No vector store loaded. Create or load one first.")
        
        results = self.vector_store.similarity_search(query, k=k)
        return results
    
    def search_and_display(self, query, k=3):
        """Search and display results in a formatted way."""
        results = self.similarity_search(query, k)
        print(f"Top {len(results)} results for query: '{query}'\n")
        
        for i, doc in enumerate(results, 1):
            print(f"Result {i}:")
            print(f"{doc.page_content[:500]}...")
            print("-" * 80)
        
        return results
