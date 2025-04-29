import logging
import os
import json
import time
from typing import Dict, List, Optional
from openai import OpenAI
from openai.types.beta.assistant import Assistant
from openai.types.beta.thread import Thread
from openai.types.beta.threads import Run

# Configure logging
logger = logging.getLogger(__name__)

class AgentSystem:
    """Base class for OpenAI Assistant-based agents"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """Initialize Agent with OpenAI API key"""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not found. Agent system will not work.")
        
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
        self.model = model
        self.assistant = None
        self.assistant_id = None
    
    def create_assistant(self, name: str, instructions: str, tools: List[Dict] = None):
        """Create an OpenAI Assistant"""
        if not self.client:
            logger.error("OpenAI client not initialized. Check API key.")
            return None
            
        try:
            tool_config = [{"type": "function", "function": tool} for tool in tools] if tools else []
            
            if not tool_config:
                # Default to code interpreter if no tools specified
                tool_config = [{"type": "code_interpreter"}]
                
            self.assistant = self.client.beta.assistants.create(
                name=name,
                instructions=instructions,
                model=self.model,
                tools=tool_config
            )
            self.assistant_id = self.assistant.id
            logger.info(f"Created assistant: {name} (ID: {self.assistant_id})")
            return self.assistant
        except Exception as e:
            logger.error(f"Error creating assistant: {str(e)}")
            return None
    
    def create_thread(self):
        """Create a new thread for conversation"""
        if not self.client:
            logger.error("OpenAI client not initialized. Check API key.")
            return None
            
        try:
            thread = self.client.beta.threads.create()
            logger.info(f"Created thread: {thread.id}")
            return thread
        except Exception as e:
            logger.error(f"Error creating thread: {str(e)}")
            return None
    
    def add_message(self, thread_id: str, content: str, role: str = "user"):
        """Add a message to the thread"""
        if not self.client:
            logger.error("OpenAI client not initialized. Check API key.")
            return None
            
        try:
            message = self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role=role,
                content=content
            )
            logger.info(f"Added message to thread {thread_id}")
            return message
        except Exception as e:
            logger.error(f"Error adding message: {str(e)}")
            return None
    
    def run_assistant(self, thread_id: str, assistant_id: str = None):
        """Run the assistant on the thread"""
        if not self.client:
            logger.error("OpenAI client not initialized. Check API key.")
            return None
            
        try:
            assistant_id = assistant_id or self.assistant_id
            if not assistant_id:
                logger.error("No assistant ID provided")
                return None
                
            run = self.client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=assistant_id
            )
            logger.info(f"Started run {run.id} on thread {thread_id}")
            return run
        except Exception as e:
            logger.error(f"Error running assistant: {str(e)}")
            return None
    
    def wait_for_run(self, thread_id: str, run_id: str, poll_interval: float = 0.5, timeout: float = 30.0):
        """Wait for a run to complete"""
        if not self.client:
            logger.error("OpenAI client not initialized. Check API key.")
            return None
            
        start_time = time.time()
        while True:
            try:
                run = self.client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
                
                if run.status == "completed":
                    logger.info(f"Run {run_id} completed")
                    return run
                    
                if run.status in ["failed", "cancelled", "expired"]:
                    logger.error(f"Run {run_id} ended with status: {run.status}")
                    return run
                    
                if time.time() - start_time > timeout:
                    logger.warning(f"Timeout waiting for run {run_id}")
                    return run
                    
                time.sleep(poll_interval)
                
            except Exception as e:
                logger.error(f"Error checking run status: {str(e)}")
                return None
    
    def get_messages(self, thread_id: str, limit: int = 10):
        """Get messages from a thread"""
        if not self.client:
            logger.error("OpenAI client not initialized. Check API key.")
            return []
            
        try:
            messages = self.client.beta.threads.messages.list(
                thread_id=thread_id,
                limit=limit
            )
            return messages.data
        except Exception as e:
            logger.error(f"Error getting messages: {str(e)}")
            return []
    
    def get_last_response(self, thread_id: str):
        """Get the last assistant response"""
        messages = self.get_messages(thread_id, limit=10)
        for message in messages:
            if message.role == "assistant":
                return message.content[0].text.value
        return None


class SafetyAgent(AgentSystem):
    """Agent specialized in food safety and temperature monitoring"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        super().__init__(api_key, model)
        
        instructions = """
        You are a Food Safety Expert specialized in monitoring refrigerator conditions.
        
        Your responsibilities:
        1. Analyze temperature readings (ideal fridge temp is 3-5°C)
        2. Evaluate gas levels for potential issues
        3. Monitor humidity levels (ideal range 40-70%)
        
        For each analysis, provide:
        - A clear assessment of current conditions
        - Safety warnings if values are outside ideal ranges
        - Recommendations to improve conditions if needed
        
        Always start responses with an emoji indicating safety status:
        ✅ = Safe, 🟡 = Caution, 🚨 = Danger
        
        Be concise and factual. Focus only on safety aspects of refrigeration.
        """
        
        self.create_assistant("Food Safety Expert", instructions)
    
    async def analyze_safety(self, temp: float, humidity: float, gas: int) -> Dict:
        """Analyze safety aspects of fridge data"""
        if not self.client or not self.assistant_id:
            return {"safety": "Safety analysis unavailable"}
        
        thread = self.create_thread()
        if not thread:
            return {"safety": "Safety analysis unavailable"}
        
        # Create the input prompt
        prompt = f"""
        Please analyze these refrigerator conditions for safety:
        
        Temperature: {temp}°C
        Humidity: {humidity}%
        Gas Level: {gas} ppm
        
        Provide a concise safety assessment with appropriate emoji prefix.
        """
        
        self.add_message(thread.id, prompt)
        run = self.run_assistant(thread.id)
        
        if run:
            self.wait_for_run(thread.id, run.id)
            response = self.get_last_response(thread.id)
            return {"safety": response or "Safety analysis failed"}
        
        return {"safety": "Safety analysis unavailable"}


class FreshnessAgent(AgentSystem):
    """Agent specialized in food freshness assessment"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        super().__init__(api_key, model)
        
        instructions = """
        You are a Food Freshness Expert specialized in assessing refrigerated foods.
        
        Your responsibilities:
        1. Analyze detected food items in a refrigerator
        2. Estimate their likely freshness based on common knowledge
        3. Prioritize foods that may need to be consumed soon
        
        For each analysis, provide:
        - Assessment of which items may be nearing end of freshness
        - Suggestions for which items to use first
        - Tips to extend freshness when appropriate
        
        Always start responses with relevant food emoji and keep suggestions concise.
        Focus only on freshness of the detected food items, not safety or recipes.
        """
        
        self.create_assistant("Food Freshness Expert", instructions)
    
    async def analyze_freshness(self, items: List[str]) -> Dict:
        """Analyze freshness of detected food items"""
        if not self.client or not self.assistant_id:
            return {"freshness": "Freshness analysis unavailable"}
        
        thread = self.create_thread()
        if not thread:
            return {"freshness": "Freshness analysis unavailable"}
        
        # Create the input prompt
        items_text = ", ".join(items) if items else "No items detected"
        prompt = f"""
        Please analyze these food items detected in a refrigerator:
        
        Items: {items_text}
        
        Provide a concise freshness assessment with appropriate food emoji.
        """
        
        self.add_message(thread.id, prompt)
        run = self.run_assistant(thread.id)
        
        if run:
            self.wait_for_run(thread.id, run.id)
            response = self.get_last_response(thread.id)
            return {"freshness": response or "Freshness analysis failed"}
        
        return {"freshness": "Freshness analysis unavailable"}


class RecipeAgent(AgentSystem):
    """Agent specialized in recipe suggestions"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        super().__init__(api_key, model)
        
        instructions = """
        You are a Creative Chef specialized in suggesting recipes based on available ingredients.
        
        Your responsibilities:
        1. Analyze available food items in a refrigerator
        2. Suggest creative, practical recipes using those ingredients
        3. Prioritize using items that may need to be consumed soon
        
        For each analysis, provide:
        - 1-2 specific recipe suggestions with names
        - Brief description of how to use the available ingredients
        
        Always start responses with a cooking emoji (🍳, 🥗, 🍲, etc.)
        Keep suggestions concise and focused only on recipes, not freshness or safety.
        """
        
        self.create_assistant("Creative Chef", instructions)
    
    async def suggest_recipes(self, items: List[str]) -> Dict:
        """Suggest recipes based on available food items"""
        if not self.client or not self.assistant_id:
            return {"recipes": "Recipe suggestions unavailable"}
        
        thread = self.create_thread()
        if not thread:
            return {"recipes": "Recipe suggestions unavailable"}
        
        # Create the input prompt
        items_text = ", ".join(items) if items else "No items detected"
        prompt = f"""
        Please suggest recipes using these food items detected in a refrigerator:
        
        Items: {items_text}
        
        Provide 1-2 concise recipe suggestions with appropriate cooking emoji.
        """
        
        self.add_message(thread.id, prompt)
        run = self.run_assistant(thread.id)
        
        if run:
            self.wait_for_run(thread.id, run.id)
            response = self.get_last_response(thread.id)
            return {"recipes": response or "Recipe suggestions failed"}
        
        return {"recipes": "Recipe suggestions unavailable"}


class GuardrailAgent(AgentSystem):
    """Guardrail agent to ensure proper response format and quality"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        super().__init__(api_key, model)
        
        instructions = """
        You are a Guardrail Agent for a Smart Fridge AI system.
        
        Your job is to:
        1. Ensure that all analyses are properly formatted and consistent
        2. Combine all analyses into a coherent summary response
        3. Flag any inappropriate content and replace it with appropriate text
        4. Maintain a consistent, helpful tone across all responses
        
        The analysis should include sections for:
        - Safety - About temperature, humidity, and gas conditions
        - Freshness - About the freshness of food items
        - Recipes - Suggested recipes based on available ingredients
        - Expiration - Information about items that may be expiring soon
        
        Decide which priority to assign based on the content and urgency:
        - If there are safety concerns, "safety" should be first
        - If items are expiring, "expiration" should be high priority
        - Otherwise, arrange in a logical order that highlights actionable items first
        
        Always return 4 analysis sections, even if the input is missing some.
        """
        
        self.create_assistant("Guardrail Agent", instructions)
    
    async def validate_analysis(
        self, 
        temp: float, 
        humidity: float, 
        gas: int,
        items: List[str],
        analysis: Dict
    ) -> Dict:
        """Validate and improve the analysis from other agents"""
        if not self.client or not self.assistant_id:
            return {
                "ai_response": "Smart Fridge AI analysis ready",
                "priority": ["safety", "expiration", "freshness", "recipes"],
                "analysis": analysis
            }
        
        thread = self.create_thread()
        if not thread:
            return {
                "ai_response": "Smart Fridge AI analysis ready",
                "priority": ["safety", "expiration", "freshness", "recipes"],
                "analysis": analysis
            }
        
        # Create the input prompt
        prompt = f"""
        Please review and validate the following Smart Fridge analysis:
        
        Fridge Data:
        - Temperature: {temp}°C
        - Humidity: {humidity}%
        - Gas Level: {gas} ppm
        - Detected Items: {", ".join(items) if items else "None"}
        
        Analysis Results:
        - Safety: {analysis.get('safety', 'Not available')}
        - Freshness: {analysis.get('freshness', 'Not available')}
        - Recipes: {analysis.get('recipes', 'Not available')}
        - Expiration: {analysis.get('expiration', 'Not available')}
        
        Please:
        1. Check if all analyses are appropriate and well-formatted
        2. Create a concise AI response summarizing the key findings
        3. Determine the priority order for displaying the analyses
        4. Return a JSON object with ai_response, priority, and analysis keys
        """
        
        self.add_message(thread.id, prompt)
        run = self.run_assistant(thread.id)
        
        if run:
            self.wait_for_run(thread.id, run.id, timeout=60.0)
            response = self.get_last_response(thread.id)
            
            # Try to extract a JSON object from the response
            try:
                import re
                json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group(1))
                    return result
                
                # If no JSON found, build our own response
                return {
                    "ai_response": response or "Smart Fridge AI analysis ready",
                    "priority": ["safety", "expiration", "freshness", "recipes"],
                    "analysis": analysis
                }
            except Exception as e:
                logger.error(f"Error parsing guardrail response: {str(e)}")
        
        # Default response if anything fails
        return {
            "ai_response": "Smart Fridge AI analysis ready",
            "priority": ["safety", "expiration", "freshness", "recipes"],
            "analysis": analysis
        }


class FridgeAgent:
    """Main agent coordination class for Smart Fridge"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Fridge Agent system"""
        self.safety_agent = SafetyAgent(api_key)
        self.freshness_agent = FreshnessAgent(api_key)
        self.recipe_agent = RecipeAgent(api_key)
        self.guardrail_agent = GuardrailAgent(api_key)
        
        # Import here to avoid circular imports
        from agents.expiration_agent import expiration_tracker
        self.expiration_tracker = expiration_tracker
    
    async def analyze(
        self, 
        temp: float, 
        humidity: float, 
        gas: int, 
        items: List[str]
    ) -> Dict:
        """
        Analyze fridge data and produce insights
        
        Args:
            temp: Temperature in Celsius
            humidity: Humidity percentage
            gas: Gas level in PPM
            items: List of detected food items
            
        Returns:
            Dict with analysis results
        """
        logger.info(f"Analyzing fridge data: Temp={temp}°C, Humidity={humidity}%, Gas={gas}ppm")
        logger.info(f"Detected items: {items}")
        
        # Run all analyses in parallel
        safety_result = await self.safety_agent.analyze_safety(temp, humidity, gas)
        freshness_result = await self.freshness_agent.analyze_freshness(items)
        recipe_result = await self.recipe_agent.suggest_recipes(items)
        
        # Add expiration tracking and analysis
        expiration_result = await self.expiration_tracker.get_expiration_analysis(items)
        
        # Combine all analysis results
        analysis = {
            "safety": safety_result.get("safety", "Safety analysis unavailable"),
            "freshness": freshness_result.get("freshness", "Freshness analysis unavailable"),
            "recipes": recipe_result.get("recipes", "Recipe suggestions unavailable"),
            "expiration": expiration_result.get("expiration", "Expiration tracking unavailable")
        }
        
        # Run the guardrail to ensure proper formatting and quality
        result = await self.guardrail_agent.validate_analysis(
            temp=temp,
            humidity=humidity,
            gas=gas,
            items=items,
            analysis=analysis
        )
        
        # Set default priority
        if "priority" not in result:
            # Include expiration in the priority list
            result["priority"] = ["safety", "expiration", "freshness", "recipes"]
        elif "expiration" not in result["priority"]:
            # Insert expiration after safety if it's not already in the list
            safety_index = result["priority"].index("safety") if "safety" in result["priority"] else 0
            result["priority"].insert(safety_index + 1, "expiration")
        
        logger.info("Analysis completed successfully")
        return result

# Create a singleton instance
fridge_agent = FridgeAgent() 