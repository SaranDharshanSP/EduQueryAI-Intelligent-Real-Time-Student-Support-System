
# AI-Driven Real-Time Query Management and FAQ System

### Overview
This repository implements an AI-driven query management system for large-scale online learning environments. It leverages state-of-the-art Natural Language Processing (NLP) techniques to handle student queries in real time, automate FAQ generation, and ensure scalability and responsiveness during live sessions.

### Key Features
- **Semantic Embedding**: Uses `paraphrase-mpnet-base-v2` for high-dimensional vector representation of course material.
- **Topic Clustering**: Organizes embedded content with FAISS and k-means clustering for efficient query resolution.
- **Automated FAQ Generation**: Pre-validates FAQs in various categories (in-chapter, across-chapter, application-based, out-of-context).
- **Retrieval-Augmented Generation (RAG)**: Provides accurate, low-latency responses for routine queries.
- **Query Escalation**: Escalates high-dissimilarity queries to instructors for personalized feedback.
- **Performance Metrics**:
  - **Answer Relevancy**: 88.65%
  - **Contextual Precision**: 88.25%
  - **Hallucination Rate**: 74.6%

### System Workflow
1. **Content Preparation**:
   - Upload course material (e.g., textbooks, notes).
   - Embed content and create topic clusters using FAISS indexing.
2. **Real-Time Query Handling**:
   - Embed student queries and calculate dissimilarity with FAQs.
   - Address low-dissimilarity queries automatically with RAG.
   - Flag high-dissimilarity queries for instructor review.
3. **Dynamic Feedback**:
   - Provide instructors with a dashboard to monitor unresolved queries.
   - Enable updates to the FAQ database for adaptive learning.

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/<your-repo-url>.git
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up FAISS indexing and upload course material using the provided scripts.

### Usage
- Start the query management system:
   ```bash
   python run_query_manager.py
   ```
- Access the instructor and student dashboards through the web interface.

## 🚧 Work in Progress
**Current Progress: [██████████████████----------] 60%**


### Future Enhancements
- Multilingual query handling using models like mBERT and XLM-R.
- Advanced reasoning for interdisciplinary and multi-step queries.
- Real-time content updates for evolving curricula.

---
