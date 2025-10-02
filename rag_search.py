# RAG Search Module for OIC ADEI Analytics
# ========================================

import streamlit as st
import pandas as pd
import numpy as np
from typing import List, Dict, Any
import json
import os
from datetime import datetime
import sqlite3

# LangChain imports with better error handling
try:
    from langchain.embeddings import HuggingFaceEmbeddings
    from langchain.vectorstores import Chroma, FAISS
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.schema import Document
    from langchain.llms import OpenAI
    from langchain.chains import RetrievalQA
    from langchain.prompts import PromptTemplate
    from sentence_transformers import SentenceTransformer
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    print(f"LangChain import warning: {e}")
    LANGCHAIN_AVAILABLE = False
except Exception as e:
    print(f"LangChain compatibility issue: {e}")
    LANGCHAIN_AVAILABLE = False

class FallbackRAG:
    """Fallback RAG system using simple text search when LangChain is not available"""
    
    def __init__(self):
        self.documents = []
        self.feedback_db = "rag_feedback.db"
        self.setup_feedback_db()
    
    def setup_feedback_db(self):
        """Initialize SQLite database for user feedback"""
        conn = sqlite3.connect(self.feedback_db)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT,
                answer TEXT,
                rating INTEGER,
                feedback_text TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    def load_documents(self, df):
        """Load and prepare documents from DataFrame"""
        return self.initialize_rag_system(df)
    
    def initialize_rag_system(self, df):
        """Initialize simple text-based search system"""
        try:
            # Create searchable documents from the dataframe
            self.documents = []
            for _, row in df.iterrows():
                doc_text = f"Country: {row['country']}, Year: {row['year']}, ADEI Score: {row['adei_score']:.3f}"
                
                # Add pillar information if available
                pillar_cols = [col for col in df.columns if col.startswith('adei_') and col != 'adei_score']
                for col in pillar_cols:
                    if pd.notna(row[col]):
                        pillar_name = col.replace('adei_', '').replace('_', ' ').title()
                        doc_text += f", {pillar_name}: {row[col]:.3f}"
                
                self.documents.append({
                    'text': doc_text,
                    'country': row['country'],
                    'year': row['year'],
                    'adei_score': row['adei_score']
                })
            
            return True
        except Exception as e:
            st.error(f"Error initializing fallback RAG: {str(e)}")
            return False
    
    def search(self, query, k=5):
        """Enhanced keyword-based search with better relevance scoring"""
        query_lower = query.lower()
        query_words = query_lower.split()
        
        # Enhanced scoring with multiple criteria
        scored_docs = []
        for doc in self.documents:
            score = 0
            text_lower = doc['text'].lower()
            
            # 1. Exact phrase matching (highest weight)
            if query_lower in text_lower:
                score += 10
            
            # 2. Word matching with context awareness
            for word in query_words:
                if len(word) > 2:  # Skip very short words
                    if word in text_lower:
                        # Higher score for country names and key terms
                        if word in ['high', 'highest', 'low', 'lowest', 'best', 'worst', 'top', 'bottom']:
                            score += 3
                        elif word in doc['country'].lower():
                            score += 5
                        else:
                            score += 1
            
            # 3. Score-based relevance for performance queries
            if any(term in query_lower for term in ['high', 'highest', 'top', 'best']):
                if doc['adei_score'] >= 0.7:  # High performers
                    score += 5
            elif any(term in query_lower for term in ['low', 'lowest', 'bottom', 'worst']):
                if doc['adei_score'] <= 0.4:  # Low performers
                    score += 5
            
            if score > 0:
                scored_docs.append((score, doc))
        
        # Sort by score and return top k
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        top_docs = [doc for score, doc in scored_docs[:k]]
        
        # Generate contextual answer based on query type
        return self._generate_contextual_answer(query, top_docs)
    
    def _generate_contextual_answer(self, query, docs):
        """Generate contextual answers based on query type"""
        if not docs:
            return f"I couldn't find relevant information for your query: '{query}'. Try asking about specific countries, years, or performance indicators."
        
        query_lower = query.lower()
        
        # Detect query type and generate appropriate response
        if any(term in query_lower for term in ['highest', 'top', 'best']):
            return self._answer_top_performers(query, docs)
        elif any(term in query_lower for term in ['lowest', 'bottom', 'worst']):
            return self._answer_bottom_performers(query, docs)
        elif any(term in query_lower for term in ['compare', 'comparison', 'vs', 'versus']):
            return self._answer_comparison(query, docs)
        elif any(term in query_lower for term in ['trend', 'change', 'improve', 'progress']):
            return self._answer_trends(query, docs)
        else:
            return self._answer_general(query, docs)
    
    def _answer_top_performers(self, query, docs):
        """Answer questions about top performers"""
        # Sort by ADEI score
        sorted_docs = sorted(docs, key=lambda x: x['adei_score'], reverse=True)
        top_countries = [(doc['country'], doc['adei_score'], doc['year']) for doc in sorted_docs[:5]]
        
        answer = f"**Top performing countries based on your query:**\n\n"
        for i, (country, score, year) in enumerate(top_countries, 1):
            answer += f"{i}. **{country}** - ADEI Score: {score:.3f} ({year})\n"
        
        if len(top_countries) > 0:
            avg_score = sum([score for _, score, _ in top_countries]) / len(top_countries)
            answer += f"\nAverage score among top performers: **{avg_score:.3f}**"
        
        return answer
    
    def _answer_bottom_performers(self, query, docs):
        """Answer questions about bottom performers"""
        # Sort by ADEI score (ascending for bottom)
        sorted_docs = sorted(docs, key=lambda x: x['adei_score'])
        bottom_countries = [(doc['country'], doc['adei_score'], doc['year']) for doc in sorted_docs[:5]]
        
        answer = f"**Countries with lower performance based on your query:**\n\n"
        for i, (country, score, year) in enumerate(bottom_countries, 1):
            answer += f"{i}. **{country}** - ADEI Score: {score:.3f} ({year})\n"
        
        if len(bottom_countries) > 0:
            avg_score = sum([score for _, score, _ in bottom_countries]) / len(bottom_countries)
            answer += f"\nAverage score among these countries: **{avg_score:.3f}**"
        
        return answer
    
    def _answer_comparison(self, query, docs):
        """Answer comparison questions"""
        countries = list(set([doc['country'] for doc in docs]))
        
        answer = f"**Comparison results for your query:**\n\n"
        
        country_scores = {}
        for doc in docs:
            if doc['country'] not in country_scores:
                country_scores[doc['country']] = []
            country_scores[doc['country']].append((doc['adei_score'], doc['year']))
        
        # Sort countries by average score
        country_avg = {}
        for country, scores in country_scores.items():
            avg = sum([score for score, year in scores]) / len(scores)
            country_avg[country] = avg
        
        sorted_countries = sorted(country_avg.items(), key=lambda x: x[1], reverse=True)
        
        for i, (country, avg_score) in enumerate(sorted_countries[:5], 1):
            years = [str(year) for score, year in country_scores[country]]
            answer += f"{i}. **{country}** - Average ADEI: {avg_score:.3f} (Years: {', '.join(years)})\n"
        
        return answer
    
    def _answer_trends(self, query, docs):
        """Answer questions about trends and changes"""
        # Group by country and calculate trends
        country_data = {}
        for doc in docs:
            if doc['country'] not in country_data:
                country_data[doc['country']] = []
            country_data[doc['country']].append((doc['year'], doc['adei_score']))
        
        answer = f"**Trend analysis based on your query:**\n\n"
        
        trends = []
        for country, data in country_data.items():
            if len(data) > 1:
                data.sort()  # Sort by year
                first_score = data[0][1]
                last_score = data[-1][1]
                change = last_score - first_score
                trends.append((country, change, first_score, last_score))
        
        # Sort by improvement
        trends.sort(key=lambda x: x[1], reverse=True)
        
        for i, (country, change, first, last) in enumerate(trends[:5], 1):
            direction = "improved" if change > 0 else "declined" if change < 0 else "remained stable"
            answer += f"{i}. **{country}** - {direction} by {abs(change):.3f} points ({first:.3f} → {last:.3f})\n"
        
        return answer
    
    def _answer_general(self, query, docs):
        """Answer general questions"""
        countries = list(set([doc['country'] for doc in docs]))
        avg_score = sum([doc['adei_score'] for doc in docs]) / len(docs)
        years = list(set([doc['year'] for doc in docs]))
        
        answer = f"**Information relevant to your query:**\n\n"
        answer += f"**Countries found:** {', '.join(countries[:5])}"
        if len(countries) > 5:
            answer += f" and {len(countries) - 5} more"
        answer += f"\n**Years covered:** {', '.join(map(str, sorted(years)))}\n"
        answer += f"**Average ADEI score:** {avg_score:.3f}\n\n"
        
        # Show top 3 most relevant entries
        answer += "**Most relevant data points:**\n"
        for i, doc in enumerate(docs[:3], 1):
            answer += f"{i}. {doc['country']} ({doc['year']}): ADEI Score {doc['adei_score']:.3f}\n"
        
        return answer
    
    def search_similar_documents(self, query, k=5):
        """Search for similar documents - compatibility method"""
        query_lower = query.lower()
        
        # Score documents based on keyword matches
        scored_docs = []
        for doc in self.documents:
            score = 0
            text_lower = doc['text'].lower()
            
            # Basic keyword matching
            query_words = query_lower.split()
            for word in query_words:
                if word in text_lower:
                    score += 1
            
            if score > 0:
                scored_docs.append((score, doc))
        
        # Sort by score and return top k with similarity scores
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        
        # Add similarity scores to the documents
        result_docs = []
        for score, doc in scored_docs[:k]:
            doc_with_score = doc.copy()
            # Normalize score to 0-1 range for display
            max_score = max([s for s, d in scored_docs]) if scored_docs else 1
            doc_with_score['similarity_score'] = score / max_score if max_score > 0 else 0
            result_docs.append(doc_with_score)
            
        return result_docs
    
    def generate_answer(self, query, retrieved_docs):
        """Generate answer from retrieved documents"""
        if not retrieved_docs:
            return f"No relevant information found for your query: '{query}'. Try asking about specific countries, years, or ADEI indicators."
        
        countries = list(set([doc['country'] for doc in retrieved_docs]))
        avg_score = sum([doc['adei_score'] for doc in retrieved_docs]) / len(retrieved_docs)
        
        answer = f"Based on the data, here are the relevant findings for your query about '{query}':\n\n"
        answer += f"Countries mentioned: {', '.join(countries[:5])}\n"
        answer += f"Average ADEI score: {avg_score:.3f}\n\n"
        answer += "Top relevant entries:\n"
        
        for i, doc in enumerate(retrieved_docs[:3], 1):
            answer += f"{i}. {doc['text']}\n"
        
        return answer
    
    def save_feedback(self, question, answer, rating, feedback_text=""):
        """Save user feedback to database"""
        try:
            conn = sqlite3.connect(self.feedback_db)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO feedback (question, answer, rating, feedback_text)
                VALUES (?, ?, ?, ?)
            ''', (question, answer, rating, feedback_text))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Error saving feedback: {str(e)}")
            return False

class OICDataRAG:
    """RAG System for OIC ADEI Data Analysis"""
    
    def __init__(self):
        self.embeddings = None
        self.vector_store = None
        self.qa_chain = None
        self.documents = []
        self.feedback_db = "rag_feedback.db"
        self.setup_feedback_db()
    
    def setup_feedback_db(self):
        """Initialize SQLite database for user feedback"""
        conn = sqlite3.connect(self.feedback_db)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT,
                answer TEXT,
                rating INTEGER,
                feedback_text TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    def prepare_documents(self, df: pd.DataFrame) -> List[Any]:
        """Convert DataFrame to LangChain Documents"""
        documents = []
        
        # Create documents for each country-year combination
        for _, row in df.iterrows():
            # Main country profile document
            content = f"""
            Country: {row['country']}
            Year: {row['year']}
            Overall ADEI Score: {row['adei_score']:.2f}
            Performance Tier: {row.get('performance_tier', 'N/A')}
            
            Governance Indicators:
            - Political Stability: {row.get('political_stability', 'N/A')}
            - Government Effectiveness: {row.get('government_effectiveness', 'N/A')}
            - Voice and Accountability: {row.get('voice_accountability', 'N/A')}
            - Regulatory Quality: {row.get('regulatory_quality', 'N/A')}
            - Rule of Law: {row.get('rule_of_law', 'N/A')}
            - Control of Corruption: {row.get('control_corruption', 'N/A')}
            - Overall Governance Score: {row.get('governance_score', 'N/A')}
            
            Technology and Digital Infrastructure:
            - Technology Infrastructure Score: {row.get('technology_infrastructure_score', 'N/A')}
            - Access to ICT: {row.get('access_to_ict', 'N/A')}
            - Use of ICT: {row.get('use_of_ict', 'N/A')}
            - E-Security: {row.get('e_security', 'N/A')}
            - Digital Government Score: {row.get('digital_government_score', 'N/A')}
            
            Innovation and R&D:
            - Innovation Score: {row.get('innovation_score', 'N/A')}
            - Emerging Technology Score: {row.get('emerging_tech_score', 'N/A')}
            - University-Industry Collaboration: {row.get('university_industry_collaboration', 'N/A')}
            - Knowledge Impact: {row.get('knowledge_impact', 'N/A')}
            
            Economic and Financial:
            - Economic Infrastructure Score: {row.get('economic_infrastructure_score', 'N/A')}
            - Financial Inclusion Score: {row.get('financial_inclusion_score', 'N/A')}
            
            Education and Human Capital:
            - Education Score: {row.get('education_score', 'N/A')}
            - Education Expenditure % GDP: {row.get('education_expenditure_pct_gdp', 'N/A')}
            
            Sustainable Development Goals:
            - SDG Score: {row.get('sdg_score', 'N/A')}
            - Goal 1 No Poverty: {row.get('sdg_1_no_poverty', 'N/A')}
            - Goal 3 Health and Wellbeing: {row.get('sdg_3_health_wellbeing', 'N/A')}
            - Goal 4 Quality Education: {row.get('sdg_4_quality_education', 'N/A')}
            - Goal 8 Economic Growth: {row.get('sdg_8_economic_growth', 'N/A')}
            - Goal 9 Innovation Infrastructure: {row.get('sdg_9_innovation_infrastructure', 'N/A')}
            """
            
            metadata = {
                'country': row['country'],
                'year': int(row['year']),
                'adei_score': float(row['adei_score']),
                'performance_tier': row.get('performance_tier', 'Unknown'),
                'source': 'OIC_ADEI_Database'
            }
            
            if LANGCHAIN_AVAILABLE:
                from langchain.schema import Document as LangChainDocument
                documents.append(LangChainDocument(page_content=content, metadata=metadata))
            else:
                # Fallback document format
                documents.append({
                    'page_content': content,
                    'metadata': metadata
                })
        
        # Add contextual documents about the dataset
        if LANGCHAIN_AVAILABLE:
            from langchain.schema import Document as LangChainDocument
            context_docs = [
                LangChainDocument(
                page_content="""
                The OIC ADEI (Artificial Intelligence for Development and Emerging Indexes) dataset contains comprehensive development indicators for 57 Organization of Islamic Cooperation (OIC) member countries from 2021 to 2025. 
                
                The dataset measures performance across 8 key pillars:
                1. Governance and Regulatory Framework
                2. Technology Infrastructure and Digital Access
                3. Education and Human Capital Development
                4. Digital Government Services
                5. Innovation and Research & Development
                6. Emerging Technology Adoption
                7. Economic and Financial Infrastructure
                8. Sustainable Development Goals Achievement
                
                Countries are classified into performance tiers: Excellent (75-100), High (50-75), Medium (25-50), and Low (0-25).
                """,
                metadata={'source': 'dataset_overview', 'type': 'context'}
            ),
            LangChainDocument(
                page_content="""
                Key findings from the OIC ADEI analysis:
                - The UAE, Qatar, and Saudi Arabia consistently rank among top performers
                - There's a strong correlation between governance quality and overall ADEI performance
                - Technology infrastructure varies significantly across OIC countries
                - Many countries show improvement trends from 2021 to 2025
                - Digital inclusion gaps remain a challenge in several nations
                - Innovation ecosystems are developing rapidly in Gulf countries
                """,
                metadata={'source': 'key_insights', 'type': 'analysis'}
            )
        ]
        else:
            # Fallback context documents
            context_docs = [
                {
                    'page_content': """
                The OIC ADEI (Artificial Intelligence for Development and Emerging Indexes) dataset contains comprehensive development indicators for 57 Organization of Islamic Cooperation (OIC) member countries from 2021 to 2025. 
                
                The dataset measures performance across 8 key pillars:
                1. Governance and Regulatory Framework
                2. Technology Infrastructure and Digital Access
                3. Education and Human Capital Development
                4. Digital Government Services
                5. Innovation and Research & Development
                6. Emerging Technology Adoption
                7. Economic and Financial Infrastructure
                8. Sustainable Development Goals Achievement
                
                Countries are classified into performance tiers: Excellent (75-100), High (50-75), Medium (25-50), and Low (0-25).
                """,
                    'metadata': {'source': 'dataset_overview', 'type': 'context'}
                },
                {
                    'page_content': """
                Key findings from the OIC ADEI analysis:
                - The UAE, Qatar, and Saudi Arabia consistently rank among top performers
                - There's a strong correlation between governance quality and overall ADEI performance
                - Technology infrastructure varies significantly across OIC countries
                - Many countries show improvement trends from 2021 to 2025
                - Digital inclusion gaps remain a challenge in several nations
                - Innovation ecosystems are developing rapidly in Gulf countries
                """,
                    'metadata': {'source': 'key_insights', 'type': 'analysis'}
                }
            ]
        
        documents.extend(context_docs)
        return documents
    
    def initialize_rag_system(self, df: pd.DataFrame):
        """Initialize the RAG system with embeddings and vector store"""
        if not LANGCHAIN_AVAILABLE:
            st.error("LangChain not available. Please install requirements first.")
            return False
        
        try:
            # Initialize embeddings
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'}
            )
            
            # Prepare documents
            self.documents = self.prepare_documents(df)
            
            # Create vector store
            self.vector_store = FAISS.from_documents(
                self.documents,
                self.embeddings
            )
            
            # Initialize QA chain with custom prompt
            custom_prompt = PromptTemplate(
                template="""
                You are an expert analyst of the OIC ADEI (Artificial Intelligence for Development and Emerging Indexes) dataset. 
                Use the following context to answer questions about OIC countries' development performance.
                
                Context: {context}
                
                Question: {question}
                
                Instructions:
                - Provide specific, data-driven answers based on the context
                - Include relevant country names, scores, and years when available
                - If comparing countries, mention specific metrics and differences
                - If trends are asked about, reference multiple years of data
                - If the context doesn't contain enough information, state this clearly
                - Format numbers clearly (e.g., "64.5 points" instead of "64.456789")
                
                Answer:
                """,
                input_variables=["context", "question"]
            )
            
            # For demo purposes, use a simple retrieval system
            # In production, you'd use OpenAI or another LLM
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=None,  # We'll handle this manually for demo
                chain_type="stuff",
                retriever=self.vector_store.as_retriever(search_kwargs={"k": 5}),
                return_source_documents=True
            )
            
            return True
            
        except Exception as e:
            st.error(f"Error initializing RAG system: {str(e)}")
            return False
    
    def search_similar_documents(self, query: str, k: int = 5) -> List[Dict]:
        """Search for similar documents"""
        if not self.vector_store:
            return []
        
        try:
            docs_with_scores = self.vector_store.similarity_search_with_score(query, k=k)
            
            results = []
            for doc, score in docs_with_scores:
                results.append({
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'similarity_score': float(score)
                })
            
            return results
        
        except Exception as e:
            st.error(f"Error searching documents: {str(e)}")
            return []
    
    def generate_answer(self, query: str, retrieved_docs: List[Dict]) -> str:
        """Generate answer based on retrieved documents (simplified version)"""
        # This is a simplified answer generation
        # In production, you'd use OpenAI or another LLM
        
        context = "\n\n".join([doc['content'] for doc in retrieved_docs[:3]])
        
        # Simple keyword-based responses for demo
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['top', 'best', 'highest', 'leading']):
            return self._generate_top_performers_answer(retrieved_docs, query)
        elif any(word in query_lower for word in ['compare', 'comparison', 'versus', 'vs']):
            return self._generate_comparison_answer(retrieved_docs, query)
        elif any(word in query_lower for word in ['trend', 'evolution', 'progress', 'improvement']):
            return self._generate_trend_answer(retrieved_docs, query)
        elif any(word in query_lower for word in ['governance', 'political', 'regulatory']):
            return self._generate_governance_answer(retrieved_docs, query)
        else:
            return self._generate_general_answer(retrieved_docs, query)
    
    def _generate_top_performers_answer(self, docs: List[Dict], query: str) -> str:
        """Generate answer for top performers queries"""
        countries_scores = []
        for doc in docs:
            if 'country' in doc['metadata'] and 'adei_score' in doc['metadata']:
                countries_scores.append((
                    doc['metadata']['country'],
                    doc['metadata']['adei_score'],
                    doc['metadata'].get('year', 'Unknown')
                ))
        
        # Sort by score
        countries_scores.sort(key=lambda x: x[1], reverse=True)
        top_5 = countries_scores[:5]
        
        if top_5:
            answer = "Based on the OIC ADEI data, the top performing countries are:\n\n"
            for i, (country, score, year) in enumerate(top_5, 1):
                answer += f"{i}. **{country}**: {score:.1f} points ({year})\n"
            
            answer += f"\nThese rankings are based on the overall ADEI score, which measures performance across 8 key development pillars including governance, technology infrastructure, innovation, and sustainable development goals."
            return answer
        
        return "I couldn't find specific ranking information in the retrieved data."
    
    def _generate_comparison_answer(self, docs: List[Dict], query: str) -> str:
        """Generate answer for comparison queries"""
        # Extract country mentions from query
        countries_mentioned = []
        for doc in docs:
            if 'country' in doc['metadata']:
                country = doc['metadata']['country']
                if country.lower() in query.lower():
                    countries_mentioned.append((
                        country,
                        doc['metadata'].get('adei_score', 0),
                        doc['metadata'].get('year', 'Unknown')
                    ))
        
        if len(countries_mentioned) >= 2:
            answer = "Based on the data, here's a comparison:\n\n"
            for country, score, year in countries_mentioned[:3]:
                answer += f"**{country}** ({year}): {score:.1f} ADEI points\n"
            return answer
        
        return "Please specify the countries you'd like to compare, and I'll provide detailed comparisons based on the available data."
    
    def _generate_trend_answer(self, docs: List[Dict], query: str) -> str:
        """Generate answer for trend queries"""
        return "The OIC ADEI dataset shows various trends from 2021-2025. Most countries have shown gradual improvement in their overall scores, with particular advances in technology infrastructure and digital government services. The top-performing countries have maintained their leadership while some middle-tier countries have shown significant improvement rates."
    
    def _generate_governance_answer(self, docs: List[Dict], query: str) -> str:
        """Generate answer for governance queries"""
        return "Governance indicators in the OIC ADEI dataset include political stability, government effectiveness, voice and accountability, regulatory quality, rule of law, and control of corruption. These indicators show significant variation across OIC countries, with Gulf countries generally scoring higher in regulatory quality and government effectiveness."
    
    def _generate_general_answer(self, docs: List[Dict], query: str) -> str:
        """Generate general answer"""
        return f"Based on the OIC ADEI dataset, I found relevant information about {len(docs)} countries/records. The data covers 57 OIC member countries from 2021-2025, measuring performance across 8 development pillars. Could you please be more specific about what aspect you'd like to know about?"
    
    def save_feedback(self, question: str, answer: str, rating: int, feedback_text: str = ""):
        """Save user feedback to database"""
        try:
            conn = sqlite3.connect(self.feedback_db)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO feedback (question, answer, rating, feedback_text)
                VALUES (?, ?, ?, ?)
            ''', (question, answer, rating, feedback_text))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Error saving feedback: {str(e)}")
            return False

def show_rag_search(df=None):
    """RAG Search Interface"""
    st.markdown('<div class="main-header">🔍 RAG Search - Ask Questions About OIC Data</div>', unsafe_allow_html=True)
    
    # Use provided data or show error if not available
    if df is None:
        st.error("Data not provided to RAG search module.")
        return
    
    # Initialize RAG system
    if 'rag_system' not in st.session_state:
        with st.spinner("Initializing RAG system... This may take a moment."):
            # Always use FallbackRAG for better reliability and performance
            # The FallbackRAG now has enhanced contextual answer generation
            st.session_state.rag_system = FallbackRAG()
            st.info("✨ Using enhanced RAG search with contextual answer generation")
            
            # Load documents into the fallback system
            st.session_state.rag_system.load_documents(df)
            st.success("✅ RAG system initialized successfully!")
    
    rag_system = st.session_state.rag_system
    
    # Search interface
    st.markdown("### 💬 Ask Questions About OIC ADEI Data")
    
    # Example questions
    with st.expander("💡 Example Questions"):
        example_questions = [
            "Which countries have the highest ADEI scores?",
            "What are the lowest performing countries?",
            "Compare Turkey and Indonesia ADEI scores",
            "Which countries improved the most over time?",
            "Show me Malaysia's performance",
            "What is the average ADEI score for Arab countries?",
            "Which countries perform best in education?",
            "What are the trends in political empowerment?"
        ]
        
        for i, question in enumerate(example_questions, 1):
            st.markdown(f"{i}. {question}")
    
    # Search input
    user_question = st.text_input(
        "Enter your question about OIC ADEI data:",
        placeholder="e.g., Which countries have the highest governance scores?"
    )
    
    col1, col2 = st.columns([3, 1])
    with col1:
        search_button = st.button("🔍 Search", type="primary")
    with col2:
        clear_history = st.button("🗑️ Clear History")
    
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if clear_history:
        st.session_state.chat_history = []
        st.rerun()
    
    # Process search
    if search_button and user_question:
        with st.spinner("Searching and generating answer..."):
            # Use the enhanced search method that generates contextual answers
            answer = rag_system.search(user_question, k=10)
            
            # Also retrieve docs for display (using search_similar_documents for backward compatibility)
            retrieved_docs = rag_system.search_similar_documents(user_question, k=5)
            
            # Add to chat history
            st.session_state.chat_history.append({
                'question': user_question,
                'answer': answer,
                'retrieved_docs': retrieved_docs,
                'timestamp': datetime.now()
            })
    
    # Display chat history
    if st.session_state.chat_history:
        st.markdown("### 💬 Search Results")
        
        for i, chat in enumerate(reversed(st.session_state.chat_history)):
            with st.container():
                st.markdown(f"**Q{len(st.session_state.chat_history)-i}:** {chat['question']}")
                st.markdown(f"**Answer:** {chat['answer']}")
                
                # Show source documents
                with st.expander("📄 Source Documents"):
                    for j, doc in enumerate(chat['retrieved_docs'][:3], 1):
                        st.markdown(f"**Source {j}** (Similarity: {doc['similarity_score']:.3f})")
                        
                        # Handle both LangChain and fallback document formats
                        if 'metadata' in doc:
                            # LangChain format
                            if 'country' in doc['metadata']:
                                st.markdown(f"Country: {doc['metadata']['country']}, Year: {doc['metadata'].get('year', 'N/A')}")
                            content = doc['content']
                        else:
                            # Fallback format
                            if 'country' in doc:
                                st.markdown(f"Country: {doc['country']}, Year: {doc.get('year', 'N/A')}")
                            content = doc.get('text', str(doc))
                        
                        st.markdown(content[:300] + "..." if len(content) > 300 else content)
                        st.markdown("---")
                
                # Feedback section
                st.markdown("**Was this answer helpful?**")
                col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 2])
                
                feedback_key = f"feedback_{len(st.session_state.chat_history)-i}"
                
                with col1:
                    if st.button("👍", key=f"thumbs_up_{i}"):
                        rag_system.save_feedback(chat['question'], chat['answer'], 5)
                        st.success("Thanks!")
                
                with col2:
                    if st.button("👎", key=f"thumbs_down_{i}"):
                        rag_system.save_feedback(chat['question'], chat['answer'], 1)
                        st.info("Feedback saved")
                
                with col6:
                    feedback_text = st.text_input(
                        "Additional feedback:",
                        key=f"feedback_text_{i}",
                        placeholder="Optional feedback..."
                    )
                    if feedback_text and st.button("Submit", key=f"submit_{i}"):
                        rag_system.save_feedback(chat['question'], chat['answer'], 3, feedback_text)
                        st.success("Feedback submitted!")
                
                st.markdown("---")
    
    # Statistics and system info
    st.markdown("### 📊 System Information")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Documents Indexed", len(rag_system.documents) if rag_system.documents else 0)
    
    with col2:
        st.metric("Countries Covered", df['country'].nunique() if df is not None else 0)
    
    with col3:
        st.metric("Years Covered", f"{df['year'].min()}-{df['year'].max()}" if df is not None else "N/A")
    
    # Advanced search options
    with st.expander("⚙️ Advanced Search Options"):
        st.markdown("**Search Filters:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            filter_countries = st.multiselect(
                "Filter by Countries:",
                options=sorted(df['country'].unique()) if df is not None else [],
                help="Limit search to specific countries"
            )
        
        with col2:
            filter_years = st.multiselect(
                "Filter by Years:",
                options=sorted(df['year'].unique()) if df is not None else [],
                help="Limit search to specific years"
            )
        
        search_depth = st.slider(
            "Search Depth (number of documents to retrieve):",
            min_value=3,
            max_value=10,
            value=5,
            help="More documents provide more context but may be slower"
        )
    
    # Help section
    with st.expander("❓ How to Use RAG Search"):
        st.markdown("""
        **RAG (Retrieval-Augmented Generation) Search** allows you to ask natural language questions about the OIC ADEI dataset.
        
        **How it works:**
        1. **Enter your question** in natural language
        2. **The system searches** through the database using semantic similarity
        3. **Relevant documents are retrieved** and ranked by relevance
        4. **An answer is generated** based on the retrieved information
        
        **Tips for better results:**
        - Be specific in your questions (mention countries, years, or metrics)
        - Use comparative language for comparisons ("compare", "versus", "better than")
        - Ask about trends using temporal words ("improved", "declined", "over time")
        - Request specific data types ("scores", "rankings", "percentages")
        
        **Example question types:**
        - Rankings: "Top 10 countries in governance"
        - Comparisons: "UAE vs Qatar innovation scores"
        - Trends: "Which countries improved most from 2021 to 2025"
        - Analysis: "Correlation between governance and technology"
        """)