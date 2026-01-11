[Skip to content](#content)

[![](https://codecut.ai/wp-content/uploads/2025/01/logo_compressed-1052x394.png)](https://codecut.ai/)

* [Explore Tools](https://codecut.ai/tool-selector/)
* [Past Issues](https://codecut.ai/newsletter/)
* [Blog](https://codecut.ai/blog/)
* [Book](https://codecut.ai/production-ready-data-science/)
* [Sponsor](https://codecut.ai/sponsor/)
* [Login](https://codecut.ai/login/)

* [Explore Tools](https://codecut.ai/tool-selector/)
* [Past Issues](https://codecut.ai/newsletter/)
* [Blog](https://codecut.ai/blog/)
* [Book](https://codecut.ai/production-ready-data-science/)
* [Sponsor](https://codecut.ai/sponsor/)
* [Login](https://codecut.ai/login/)

Generic selectors

[ ]

Exact matches only

[x]

Search in title

[x]

Search in content

[x]

Post Type Selectors

[x]

[x]

Filter by Categories

[x]

About Article

[x]

Analyze Data

[x]

Archive

[x]

Best Practices

[x]

Better Outputs

[x]

Blog

[x]

Code Optimization

[x]

Code Quality

[x]

Command Line

[x]

Daily tips

[x]

Dashboard

[x]

Data Analysis & Manipulation

[x]

Data Engineer

[x]

Data Visualization

[x]

DataFrame

[x]

Delta Lake

[x]

DevOps

[x]

DuckDB

[x]

Environment Management

[x]

Feature Engineer

[x]

Git

[x]

Jupyter Notebook

[x]

LLM

[x]

LLM Tools

[x]

Machine Learning

[x]

Machine Learning & AI

[x]

Machine Learning Tools

[x]

Manage Data

[x]

MLOps

[x]

Natural Language Processing

[x]

Newsletter Archive

[x]

NumPy

[x]

Pandas

[x]

Polars

[x]

PySpark

[x]

Python Helpers

[x]

Python Tips

[x]

Python Utilities

[x]

Scrape Data

[x]

SQL

[x]

Testing

[x]

Time Series

[x]

Tools

[x]

Visualization

[x]

Visualization & Reporting

[x]

Workflow & Automation

[x]

Workflow Automation

# Build a Complete RAG System with 5 Open-Source Tools

[Home](https://codecut.ai) / [Blog](https://codecut.ai/blog/) / Build a Complete RAG System with 5 Open-Source Tools

* [August 20, 2025](https://codecut.ai/2025/08/20/)

![](https://codecut.ai/wp-content/uploads/2025/08/langchain-Ollama.png)

# Build a Complete RAG System with 5 Open-Source Tools

* ![Khuyen Tran photo](https://codecut.ai/wp-content/uploads/2025/05/khuyen_headshot.png)

  ## [Khuyen Tran](https://codecut.ai/author/khuyentran1476/ "Khuyen Tran")

## Table of Contents

* [Introduction to RAG Systems](#introduction-to-rag-systems)
* [Document Ingestion with MarkItDown](#document-ingestion-with-markitdown)
* [Intelligent Chunking with LangChain](#intelligent-chunking-with-langchain)
* [Creating Searchable Embeddings with SentenceTransformers](#creating-searchable-embeddings-with-sentencetransformers)
* [Building Your Knowledge Database with ChromaDB](#building-your-knowledge-database-with-chromadb)
* [Enhanced Answer Generation with Open-Source LLMs](#enhanced-answer-generation-with-open-source-llms)
* [Building a Simple Application with Gradio](#building-a-simple-application-with-gradio)
* [Conclusion](#conclusion)

## Introduction

Have you ever spent 30 minutes searching through Slack threads, email attachments, and shared drives just to find that one technical specification your colleague mentioned last week?

It is a common scenario that repeats daily across organizations worldwide. Knowledge workers spend valuable time searching for information that should be instantly accessible, leading to decreased productivity.

Retrieval-Augmented Generation (RAG) systems solve this problem by transforming your documents into an intelligent, queryable knowledge base. Ask questions in natural language and receive instant answers with source citations, eliminating time-consuming manual searches.

In this article, we’ll build a complete RAG pipeline that turns document collections into an AI-powered question-answering system.

## Key Takeaways

Here’s what you’ll learn:

* Convert documents with MarkItDown in 3 lines
* Chunk text intelligently using LangChain RecursiveCharacterTextSplitter
* Generate embeddings locally with SentenceTransformers model
* Store vectors in ChromaDB persistent database
* Generate answers using Ollama local LLMs
* Deploy web interface with Gradio streaming

> 💻 **Get the Code**: The complete source code and Jupyter notebook for this tutorial are available on [GitHub](https://github.com/khuyentran1401/codecut-blog/blob/main/open_source_rag_pipeline_intelligent_qa_system.ipynb). Clone it to follow along!

## Introduction to RAG Systems

RAG (Retrieval-Augmented Generation) combines document retrieval with language generation to create intelligent Q&A systems. Instead of relying solely on training data, RAG systems search through your documents to find relevant information, then use that context to generate accurate, source-backed responses.

### Environment Setup

Install the required libraries for building your RAG pipeline:

```
pip install markitdown[pdf] sentence-transformers langchain-text-splitters chromadb gradio langchain-ollama ollama
```

These libraries provide:

* **[markitdown](https://github.com/microsoft/markitdown)**: Microsoft’s document conversion tool that transforms PDFs, Word docs, and other formats into clean markdown
* **[sentence-transformers](https://github.com/UKPLab/sentence-transformers)**: Local embedding generation for converting text into searchable vectors
* **[langchain-text-splitters](https://github.com/langchain-ai/langchain)**: Intelligent text chunking that preserves semantic meaning
* **[chromadb](https://github.com/chroma-core/chroma)**: Self-hosted vector database for storing and querying document embeddings
* **[gradio](https://github.com/gradio-app/gradio)**: Web interface builder for creating user-friendly Q&A applications
* **[langchain-ollama](https://github.com/langchain-ai/langchain)**: LangChain integration for local LLM inference

Install Ollama and download a model:

```
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2
```

Next, create a project directory structure to organize your files:

```
mkdir processed_docs documents
```

These directories organize your project:

* `processed_docs`: Stores converted markdown files
* `documents`: Contains original source files (PDFs, Word docs, etc.)

Create these directories in your current working path with appropriate read/write permissions.

### Dataset Setup: Python Technical Documentation

To demonstrate the RAG pipeline, we’ll use “Think Python” by Allen Downey, a comprehensive programming guide freely available under Creative Commons.

We’ll download the Python guide and save it in the `documents` directory.

```
import requests
from pathlib import Path

# Get the file path
output_folder = "documents"
filename = "think_python_guide.pdf"
url = "https://greenteapress.com/thinkpython/thinkpython.pdf"
file_path = Path(output_folder) / filename

def download_file(url: str, file_path: Path):
    response = requests.get(url, stream=True, timeout=30)
    response.raise_for_status()
    file_path.write_bytes(response.content)

# Download the file if it doesn't exist
if not file_path.exists():
    download_file(
        url=url,
        file_path=file_path,
    )
```

Next, let’s convert this PDF into a format that our RAG system can process and search through.

## Document Ingestion with MarkItDown

RAG systems need documents in a structured format that AI models can understand and process effectively.

[MarkItDown](https://github.com/microsoft/markitdown) solves this challenge by converting any document format into clean markdown while preserving the original structure and meaning.

### Converting Your Python Guide

Start by converting the Python guide to understand how MarkItDown works:

```
from markitdown import MarkItDown

# Initialize the converter
md = MarkItDown()

# Convert the Python guide to markdown
result = md.convert(file_path)
python_guide_content = result.text_content

# Display the conversion results
print("First 300 characters:")
print(python_guide_content[:300] + "...")
```

In this code:

* `MarkItDown()` creates a document converter that handles multiple file formats automatically
* `convert()` processes the PDF and returns a result object containing the extracted text
* `text_content` provides the clean markdown text ready for processing

Output:

```
First 300 characters:
Think Python

How to Think Like a Computer Scientist

Version 2.0.17

Think Python

How to Think Like a Computer Scientist

Version 2.0.17

Allen Downey

Green Tea Press

Needham, Massachusetts

Copyright © 2012 Allen Downey.

Green Tea Press
9 Washburn Ave
Needham MA 02492

Permission is granted...
```

MarkItDown automatically detects the PDF format and extracts clean text while preserving the book’s structure, including chapters, sections, and code examples.

### Preparing Document for Processing

Now that you understand the basic conversion, let’s prepare the document content for processing. We’ll store the guide’s content with source information for later use in chunking and retrieval:

```
# Organize the converted document
processed_document = {
    'source': file_path,
    'content': python_guide_content
}

# Create a list containing our single document for consistency with downstream processing
documents = [processed_document]

# Document is now ready for chunking and embedding
print(f"Document ready: {len(processed_document['content']):,} characters")
```

Output:

```
Document ready: 460,251 characters
```

With our document successfully converted to markdown, the next step is breaking it into smaller, searchable pieces.

## Intelligent Chunking with LangChain

AI models can’t process entire documents due to limited context windows. Chunking breaks documents into smaller, searchable pieces while preserving semantic meaning.

### Understanding Text Chunking with a Simple Example

Let’s see how text chunking works with a simple document:

```
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Create a simple example that will be split
sample_text = """
Machine learning transforms data processing. It enables pattern recognition without explicit programming.

Deep learning uses neural networks with multiple layers. These networks discover complex patterns automatically.

Natural language processing combines ML with linguistics. It helps computers understand human language effectively.
"""

# Apply chunking with smaller size to demonstrate splitting
demo_splitter = RecursiveCharacterTextSplitter(
    chunk_size=150,  # Small size to force splitting
    chunk_overlap=30,
    separators=["\n\n", "\n", ". ", " ", ""],  # Split hierarchy
)

sample_chunks = demo_splitter.split_text(sample_text.strip())

print(f"Original: {len(sample_text.strip())} chars → {len(sample_chunks)} chunks")

# Show chunks
for i, chunk in enumerate(sample_chunks):
    print(f"Chunk {i+1}: {chunk}")
```

Output:

```
Original: 336 chars → 3 chunks
Chunk 1: Machine learning transforms data processing. It enables pattern recognition without explicit programming.
Chunk 2: Deep learning uses neural networks with multiple layers. These networks discover complex patterns automatically.
Chunk 3: Natural language processing combines ML with linguistics. It helps computers understand human language effectively.
```

Notice how the text splitter:

* Split the 336-character text into 3 chunks, each under the 150-character limit
* Applied 30-character overlap between adjacent chunks
* Separators prioritize semantic boundaries: paragraphs (`\n\n`) → sentences (`.`) → words () → characters

### Processing Multiple Documents at Scale

Now let’s a text splitter with larger chunks and apply it to all our converted documents:

```
# Configure the text splitter with Q&A-optimized settings
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=600,         # Optimal chunk size for Q&A scenarios
    chunk_overlap=120,      # 20% overlap to preserve context
    separators=["\n\n", "\n", ". ", " ", ""]  # Split hierarchy
)
```

Next, use the text splitter to process all our documents:

```
def process_document(doc, text_splitter):
    """Process a single document into chunks."""
    doc_chunks = text_splitter.split_text(doc["content"])
    return [{"content": chunk, "source": doc["source"]} for chunk in doc_chunks]

# Process all documents and create chunks
all_chunks = []
for doc in documents:
    doc_chunks = process_document(doc, text_splitter)
    all_chunks.extend(doc_chunks)
```

Examine how the chunking process distributed content across our documents:

```
from collections import Counter

source_counts = Counter(chunk["source"] for chunk in all_chunks)
chunk_lengths = [len(chunk["content"]) for chunk in all_chunks]

print(f"Total chunks created: {len(all_chunks)}")
print(f"Chunk length: {min(chunk_lengths)}-{max(chunk_lengths)} characters")
print(f"Source document: {Path(documents[0]['source']).name}")
```

Output:

```
Total chunks created: 1007
Chunk length: 68-598 characters
Source document: think_python_guide.pdf
```

Our text chunks are ready. Next, we’ll transform them into a format that enables intelligent similarity search.

## Creating Searchable Embeddings with SentenceTransformers

RAG systems need to understand text meaning, not just match keywords. [SentenceTransformers](https://github.com/UKPLab/sentence-transformers) converts your text into numerical vectors that capture semantic relationships, allowing the system to find truly relevant information even when exact words don’t match.

### Generate Embeddings

Let’s generate embeddings for our text chunks:

```
from sentence_transformers import SentenceTransformer

# Load Q&A-optimized embedding model (downloads automatically on first use)
model = SentenceTransformer('multi-qa-mpnet-base-dot-v1')

# Extract documents and create embeddings
documents = [chunk["content"] for chunk in all_chunks]
embeddings = model.encode(documents)

print(f"Embedding generation results:")
print(f"  - Embeddings shape: {embeddings.shape}")
print(f"  - Vector dimensions: {embeddings.shape[1]}")
```

In this code:

* `SentenceTransformer()` loads the Q&A-optimized model that converts text to 768-dimensional vectors
* `multi-qa-mpnet-base-dot-v1` is specifically trained on 215M question-answer pairs for superior Q&A performance
* `model.encode()` transforms all text chunks into numerical embeddings in a single batch operation

The output shows 1007 chunks converted to 768-dimensional vectors:

```
Embedding generation results:
  - Embeddings shape: (1007, 768)
  - Vector dimensions: 768
```

### Test Semantic Similarity

Let’s test semantic similarity by querying for Python programming concepts:

```
# Test how one query finds relevant Python programming content
from sentence_transformers import util

query = "How do you define functions in Python?"
document_chunks = [
    "Variables store data values that can be used later in your program.",
    "A function is a block of code that performs a specific task when called.",
    "Loops allow you to repeat code multiple times efficiently.",
    "Functions can accept parameters and return values to the calling code."
]

# Encode query and documents
query_embedding = model.encode(query)
doc_embeddings = model.encode(document_chunks)
```

Now we’ll calculate similarity scores and rank the results. The `util.cos_sim()` function computes cosine similarity between vectors, returning values from 0 (no similarity) to 1 (identical meaning):

```
# Calculate similarities using SentenceTransformers util
similarities = util.cos_sim(query_embedding, doc_embeddings)[0]

# Create ranked results
ranked_results = sorted(
    zip(document_chunks, similarities),
    key=lambda x: x[1],
    reverse=True
)

print(f"Query: '{query}'")
print("Document chunks ranked by relevance:")
for i, (chunk, score) in enumerate(ranked_results, 1):
    print(f"{i}. ({score:.3f}): '{chunk}'")
```

Output:

```
Query: 'How do you define functions in Python?'
Document chunks ranked by relevance:
1. (0.674): 'A function is a block of code that performs a specific task when called.'
2. (0.607): 'Functions can accept parameters and return values to the calling code.'
3. (0.461): 'Loops allow you to repeat code multiple times efficiently.'
4. (0.448): 'Variables store data values that can be used later in your program.'
```

The similarity scores demonstrate semantic understanding: function-related chunks achieve high scores (0.7+) while unrelated programming concepts score much lower (0.2-).

## Building Your Knowledge Database with ChromaDB

These embeddings demonstrate semantic search capability, but memory storage has scalability limitations. Large vector collections quickly exhaust system resources.

Vector databases provide essential production capabilities:

* **Persistent storage**: Data survives system restarts and crashes
* **Optimized indexing**: Fast similarity search using HNSW algorithms
* **Memory efficiency**: Handles millions of vectors without RAM exhaustion
* **Concurrent access**: Multiple users query simultaneously
* **Metadata filtering**: Search by document properties and attributes

[ChromaDB](https://github.com/chroma-core/chroma) delivers these features with a Python-native API that integrates seamlessly into your existing data pipeline.

### Initialize Vector Database

First, we’ll set up the ChromaDB client and create a collection to store our document vectors.

```
import chromadb

# Create persistent client for data storage
client = chromadb.PersistentClient(path="./chroma_db")

# Create collection for business documents (or get existing)
collection = client.get_or_create_collection(
    name="python_guide",
    metadata={"description": "Python programming guide"}
)

print(f"Created collection: {collection.name}")
print(f"Collection ID: {collection.id}")
```

```
Created collection: python_guide
Collection ID: 42d23900-6c2a-47b0-8253-0a9b6dad4f41
```

In this code:

* `PersistentClient(path="./chroma_db")` creates a local vector database that persists data to disk
* `get_or_create_collection()` creates a new collection or returns an existing one with the same name

### Store Documents with Metadata

Now we’ll store our document chunks with basic metadata in ChromaDB with the `add()` method.

```
# Prepare metadata and add documents to collection
metadatas = [{"document": Path(chunk["source"]).name} for chunk in all_chunks]

collection.add(
    documents=documents,
    embeddings=embeddings.tolist(), # Convert numpy array to list
    metadatas=metadatas, # Metadata for each document
    ids=[f"doc_{i}" for i in range(len(documents))], # Unique identifiers for each document
)

print(f"Collection count: {collection.count()}")
```

Output:

```
Collection count: 1007
```

The database now contains 1007 searchable document chunks with their vector embeddings. ChromaDB persists this data to disk, enabling instant queries without reprocessing documents on restart.

### Query the Knowledge Base

Let’s search the vector database using natural language questions and retrieve relevant document chunks.

```
def format_query_results(question, query_embedding, documents, metadatas):
    """Format and print the search results with similarity scores"""
    from sentence_transformers import util

    print(f"Question: {question}\n")

    for i, doc in enumerate(documents):
        # Calculate accurate similarity using sentence-transformers util
        doc_embedding = model.encode([doc])
        similarity = util.cos_sim(query_embedding, doc_embedding)[0][0].item()
        source = metadatas[i].get("document", "Unknown")

        print(f"Result {i+1} (similarity: {similarity:.3f}):")
        print(f"Document: {source}")
        print(f"Content: {doc[:300]}...")
        print()

def query_knowledge_base(question, n_results=2):
    """Query the knowledge base with natural language"""
    # Encode the query using our SentenceTransformer model
    query_embedding = model.encode([question])

    results = collection.query(
        query_embeddings=query_embedding.tolist(),
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )

    # Extract results and format them
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    format_query_results(question, query_embedding, documents, metadatas)
```

In this code:

* `collection.query()` performs vector similarity search using the question text as input
* `query_texts` accepts a list of natural language questions for batch processing
* `n_results` limits the number of most similar documents returned
* `include` specifies which data to return: document text, metadata, and similarity distances

Let’s test the query function with a question:

```
query_knowledge_base("How do if-else statements work in Python?")
```

Output:

```
Question: How do if-else statements work in Python?

Result 1 (similarity: 0.636):
Document: think_python_guide.pdf
Content: 5.6 Chained conditionals

Sometimes there are more than two possibilities and we need more than two branches.
One way to express a computation like that is a chained conditional:

if x < y:
print

’

elif x > y:
’

print

x is less than y

’

x is greater than y

’

else:

print

’

x and y are equa...

Result 2 (similarity: 0.605):
Document: think_python_guide.pdf
Content: 5. An unclosed opening operator ((, {, or [) makes Python continue with the next line
as part of the current statement. Generally, an error occurs almost immediately in the
next line.

6. Check for the classic = instead of == inside a conditional.

7. Check the indentation to make sure it lines up the...
```

The search finds relevant content with strong similarity scores (0.636 and 0.605).

## Enhanced Answer Generation with Open-Source LLMs

Vector similarity search retrieves related content, but the results may be scattered across multiple chunks without forming a complete answer.

LLMs solve this by weaving retrieved context into unified responses that directly address user questions.

In this section, we’ll integrate [Ollama](https://github.com/ollama/ollama)‘s local LLMs with our vector search to generate coherent answers from retrieved chunks.

### Answer Generation Implementation

First, set up the components for LLM-powered answer generation:

```
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate

# Initialize the local LLM
llm = OllamaLLM(model="llama3.2:latest", temperature=0.1)
```

Next, create a focused prompt template for technical documentation queries:

```
prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template="""You are a Python programming expert. Based on the provided documentation, answer the question clearly and accurately.

Documentation:
{context}

Question: {question}

Answer (be specific about syntax, keywords, and provide examples when helpful):"""
)

# Create the processing chain
chain = prompt_template | llm
```

Create a function to retrieve relevant context given a question:

```
def retrieve_context(question, n_results=5):
    """Retrieve relevant context using embeddings"""
    query_embedding = model.encode([question])
    results = collection.query(
        query_embeddings=query_embedding.tolist(),
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )

    documents = results["documents"][0]
    context = "\n\n---SECTION---\n\n".join(documents)
    return context, documents

def get_llm_answer(question, context):
    """Generate answer using retrieved context"""
    answer = chain.invoke(
        {
            "context": context[:2000],
            "question": question,
        }
    )
    return answer

def format_response(question, answer, source_chunks):
    """Format the final response with sources"""
    response = f"**Question:** {question}\n\n"
    response += f"**Answer:** {answer}\n\n"
    response += "**Sources:**\n"

    for i, chunk in enumerate(source_chunks[:3], 1):
        preview = chunk[:100].replace("\n", " ") + "..."
        response += f"{i}. {preview}\n"

    return response

def enhanced_query_with_llm(question, n_results=5):
    """Query function combining retrieval with LLM generation"""
    context, documents = retrieve_context(question, n_results)
    answer = get_llm_answer(question, context)
    return format_response(question, answer, documents)
```

### Testing Enhanced Answer Generation

Let’s test the enhanced system with our challenging question:

```
# Test the enhanced query system
enhanced_response = enhanced_query_with_llm("How do if-else statements work in Python?")
print(enhanced_response)
```

Output:

```
**Question:** How do if-else statements work in Python?

**Answer:** If-else statements in Python are used for conditional execution of code. Here's a breakdown of how they work:

**Syntax**

The basic syntax of an if-else statement is as follows:
```text
if condition:
    # code to execute if condition is true
elif condition2:
    # code to execute if condition1 is false and condition2 is true
else:
    # code to execute if both conditions are false
```text
**Keywords**

The keywords used in an if-else statement are:

* `if`: used to check a condition
* `elif` (short for "else if"): used to check another condition if the first one is false
* `else`: used to specify code to execute if all conditions are false

**How it works**

Here's how an if-else statement works:

1. The interpreter evaluates the condition inside the `if` block.
2. If the condition is true, the code inside the `if` block is executed.
3. If the condition is false, the interpreter moves on to the next line and checks the condition in the `elif` block.
4. If the condition in the `elif` block is true, the code inside that block is executed.
5. If both conditions are false, the interpreter executes the code inside the `else` block.

**Sources:**
1. 5.6 Chained conditionals  Sometimes there are more than two possibilities and we need more than two ...
2. 5. An unclosed opening operator ((, {, or [) makes Python continue with the next line as part of the c...
3. if x == y:  print  else:  ’  x and y are equal  ’  if x < y:  44  Chapter 5. Conditionals and recur...
```

Notice how the LLM organizes multiple chunks into logical sections with syntax examples and step-by-step explanations. This transformation turns raw retrieval into actionable programming guidance.

### Streaming Interface Implementation

Users now expect the real-time streaming experience from ChatGPT and Claude. Static responses that appear all at once feel outdated and create an impression of poor performance.

Token-by-token streaming bridges this gap by creating the familiar typing effect that signals active processing.

To implement a streaming interface, we’ll use the `chain.stream()` method to generate tokens one at a time.

```
def stream_llm_answer(question, context):
    """Stream LLM answer generation token by token"""
    for chunk in chain.stream({
        "context": context[:2000],
        "question": question,
    }):
        yield getattr(chunk, "content", str(chunk))
```

Let’s see how streaming works by combining our modular functions:

```
import time

# Test the streaming functionality
question = "What are Python loops?"
context, documents = retrieve_context(question, n_results=3)

print("Question:", question)
print("Answer: ", end="", flush=True)

# Stream the answer token by token
for token in stream_llm_answer(question, context):
    print(token, end="", flush=True)
    time.sleep(0.05)  # Simulate real-time typing effect
```

Output:

```
Question: What are Python loops?
Answer: Python → loops → are → structures → that → repeat → code...

[Each token appears with typing animation]
Final: "Python loops are structures that repeat code blocks."
```

This creates the familiar ChatGPT-style typing animation where tokens appear progressively.

## Building a Simple Application with Gradio

Now that we have a complete RAG system with enhanced answer generation, let’s make it accessible through a web interface.

Your RAG system needs an intuitive interface that non-technical users can access easily. [Gradio](https://github.com/gradio-app/gradio) provides this solution with:

* **Zero web development required**: Create interfaces directly from Python functions
* **Automatic UI generation**: Input fields and buttons generated automatically
* **Instant deployment**: Launch web apps with a single line of code

### Interface Function

Let’s create the complete Gradio interface that combines the functions we’ve built into a streaming RAG system:

```
import gradio as gr

def rag_interface(question):
    """Gradio interface reusing existing format_response function"""
    if not question.strip():
        yield "Please enter a question."
        return

    # Use modular retrieval and streaming
    context, documents = retrieve_context(question, n_results=5)

    response_start = f"**Question:** {question}\n\n**Answer:** "
    answer = ""

    # Stream the answer progressively
    for token in stream_llm_answer(question, context):
        answer += token
        yield response_start + answer

    # Use existing formatting function for final response
    yield format_response(question, answer, documents)
```

### Application Setup and Launch

Now, we’ll configure the Gradio web interface with sample questions and launch the application for user access.

```
# Create Gradio interface with streaming support
demo = gr.Interface(
    fn=rag_interface,
    inputs=gr.Textbox(
        label="Ask a question about Python programming",
        placeholder="How do if-else statements work in Python?",
        lines=2,
    ),
    outputs=gr.Markdown(label="Answer"),
    title="Intelligent Document Q&A System",
    description="Ask questions about Python programming concepts and get instant answers with source citations.",
    examples=[
        "How do if-else statements work in Python?",
        "What are the different types of loops in Python?",
        "How do you handle errors in Python?",
    ],
    allow_flagging="never",
)

# Launch the interface with queue enabled for streaming
if __name__ == "__main__":
    demo.queue().launch(share=True)
```

In this code:

* `gr.Interface()` creates a clean web application with automatic UI generation
* `fn` specifies the function called when users submit questions (includes streaming output)
* `inputs`/`outputs` define UI components (textbox for questions, markdown for formatted answers)
* `examples` provides clickable sample questions that demonstrate system capabilities
* `demo.queue().launch(share=True)` enables streaming output and creates both local and public URLs

Running the application produces the following output:

```
* Running on local URL:  http://127.0.0.1:7861
* Running on public URL: https://bb9a9fc06531d49927.gradio.live
```

Test the interface locally or share the public URL to demonstrate your RAG system’s capabilities.

![Gradio Interface](https://codecut.ai/wp-content/uploads/2025/08/gradio_demo.gif)

The public URL expires in 72 hours. For persistent access, deploy to Hugging Face Spaces:

```
gradio deploy
```

You now have a complete, streaming-enabled RAG system ready for production use with real-time token generation and source citations.

## Conclusion

In this article, we’ve built a complete RAG pipeline that turns your documents into an AI-powered question-answering system.

We’ve used the following tools:

* MarkItDown for document conversion
* LangChain for text chunking and embedding generation
* ChromaDB for vector storage
* Ollama for local LLM inference
* Gradio for web interface

Since all of these tools are open-source, you can easily deploy this system in your own infrastructure.

> 📚 For comprehensive production deployment practices including configuration management, logging, and data validation, check out [Production-Ready Data Science](https://codecut.ai/production-ready-data-science/).

The best way to learn is to build, so go ahead and try it out!

## Related Tutorials

* **Alternative Vector Database**: [Implement Semantic Search in Postgres Using pgvector and Ollama](https://codecut.ai/semantic-search-postgres-pgvector-ollama/) for PostgreSQL-based vector storage
* **Advanced Document Processing**: [Transform Any PDF into Searchable AI Data with Docling](https://codecut.ai/docling-pdf-rag-document-processing/) for specialized PDF parsing and RAG optimization
* **LangChain Fundamentals**: [Run Private AI Workflows with LangChain and Ollama](https://codecut.ai/private-ai-workflows-langchain-ollama/) for comprehensive LangChain and Ollama integration guide

---

> 📚 **Want to go deeper?** Learning new techniques is the easy part. Knowing how to structure, test, and deploy them is what separates side projects from real work. My book shows you how to build data science projects that actually make it to production. [Get the book →](https://codecut.ai/production-ready-data-science/?utm_source=blog&utm_medium=article&utm_campaign=book_cta_footer)

Favorite

## Related Posts

[![](https://codecut.ai/wp-content/uploads/2025/12/yellowbrick.png)](https://codecut.ai/yellowbrick-machine-learning-visualization/)

[Visualize Machine Learning Results with Yellowbrick](https://codecut.ai/yellowbrick-machine-learning-visualization/)

December 21, 2025

[![](https://codecut.ai/wp-content/uploads/2025/12/great_tables.png)](https://codecut.ai/great-tables-python/)

[Great Tables: Publication-Ready Tables from Polars and Pandas DataFrames](https://codecut.ai/great-tables-python/)

December 10, 2025

[![](https://codecut.ai/wp-content/uploads/2025/12/dictionary.png)](https://codecut.ai/hidden-cost-python-dictionaries-safer-alternatives/)

[The Hidden Cost of Python Dictionaries (And 3 Safer Alternatives)](https://codecut.ai/hidden-cost-python-dictionaries-safer-alternatives/)

December 5, 2025

### Leave a Comment [Cancel Reply](/open-source-rag-pipeline-intelligent-qa-system/#respond)

Your email address will not be published. Required fields are marked \*

Type here..

Name

Email

Website

[ ]  Save my name, email, and website in this browser for the next time I comment.

Δ

#### Stay up-to-date with data skills using CodeCut

CodeCut is a platform that offers short and visually appealing code snippets related to data science, data analysis, data engineering, and Python programming.

##### Drop a line

khuyentran@codecut.ai

##### [Get in touch](https://codecut.ai/contact-us-page-new/)

I’d love to connect with you!

[Linkedin-in](https://www.linkedin.com/in/khuyen-tran-1ab926151/)

[Twitter](https://twitter.com/KhuyenTran16)

[Youtube](https://www.youtube.com/%40datasciencesimplified)

##### Follow Us on Social Media

Copyright © 2025 Code Cut - All rights reserved.

0

0

Your Cart

Your cart is empty

Continue Shopping

Scroll to Top

## Work with Khuyen Tran

Enter Your Total Budget

Please explain the goals of you campaign

Why Do you want to collaborate with Khuyen Tran

Add date preferences

Enter your contact details

Submit

## Work with Khuyen Tran
