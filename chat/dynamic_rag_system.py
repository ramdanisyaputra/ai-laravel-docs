import os
from typing import List, Dict, Any, Optional, Callable
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
import json
import re


class DynamicLLMTool:
    """A tool that uses LLM for processing with optimized model selection."""
    
    def __init__(self, name: str, description: str, func: Callable, vector_store_manager, model_name: str = "gpt-3.5-turbo"):
        self.name = name
        self.description = description
        self.func = func
        self.vector_store_manager = vector_store_manager
        self.llm = ChatOpenAI(model=model_name, temperature=0.1)


class AdvancedRAGWithDynamicTools:
    """Advanced RAG system where LLM decides which tools to use dynamically."""
    
    def __init__(self, vector_store_manager, temperature=0.1):
        self.vector_store_manager = vector_store_manager
        # 🧠 Use GPT-4 for complex orchestration (deciding which tools to use)
        self.orchestrator_llm = ChatOpenAI(model="gpt-4", temperature=temperature)
        # 🎨 Use GPT-3.5-turbo for final response synthesis (cost-effective)
        self.final_llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=temperature)
        self.chat_history = ChatMessageHistory()
        
        # Create dynamic tools
        self.tools = self._create_dynamic_tools()
        
        # Create the orchestrator that decides which tools to use
        self.orchestrator = self._create_orchestrator()
        
        # Create final answerer
        self.final_answerer = self._create_final_answerer()
    
    def _create_dynamic_tools(self) -> List[DynamicLLMTool]:
        """Create tools that the LLM can choose from."""
        
        def version_search_tool(query: str) -> str:
            """Search for Laravel version information with LLM analysis."""
            try:
                # Multi-query search for version info
                searches = [
                    f"{query} version",
                    "Laravel version",
                    "release notes",
                    "upgrade guide",
                    "Laravel 12.x",
                    "Laravel 11.x",
                    "Laravel 10.x",
                    "current version"
                ]
                
                all_docs = []
                for search in searches:
                    docs = self.vector_store_manager.similarity_search(search, k=3)
                    all_docs.extend(docs)
                    if not all_docs:
                        context = "No relevant documentation found."
                    else:
                        context = "\n\n".join([f"Document {i}:\n{doc.page_content}" 
                                             for i, doc in enumerate(all_docs[:5], 1)])
                
                # LLM analysis - using GPT-3.5-turbo for version extraction (simple task)
                version_llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)
                prompt = ChatPromptTemplate.from_messages([
                    ("system", """You are a Laravel version specialist. Analyze the documentation context and extract version information.
You are master at laravel 12 please extract the version number from the context.

Context:
{context}"""),
                    ("human", "{query}")
                ])
                
                chain = prompt | version_llm | StrOutputParser()
                result = chain.invoke({"query": query, "context": context})
                
                print(f"🔍 Version Tool Result: {result[:100]}...")
                return result
                
            except Exception as e:
                return f"Error in version search: {e}"
        
        def feature_search_tool(query: str) -> str:
            """Search for Laravel feature information with LLM analysis."""
            try:
                # Multi-query search for features
                searches = [
                    f"Laravel {query}",
                    f"how to {query}",
                    f"{query} implementation",
                    f"{query} configuration",
                    f"{query} example",
                    f"{query} tutorial"
                ]
                
                all_docs = []
                for search in searches:
                    docs = self.vector_store_manager.similarity_search(search, k=3)
                    all_docs.extend(docs)
                    if not all_docs:
                        context = "No relevant documentation found."
                    else:
                        context = "\n\n".join([f"Document {i}:\n{doc.page_content}" 
                                             for i, doc in enumerate(all_docs[:5], 1)])
                
                # LLM analysis - using GPT-4 for complex feature explanations
                feature_llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)
                prompt = ChatPromptTemplate.from_messages([
                    ("system", """You are a Laravel feature specialist. Only follow the RAG (Retrieval-Augmented Generation) approach: analyze the provided documentation context and answer strictly based on it.

Provide:
- Clear explanations of how the feature works (from context only)
- Code examples (exactly as they appear in docs)
- Step-by-step implementation guides (from context only)
- Best practices and common use cases (from context only)
- Prerequisites or requirements (from context only)

Do not use outside knowledge. If the context does not contain the answer, say so.

Context:
{context}"""),
                    ("human", "{query}")
                ])
                
                chain = prompt | feature_llm | StrOutputParser()
                result = chain.invoke({"query": query, "context": context})
                
                print(f"⚙️ Feature Tool Result: {result[:100]}...")
                return result
                
            except Exception as e:
                return f"Error in feature search: {e}"
        
        def installation_search_tool(query: str) -> str:
            """Search for Laravel installation and setup information."""
            try:
                # Multi-query search for installation
                searches = [
                    "Laravel installation",
                    "install Laravel",
                    "Laravel setup",
                    "Laravel requirements",
                    "Laravel getting started",
                    f"{query} install",
                    f"{query} composer"
                ]
                
                all_docs = []
                for search in searches:
                    docs = self.vector_store_manager.similarity_search(search, k=3)
                    all_docs.extend(docs)
                
                # --- FIX: Moved this block outside the loop ---
                if not all_docs:
                    context = "No relevant documentation found."
                else:
                    # You can also de-duplicate here if you want
                    unique_docs = {doc.page_content: doc for doc in all_docs}.values()
                    context = "\n\n".join([f"Document {i}:\n{doc.page_content}" 
                                        for i, doc in enumerate(list(unique_docs)[:5], 1)])
                # --- End of Fix ---
                
                # LLM analysis - using GPT-3.5-turbo for installation instructions
                install_llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)
                prompt = ChatPromptTemplate.from_messages([
                    ("system", """You are a Laravel installation specialist. Only follow the RAG (Retrieval-Augmented Generation) approach: analyze the provided documentation context and answer strictly based on it.
Provide:
- System requirements
- Step-by-step installation instructions
- Command examples
- Common issues and solutions
- Post-installation setup steps

Do not use outside knowledge. If the context does not contain the answer, say so.

Context:
{context}"""),
                    ("human", "{query}")
                ])
                
                chain = prompt | install_llm | StrOutputParser()
                result = chain.invoke({"query": query, "context": context})
                
                print(f"📦 Installation Tool Result: {result[:100]}...")
                return result
                
            except Exception as e:
                return f"Error in installation search: {e}"
        
        def general_search_tool(query: str) -> str:
            """General Laravel documentation search with LLM analysis."""
            try:
                # Multi-query search
                searches = [
                    query,
                    f"Laravel {query}",
                    f"{query} documentation",
                    f"{query} guide"
                ]
                
                all_docs = []
                for search in searches:
                    docs = self.vector_store_manager.similarity_search(search, k=3)
                    all_docs.extend(docs)
                    if not all_docs:
                        context = "No relevant documentation found."
                    else:
                        context = "\n\n".join([f"Document {i}:\n{doc.page_content}" 
                                             for i, doc in enumerate(all_docs[:5], 1)])
                
                general_llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)
                prompt = ChatPromptTemplate.from_messages([
                    ("system", """You are a Laravel documentation specialist. Only follow the RAG (Retrieval-Augmented Generation) approach: analyze the provided documentation context and answer strictly based on it.

Provide:
- Clear, accurate information based on the documentation context only
- Code examples when available (from context only)
- Practical guidance and best practices (from context only)
- Structured, easy-to-follow responses

Do not use outside knowledge. If the context does not contain the answer, say so.

Context:
{context}"""),
                    ("human", "{query}")
                ])
                
                chain = prompt | general_llm | StrOutputParser()
                result = chain.invoke({"query": query, "context": context})
                
                print(f"📚 General Tool Result: {result[:100]}...")
                return result
                
            except Exception as e:
                return f"Error in general search: {e}"
        
        # Create tool objects with optimized model selection
        tools = [
            DynamicLLMTool(
                name="version_search",
                description="Search for Laravel version information, release notes, upgrade guides, or version-specific features",
                func=version_search_tool,
                vector_store_manager=self.vector_store_manager,
                model_name="gpt-3.5-turbo"  # Simple version extraction task
            ),
            DynamicLLMTool(
                name="feature_search",
                description="Search for specific Laravel features like middleware, routing, Eloquent, validation, authentication, etc.",
                func=feature_search_tool,
                vector_store_manager=self.vector_store_manager,
                model_name="gpt-4"  # Complex feature explanations need GPT-4
            ),
            DynamicLLMTool(
                name="installation_search",
                description="Search for ONLY Laravel installation, setup, requirements, and getting started information",
                func=installation_search_tool,
                vector_store_manager=self.vector_store_manager,
                model_name="gpt-3.5-turbo"  # Structured installation steps
            ),
            DynamicLLMTool(
                name="general_search",
                description="General Laravel documentation search for any Laravel-related topics not covered by other tools",
                func=general_search_tool,
                vector_store_manager=self.vector_store_manager,
                model_name="gpt-3.5-turbo"  # General documentation queries
            )
        ]
        
        return tools
    
    def _create_orchestrator(self) -> ChatPromptTemplate:
        """Create the orchestrator that decides which tools to use, with chat history as context."""
        tool_descriptions = "\n".join([f"- {tool.name}: {tool.description}" for tool in self.tools])
        
        system_message = """You are an intelligent orchestrator for a Laravel documentation system. Your job is to analyze user questions and decide which tools to use.

AVAILABLE TOOLS:
""" + tool_descriptions + """

INSTRUCTIONS:
1. Analyze the user's question carefully
2. Use the chat history as context to understand the user's intent and previous questions
3. Decide which tool(s) would be most helpful (you can use multiple tools)
4. Return a JSON response with the tools to use and queries for each tool

Response format:
{{
    "tools": [
        {{
            "name": "tool_name",
            "query": "specific query for this tool"
        }}
    ],
    "reasoning": "Brief explanation of why you chose these tools"
}}

Examples:
- "What version Laravel currently" → {{"tools": [{{"name": "version_search", "query": "current Laravel version"}}], "reasoning": "User wants version information"}}
- "How to use middleware" → {{"tools": [{{"name": "feature_search", "query": "middleware"}}], "reasoning": "User wants to learn about a specific feature"}}
- "How to install Laravel" → {{"tools": [{{"name": "installation_search", "query": "install Laravel"}}], "reasoning": "User wants installation guidance"}}
- "Laravel routing and middleware" → {{"tools": [{{"name": "feature_search", "query": "routing"}}, {{"name": "feature_search", "query": "middleware"}}], "reasoning": "User wants information about multiple features"}}

Respond only with valid JSON.

Chat History:
{chat_history}
"""
        return ChatPromptTemplate.from_messages([
            ("system", system_message),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}")
        ])
        
        # return ChatPromptTemplate.from_messages([
        #     ("system", system_message),
        #     ("human", "{question}")
        # ])
    
    def _create_final_answerer(self) -> ChatPromptTemplate:
        """Create the final answerer that combines tool results."""
        return ChatPromptTemplate.from_messages([
            ("system", """You are a world-class Laravel documentation assistant. Your job is to answer the user's question using ONLY the information provided in 'Tool Results' below.

INSTRUCTIONS:
- Do NOT reference the tools or mention which tool was used.
- Do NOT say "based on the information provided" or similar.
- Use ONLY the content from 'Tool Results' to answer.
- If the context does not contain the answer, say so politely.
- Provide step-by-step instructions, code examples, and practical guidance as found in the Tool Results.
- Be clear, concise, and professional.
- Format code blocks using triple backticks.
- If multiple results are provided, synthesize them into a single, coherent answer.

Tool Results:
{tool_results}

Answer the user's question using only the information above.
"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}")
        ])
    
    def chat(self, question: str, session_id: str = "default") -> str:
        """Chat with the advanced RAG system."""
        try:
            # Handle greetings
            question_lower = question.lower().strip()
            greetings = ['hi', 'hello', 'hey', 'hii', 'hai', 'sup', 'yo', 'howdy']
            
            if question_lower in greetings:
                return "Hello! I'm your advanced Laravel documentation assistant. I intelligently choose the best tools to answer your Laravel questions. Ask me anything about Laravel!"
            
            if len(question.strip()) <= 3:
                return "Please ask me a specific question about Laravel, and I'll intelligently choose the best tools to help you!"
            
            print(f"🧠 Step 1: Orchestrator analyzing question...")
            
            # Step 1: Orchestrator decides which tools to use
            orchestrator_chain = self.orchestrator | self.orchestrator_llm | StrOutputParser()
            # Pass both 'question' and 'chat_history' as required by the prompt
            orchestrator_response = orchestrator_chain.invoke({
                "question": question,
                "chat_history": self.chat_history.messages
            })
            
            print(f"🤖 Orchestrator response: {orchestrator_response}")
            
            # Parse the JSON response
            try:
                tool_plan = json.loads(orchestrator_response)
                print(f"📋 Tool plan: {tool_plan}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing error: {e}")
                # Fallback to general search
                tool_plan = {
                    "tools": [{"name": "general_search", "query": question}],
                    "reasoning": "Fallback to general search due to parsing error"
                }
            
            # Step 2: Execute the selected tools
            tool_results = []
            for tool_info in tool_plan.get("tools", []):
                tool_name = tool_info.get("name")
                tool_query = tool_info.get("query", question)
                
                print(f"🔧 Step 2: Executing tool '{tool_name}' with query: '{tool_query}'")
                
                # Find and execute the tool
                tool_found = False
                for tool in self.tools:
                    if tool.name == tool_name:
                        result = tool.func(tool_query)
                        tool_results.append(f"Tool '{tool_name}' result:\n{result}")
                        tool_found = True
                        break
                
                if not tool_found:
                    print(f"⚠️ Tool '{tool_name}' not found, using general search")
                    # Fallback to general search
                    for tool in self.tools:
                        if tool.name == "general_search":
                            result = tool.func(tool_query)
                            tool_results.append(f"Tool 'general_search' result:\n{result}")
                            break
            
            # Step 3: Combine results with final answerer
            print(f"🎨 Step 3: Combining {len(tool_results)} tool results...")
            
            combined_results = "\n\n".join(tool_results)
            
            final_chain = RunnableWithMessageHistory(
                self.final_answerer | self.final_llm | StrOutputParser(),
                self._get_session_history,
                input_messages_key="question",
                history_messages_key="chat_history",
            )
            
            response = final_chain.invoke(
                {"question": question, "tool_results": combined_results},
                config={"configurable": {"session_id": session_id}}
            )
            
            print("✅ Step 4: Final response ready!")
            return response
            
        except Exception as e:
            return f"Error in advanced RAG system: {e}"
    
    def _get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        """Get chat history for a session."""
        return self.chat_history
    
    def clear_history(self):
        """Clear chat history."""
        self.chat_history.clear()
        print("✅ Chat history cleared.")
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools."""
        return [f"{tool.name}: {tool.description}" for tool in self.tools]
    
    def display_history(self):
        """Display chat history in a formatted way."""
        messages = self.chat_history.messages
        if not messages:
            print("No chat history.")
            return
        
        print("\n" + "="*60)
        print("CHAT HISTORY")
        print("="*60)
        
        for i, message in enumerate(messages, 1):
            if isinstance(message, HumanMessage):
                print(f"\n👤 User: {message.content}")
            elif isinstance(message, AIMessage):
                print(f"\n🤖 Laravel Bot: {message.content}")
        print("\n" + "="*60)
