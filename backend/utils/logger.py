import logging
import sys
from datetime import datetime
from typing import Any, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)

logger = logging.getLogger('fridgesense')

def log_request(request_data: Dict[str, Any], endpoint: str) -> None:
    """Log incoming request data"""
    logger.info(f"Request received at {endpoint}")
    logger.info(f"Request data: {request_data}")

def log_response(response_data: Dict[str, Any], endpoint: str) -> None:
    """Log outgoing response data"""
    logger.info(f"Response sent from {endpoint}")
    logger.info(f"Response data: {response_data}")

def log_error(error: Exception, endpoint: str) -> None:
    """Log error details"""
    logger.error(f"Error in {endpoint}: {str(error)}", exc_info=True)

def log_api_call(api_name: str, request_data: Dict[str, Any], response_data: Dict[str, Any]) -> None:
    """Log external API calls"""
    logger.info(f"External API call to {api_name}")
    logger.info(f"Request: {request_data}")
    logger.info(f"Response: {response_data}") 