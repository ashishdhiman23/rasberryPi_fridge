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
    """Agent that verifies and ensures safety of all recommendations"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        super().__init__(api_key, model)
        
        instructions = """
        You are a Food Safety Guardrail that reviews and verifies all recommendations.
        
        Your responsibilities:
        1. Review input data and agent outputs for safety concerns
        2. Verify that temperature, humidity, and gas readings are interpreted correctly
        3. Ensure food safety is prioritized in all recommendations
        4. Override any suggestions that could pose health risks
        
        Rules to enforce:
        - Temperature must be 0-5°C (warn if outside this range)
        - Gas levels above 300 ppm require immediate attention
        - Never recommend consuming food that might be spoiled
        - Never provide medical advice
        
        Flag any recommendations that violate these rules and provide safer alternatives.
        Be the final authority on food safety matters.
        """
        
        self.create_assistant("Food Safety Guardrail", instructions)
    
    async def validate_analysis(
        self, 
        temp: float, 
        humidity: float, 
        gas: int,
        items: List[str],
        analysis: Dict
    ) -> Dict:
        """Validate analysis results from other agents"""
        if not self.client or not self.assistant_id:
            return {"ai_response": "AI analysis validation unavailable"}
        
        thread = self.create_thread()
        if not thread:
            return {"ai_response": "AI analysis validation unavailable"}
        
        # Format the input data and analysis for review
        items_text = ", ".join(items) if items else "No items detected"
        analysis_text = json.dumps(analysis, indent=2)
        
        prompt = f"""
        Please review these refrigerator conditions and agent analyses for safety:
        
        SENSOR DATA:
        Temperature: {temp}°C
        Humidity: {humidity}%
        Gas Level: {gas} ppm
        Food Items: {items_text}
        
        AGENT ANALYSES:
        {analysis_text}
        
        Please provide:
        1. A priority alert or recommendation (ai_response)
        2. Validation of the analysis results
        3. Any safety overrides if necessary
        
        Return only a validated ai_response that addresses the most important issue.
        """
        
        self.add_message(thread.id, prompt)
        run = self.run_assistant(thread.id)
        
        if run:
            self.wait_for_run(thread.id, run.id)
            response = self.get_last_response(thread.id)
            return {"ai_response": response or "Analysis validation failed"}
        
        return {"ai_response": "Analysis validation unavailable"}


class FridgeAgent:
    """
    FridgeAgent is a multi-agent system that coordinates specialized agents
    to analyze fridge data and provide insights on safety, freshness, and recipes.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the agent system with OpenAI API key"""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not found. FridgeAgent will not work.")
        
        # Initialize specialized agents
        self.safety_agent = SafetyAgent(api_key=self.api_key)
        self.freshness_agent = FreshnessAgent(api_key=self.api_key)
        self.recipe_agent = RecipeAgent(api_key=self.api_key)
        self.guardrail_agent = GuardrailAgent(api_key=self.api_key)
    
    async def analyze(
        self, 
        temp: float, 
        humidity: float, 
        gas: int, 
        items: List[str]
    ) -> Dict:
        """
        Analyze the fridge data using a multi-agent approach
        
        Args:
            temp: Temperature in Celsius
            humidity: Humidity percentage
            gas: Gas level in ppm
            items: List of detected food items
            
        Returns:
            Dict with analysis results from all agents after guardrail validation
        """
        # Default response in case of failure
        default_response = {
            "ai_response": "AI analysis unavailable",
            "priority": ["safety", "freshness", "recipes"],
            "analysis": {
                "safety": "Analysis unavailable",
                "freshness": "Analysis unavailable",
                "recipes": "Analysis unavailable"
            }
        }
        
        try:
            # Run specialized analyses in parallel (if using Python 3.7+)
            import asyncio
            
            # Step 1: Get safety analysis
            safety_task = asyncio.create_task(
                self.safety_agent.analyze_safety(temp, humidity, gas)
            )
            
            # Step 2: Get freshness analysis
            freshness_task = asyncio.create_task(
                self.freshness_agent.analyze_freshness(items)
            )
            
            # Step 3: Get recipe suggestions
            recipe_task = asyncio.create_task(
                self.recipe_agent.suggest_recipes(items)
            )
            
            # Wait for all tasks to complete
            safety_result = await safety_task
            freshness_result = await freshness_task
            recipe_result = await recipe_task
            
            # Combine results
            analysis = {
                **safety_result,
                **freshness_result,
                **recipe_result
            }
            
            # Determine priority based on results
            # Simple logic: if there's a safety concern, prioritize safety
            priority = ["safety", "freshness", "recipes"]
            
            safety_text = safety_result.get("safety", "").lower()
            if "danger" in safety_text or "warning" in safety_text or "🚨" in safety_text:
                priority = ["safety", "freshness", "recipes"]
            elif "caution" in safety_text or "🟡" in safety_text:
                priority = ["safety", "freshness", "recipes"]
            else:
                # If no safety concerns, maybe prioritize freshness
                freshness_text = freshness_result.get("freshness", "").lower()
                if "soon" in freshness_text or "old" in freshness_text or "expire" in freshness_text:
                    priority = ["freshness", "safety", "recipes"]
                else:
                    # Otherwise, recipes can be first
                    priority = ["recipes", "freshness", "safety"]
            
            # Step 4: Run everything through the guardrail
            guardrail_result = await self.guardrail_agent.validate_analysis(
                temp, humidity, gas, items, analysis
            )
            
            # Return the final result
            return {
                "ai_response": guardrail_result.get("ai_response", "Analysis complete"),
                "priority": priority,
                "analysis": analysis
            }
            
        except Exception as e:
            logger.error(f"Error in multi-agent analysis: {str(e)}")
            return default_response

# Create a singleton instance
fridge_agent = FridgeAgent() 