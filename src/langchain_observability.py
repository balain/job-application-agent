"""
Observability and monitoring for LangChain operations.
"""

import logging
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.outputs import LLMResult
from langchain_core.messages import BaseMessage

from pathlib import Path
from platformdirs import user_data_dir

logger = logging.getLogger(__name__)


class MetricsCallbackHandler(BaseCallbackHandler):
    """Track LLM usage metrics and performance."""
    
    def __init__(self):
        self.total_tokens = 0
        self.total_cost = 0.0
        self.total_calls = 0
        self.total_time = 0.0
        self.call_history: List[Dict[str, Any]] = []
        self.start_time = None
    
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) -> None:
        """Called when LLM starts."""
        self.start_time = datetime.now()
        self.total_calls += 1
        
        logger.debug(f"LLM call started - Call #{self.total_calls}")
    
    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Called when LLM ends."""
        if self.start_time:
            call_duration = (datetime.now() - self.start_time).total_seconds()
            self.total_time += call_duration
        
        # Extract token usage
        if hasattr(response, 'llm_output') and response.llm_output:
            token_usage = response.llm_output.get('token_usage', {})
            if token_usage:
                self.total_tokens += token_usage.get('total_tokens', 0)
                
                # Estimate cost (simplified)
                cost = self._estimate_cost(token_usage)
                self.total_cost += cost
        
        # Record call history
        call_info = {
            "timestamp": datetime.now().isoformat(),
            "duration": call_duration if self.start_time else 0,
            "tokens": token_usage.get('total_tokens', 0) if 'token_usage' in locals() else 0,
            "cost": cost if 'cost' in locals() else 0,
            "generations": len(response.generations)
        }
        self.call_history.append(call_info)
        
        logger.debug(f"LLM call completed - Duration: {call_duration:.2f}s, Tokens: {token_usage.get('total_tokens', 0)}")
    
    def on_llm_error(self, error: Exception, **kwargs: Any) -> None:
        """Called when LLM encounters an error."""
        logger.error(f"LLM error: {error}")
        
        # Record error in call history
        call_info = {
            "timestamp": datetime.now().isoformat(),
            "error": str(error),
            "duration": 0,
            "tokens": 0,
            "cost": 0
        }
        self.call_history.append(call_info)
    
    def _estimate_cost(self, token_usage: Dict[str, int]) -> float:
        """Estimate cost based on token usage (simplified)."""
        # This is a simplified cost estimation
        # In practice, you'd want to use actual model pricing
        total_tokens = token_usage.get('total_tokens', 0)
        
        # Rough estimate: $0.01 per 1000 tokens
        return (total_tokens / 1000) * 0.01
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        avg_duration = self.total_time / self.total_calls if self.total_calls > 0 else 0
        avg_tokens = self.total_tokens / self.total_calls if self.total_calls > 0 else 0
        
        return {
            "total_calls": self.total_calls,
            "total_tokens": self.total_tokens,
            "total_cost": round(self.total_cost, 4),
            "total_time": round(self.total_time, 2),
            "average_duration": round(avg_duration, 2),
            "average_tokens": round(avg_tokens, 2),
            "call_history": self.call_history[-10:]  # Last 10 calls
        }
    
    def reset_metrics(self) -> None:
        """Reset all metrics."""
        self.total_tokens = 0
        self.total_cost = 0.0
        self.total_calls = 0
        self.total_time = 0.0
        self.call_history = []
        self.start_time = None


class LangChainObservability:
    """Observability manager for LangChain operations."""
    
    def __init__(self):
        self.metrics_handler = MetricsCallbackHandler()
        self.enabled = self._is_tracing_enabled()
        self._setup_tracing()
    
    def _is_tracing_enabled(self) -> bool:
        """Check if LangSmith tracing is enabled."""
        return (
            os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true" and
            bool(os.getenv("LANGCHAIN_API_KEY"))
        )
    
    def _setup_tracing(self) -> None:
        """Setup LangSmith tracing if enabled."""
        if self.enabled:
            try:
                os.environ["LANGCHAIN_PROJECT"] = os.getenv(
                    "LANGCHAIN_PROJECT", 
                    "job-application-agent"
                )
                logger.info("LangSmith tracing enabled")
            except Exception as e:
                logger.error(f"Failed to setup LangSmith tracing: {e}")
                self.enabled = False
    
    def get_callbacks(self) -> List[BaseCallbackHandler]:
        """Get callback handlers for LLM calls."""
        callbacks = [self.metrics_handler]
        
        if self.enabled:
            # LangSmith callbacks are automatically added when tracing is enabled
            logger.debug("Using LangSmith callbacks")
        
        return callbacks
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        metrics = self.metrics_handler.get_metrics()
        metrics["tracing_enabled"] = self.enabled
        metrics["langsmith_project"] = os.getenv("LANGCHAIN_PROJECT", "job-application-agent")
        
        return metrics
    
    def reset_metrics(self) -> None:
        """Reset all metrics."""
        self.metrics_handler.reset_metrics()
    
    def log_operation(
        self,
        operation: str,
        details: Dict[str, Any],
        success: bool = True
    ) -> None:
        """Log a custom operation."""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "success": success,
            "details": details
        }
        
        if success:
            logger.info(f"Operation: {operation} - {details}")
        else:
            logger.error(f"Operation failed: {operation} - {details}")
    
    def export_metrics(self, file_path: Optional[str] = None) -> str:
        """Export metrics to file."""
        if file_path is None:
            file_path = Path(user_data_dir("job-application-agent")) / "metrics" / f"langchain_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        file_path = str(file_path)
        
        try:
            import json
            from pathlib import Path
            
            # Ensure directory exists
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            metrics = self.get_metrics()
            
            with open(file_path, 'w') as f:
                json.dump(metrics, f, indent=2)
            
            logger.info(f"Metrics exported to {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Failed to export metrics: {e}")
            raise


# Global observability instance
_observability: Optional[LangChainObservability] = None


def get_observability() -> LangChainObservability:
    """Get the global observability instance."""
    global _observability
    if _observability is None:
        _observability = LangChainObservability()
    return _observability


def get_callbacks() -> List[BaseCallbackHandler]:
    """Get callback handlers for LLM calls."""
    observability = get_observability()
    return observability.get_callbacks()


def log_operation(operation: str, details: Dict[str, Any], success: bool = True) -> None:
    """Log a custom operation."""
    observability = get_observability()
    observability.log_operation(operation, details, success)


def get_metrics() -> Dict[str, Any]:
    """Get current metrics."""
    observability = get_observability()
    return observability.get_metrics()


def reset_metrics() -> None:
    """Reset all metrics."""
    observability = get_observability()
    observability.reset_metrics()


def export_metrics(file_path: Optional[str] = None) -> str:
    """Export metrics to file."""
    observability = get_observability()
    return observability.export_metrics(file_path)
