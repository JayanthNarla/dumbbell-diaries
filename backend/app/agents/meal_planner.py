import os
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from langgraph.graph import END, StateGraph
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json
import datetime


class MealPlanRequest(BaseModel):
    """Meal plan request model"""
    user_id: str
    goal_type: str  # weight_loss, muscle_gain, maintenance
    daily_calories: Optional[int] = None
    diet_type: Optional[str] = None  # vegan, vegetarian, keto, etc.
    allergies: Optional[List[str]] = None
    excluded_foods: Optional[List[str]] = None
    preferred_foods: Optional[List[str]] = None
    meals_per_day: Optional[int] = 3


class Meal(BaseModel):
    """Meal model"""
    name: str
    calories: int
    protein: float
    carbs: float
    fat: float
    ingredients: List[str]
    recipe: Optional[str] = None
    preparation_time: Optional[int] = None  # in minutes


class DailyMealPlan(BaseModel):
    """Daily meal plan model"""
    day: int
    meals: List[Meal]
    total_calories: int
    total_protein: float
    total_carbs: float
    total_fat: float


class MealPlan(BaseModel):
    """Meal plan model"""
    title: str
    description: str
    daily_plans: List[DailyMealPlan]
    duration_days: int
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)


class MealPlannerState(BaseModel):
    """State for the meal planner agent"""
    request: MealPlanRequest
    intermediate_steps: List[Dict[str, Any]] = Field(default_factory=list)
    meal_plan: Optional[MealPlan] = None


# Define the LangGraph agent
def create_meal_planner_agent():
    """Create a meal planner agent using LangGraph"""
    
    # Define the meal planning prompt
    meal_planning_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert nutritionist specialized in creating personalized meal plans.
        Create a detailed meal plan based on the user's goals, dietary preferences, and requirements.
        
        The meal plan should include:
        1. A title for the plan
        2. A brief description explaining the benefits and focus of the plan
        3. A list of meals for each day, for a 7-day period
        4. Each meal should include a name, ingredients, calories, and macronutrients
        5. Ensure the daily caloric and macronutrient targets are met
        
        Format your response as valid JSON with the following structure:
        {
            "title": "Plan Title",
            "description": "Plan description",
            "daily_plans": [
                {
                    "day": 1,
                    "meals": [
                        {
                            "name": "Meal name",
                            "calories": 500,
                            "protein": 30,
                            "carbs": 50,
                            "fat": 15,
                            "ingredients": ["ingredient 1", "ingredient 2"],
                            "recipe": "Brief preparation instructions",
                            "preparation_time": 20
                        }
                    ],
                    "total_calories": 2000,
                    "total_protein": 120,
                    "total_carbs": 180,
                    "total_fat": 60
                }
            ],
            "duration_days": 7
        }
        """),
        ("human", "Create a meal plan for a user with the following details: {request_json}")
    ])
    
    # Define the nodes for the graph
    def generate_meal_plan(state: MealPlannerState) -> MealPlannerState:
        """Generate meal plan based on the request"""
        request_json = state.request.json()
        response = meal_planning_prompt.invoke({"request_json": request_json})
        parsed_response = StrOutputParser().invoke(response)
        
        try:
            # Extract the JSON part from the response
            meal_plan_data = json.loads(parsed_response)
            
            # Create a meal plan
            meal_plan = MealPlan(
                title=meal_plan_data["title"],
                description=meal_plan_data["description"],
                daily_plans=meal_plan_data["daily_plans"],
                duration_days=meal_plan_data["duration_days"]
            )
            
            state.meal_plan = meal_plan
            state.intermediate_steps.append({"action": "generate_meal_plan", "result": "success"})
        except Exception as e:
            state.intermediate_steps.append({"action": "generate_meal_plan", "result": "error", "error": str(e)})
        
        return state
    
    # Build the graph
    workflow = StateGraph(MealPlannerState)
    
    # Add the nodes
    workflow.add_node("generate_meal_plan", generate_meal_plan)
    
    # Define the edges
    workflow.add_edge("generate_meal_plan", END)
    
    # Set the entry point
    workflow.set_entry_point("generate_meal_plan")
    
    # Compile the graph
    return workflow.compile()


# Function to generate a meal plan
async def generate_meal_plan(request: MealPlanRequest) -> MealPlan:
    """
    Generate a meal plan using the LangGraph agent.
    
    Args:
        request: Meal plan request
        
    Returns:
        Generated meal plan
    """
    # Create the agent
    agent = create_meal_planner_agent()
    
    # Initialize the state
    state = MealPlannerState(request=request)
    
    # Run the agent
    result = agent.invoke(state)
    
    # Extract and return the meal plan
    return result.meal_plan
