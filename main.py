#!/usr/bin/env python3
"""
Advanced Laravel Documentation RAG System
This implements proper RAG with dynamic LLM tool selection
"""

import os
import sys
sys.path.append('.')

from tools.tools import get_laravel_docs
from embeddings.vector_store import LaravelDocsVectorStore
from chat.dynamic_rag_system import AdvancedRAGWithDynamicTools

def main():
    """Main function - directly start the advanced RAG chat."""
    print("🚀 Advanced Laravel Documentation RAG System")
    print("=" * 60)
    
    # Load or create vector store
    try:
        vector_store = LaravelDocsVectorStore()
        
        # Try to load existing vector store
        try:
            vector_store.load_local()
            print("✅ Vector store loaded successfully!")
        except Exception as e:
            print("⚠️ Vector store not found or corrupted. Creating new one...")
            
            # Create new vector store
            print("📥 Fetching Laravel documentation...")
            docs = get_laravel_docs()
            
            if not docs:
                print("❌ No documentation retrieved. Please check your API key and connection.")
                return
            
            print(f"✅ Retrieved {len(docs)} documents")
            
            # Create vector store
            print("🔮 Creating vector store...")
            vector_store.create_vector_store(docs)
            
            # Save vector store
            print("💾 Saving vector store...")
            vector_store.save_local()
            
            print("✅ Vector store created and saved successfully!")
            
    except Exception as e:
        print(f"❌ Error with vector store: {e}")
        return
    
    # Create advanced chatbot
    try:
        chatbot = AdvancedRAGWithDynamicTools(vector_store)
        print("✅ Advanced RAG with Dynamic Tools initialized!")
    except Exception as e:
        print(f"❌ Error initializing chatbot: {e}")
        return
    
    print("\n🤖 Advanced Laravel Bot: Hello! I'm your advanced Laravel documentation assistant.")
    print("I use intelligent tool selection where the LLM DECIDES which tools to use!")
    print("Ask me anything about Laravel - I'll automatically choose the best tools!")
    print("Type 'help' for commands, 'tools' to see available tools, 'quit' or 'exit' to quit.")
    
    while True:
        user_input = input("\n👤 You: ").strip()
        
        if not user_input:
            continue
        
        if user_input.lower() in ['quit', 'exit']:
            print("👋 Goodbye!")
            break
        elif user_input.lower() == 'help':
            print("\n📋 Available commands:")
            print("• help - Show this help message")
            print("• tools - Show available tools")
            print("• history - Show chat history")
            print("• clear - Clear chat history")
            print("• quit or exit - Exit chat")
            continue
        elif user_input.lower() == 'tools':
            print("\n🛠️  Available specialized tools:")
            tools = chatbot.get_available_tools()
            for i, tool in enumerate(tools, 1):
                print(f"{i}. {tool}")
            print("\n🧠 The LLM automatically chooses the best tools for your question!")
            continue
        elif user_input.lower() == 'history':
            chatbot.display_history()
            continue
        elif user_input.lower() == 'clear':
            chatbot.clear_history()
            continue
        
        try:
            # Use the advanced RAG system with LLM tools
            response = chatbot.chat(user_input)
            print(f"\n🤖 Laravel Bot: {response}")
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Please try again or type 'help' for assistance.")

if __name__ == "__main__":
    main()
