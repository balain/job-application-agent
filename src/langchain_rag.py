"""
RAG (Retrieval-Augmented Generation) for application similarity and knowledge retrieval.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from langchain_chroma import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.vectorstores import VectorStore

from pathlib import Path
from platformdirs import user_data_dir

logger = logging.getLogger(__name__)


class ApplicationRAG:
    """
    RAG system for storing and retrieving similar applications.
    """
    
    def __init__(
        self,
        persist_directory: Optional[Path] = None,
        collection_name: str = "applications"
    ):
        self.persist_directory = persist_directory or Path(user_data_dir("job-application-agent")) / "vectorstore"
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        self.collection_name = collection_name
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings()
        
        # Initialize vector store
        self.vectorstore = Chroma(
            persist_directory=str(self.persist_directory),
            embedding_function=self.embeddings,
            collection_name=self.collection_name
        )
        
        logger.info(f"Application RAG initialized at {self.persist_directory}")
    
    def add_application(self, app_data: Dict[str, Any]) -> None:
        """
        Add application to vector store.
        
        Args:
            app_data: Application data dictionary
        """
        try:
            # Create document content
            content = self._create_document_content(app_data)
            
            # Create document
            doc = Document(
                page_content=content,
                metadata={
                    "application_id": app_data.get("id"),
                    "company": app_data.get("company", "Unknown"),
                    "job_title": app_data.get("job_title", "Unknown"),
                    "industry": app_data.get("industry", "Unknown"),
                    "status": app_data.get("status", "Unknown"),
                    "date_applied": app_data.get("date_applied"),
                    "user_id": app_data.get("user_id"),
                    **app_data.get("metadata", {})
                }
            )
            
            # Add to vector store
            self.vectorstore.add_documents([doc])
            logger.info(f"Added application {app_data.get('id')} to vector store")
            
        except Exception as e:
            logger.error(f"Error adding application to vector store: {e}")
            raise
    
    def find_similar_applications(
        self,
        query: str,
        k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Find similar applications using semantic search.
        
        Args:
            query: Search query
            k: Number of results to return
            filter_dict: Optional metadata filters
            
        Returns:
            List of similar application metadata
        """
        try:
            # Perform similarity search
            results = self.vectorstore.similarity_search(
                query,
                k=k,
                filter=filter_dict
            )
            
            # Extract metadata
            similar_apps = []
            for doc in results:
                similar_apps.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "similarity_score": getattr(doc, 'score', None)
                })
            
            logger.info(f"Found {len(similar_apps)} similar applications for query: {query}")
            return similar_apps
            
        except Exception as e:
            logger.error(f"Error finding similar applications: {e}")
            return []
    
    def find_applications_by_company(self, company: str, k: int = 10) -> List[Dict[str, Any]]:
        """
        Find applications by company name.
        
        Args:
            company: Company name
            k: Number of results to return
            
        Returns:
            List of applications for the company
        """
        return self.find_similar_applications(
            f"company: {company}",
            k=k,
            filter_dict={"company": company}
        )
    
    def find_applications_by_industry(self, industry: str, k: int = 10) -> List[Dict[str, Any]]:
        """
        Find applications by industry.
        
        Args:
            industry: Industry name
            k: Number of results to return
            
        Returns:
            List of applications in the industry
        """
        return self.find_similar_applications(
            f"industry: {industry}",
            k=k,
            filter_dict={"industry": industry}
        )
    
    def find_applications_by_skills(self, skills: List[str], k: int = 10) -> List[Dict[str, Any]]:
        """
        Find applications by required skills.
        
        Args:
            skills: List of skills
            k: Number of results to return
            
        Returns:
            List of applications requiring these skills
        """
        query = f"skills: {', '.join(skills)}"
        return self.find_similar_applications(query, k=k)
    
    def get_application_stats(self) -> Dict[str, Any]:
        """
        Get statistics about stored applications.
        
        Returns:
            Application statistics
        """
        try:
            # Get all documents
            all_docs = self.vectorstore.similarity_search("", k=1000)
            
            if not all_docs:
                return {
                    "total_applications": 0,
                    "companies": [],
                    "industries": [],
                    "statuses": []
                }
            
            # Extract statistics
            companies = set()
            industries = set()
            statuses = set()
            
            for doc in all_docs:
                metadata = doc.metadata
                if metadata.get("company"):
                    companies.add(metadata["company"])
                if metadata.get("industry"):
                    industries.add(metadata["industry"])
                if metadata.get("status"):
                    statuses.add(metadata["status"])
            
            return {
                "total_applications": len(all_docs),
                "companies": list(companies),
                "industries": list(industries),
                "statuses": list(statuses),
                "unique_companies": len(companies),
                "unique_industries": len(industries)
            }
            
        except Exception as e:
            logger.error(f"Error getting application stats: {e}")
            return {"error": str(e)}
    
    def delete_application(self, application_id: str) -> bool:
        """
        Delete application from vector store.
        
        Args:
            application_id: Application ID to delete
            
        Returns:
            True if deleted successfully
        """
        try:
            # Find documents with matching application_id
            results = self.vectorstore.similarity_search(
                "",
                k=1000,
                filter={"application_id": application_id}
            )
            
            if not results:
                logger.warning(f"No application found with ID: {application_id}")
                return False
            
            # Delete documents (Chroma doesn't have direct delete by metadata)
            # This is a limitation - we'd need to implement custom deletion
            logger.warning(f"Cannot delete application {application_id} - Chroma limitation")
            return False
            
        except Exception as e:
            logger.error(f"Error deleting application: {e}")
            return False
    
    def _create_document_content(self, app_data: Dict[str, Any]) -> str:
        """
        Create document content from application data.
        
        Args:
            app_data: Application data dictionary
            
        Returns:
            Formatted document content
        """
        content_parts = []
        
        # Basic information
        if app_data.get("company"):
            content_parts.append(f"Company: {app_data['company']}")
        if app_data.get("job_title"):
            content_parts.append(f"Job Title: {app_data['job_title']}")
        if app_data.get("industry"):
            content_parts.append(f"Industry: {app_data['industry']}")
        if app_data.get("location"):
            content_parts.append(f"Location: {app_data['location']}")
        
        # Job description
        if app_data.get("job_description"):
            content_parts.append(f"Job Description: {app_data['job_description']}")
        
        # Skills
        if app_data.get("required_skills"):
            skills = app_data["required_skills"]
            if isinstance(skills, list):
                content_parts.append(f"Required Skills: {', '.join(skills)}")
            else:
                content_parts.append(f"Required Skills: {skills}")
        
        # Additional metadata
        if app_data.get("notes"):
            content_parts.append(f"Notes: {app_data['notes']}")
        
        return "\n".join(content_parts)
    
    def clear_all_applications(self) -> None:
        """Clear all applications from vector store."""
        try:
            # Delete the collection and recreate it
            self.vectorstore.delete_collection()
            self.vectorstore = Chroma(
                persist_directory=str(self.persist_directory),
                embedding_function=self.embeddings,
                collection_name=self.collection_name
            )
            logger.info("Cleared all applications from vector store")
        except Exception as e:
            logger.error(f"Error clearing applications: {e}")
            raise
