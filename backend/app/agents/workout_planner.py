import os
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from langgraph.graph import END, StateGraph
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json
import datetime


class WorkoutRecommendationRequest(BaseModel):
    """Workout recommendation request model"""
    user_id: str
    goal_type: str  # weight_loss, muscle_gain, endurance, etc.
    fitness_level: str  # beginner, intermediate, advanced
    available_equipment: Optional[List[str]] = None
    preferred_workout_duration: Optional[int] = None  # in minutes
    frequency: Optional[int] = None  # workouts per week
    restrictions: Optional[List[str]] = None  # injuries, limitations
    preferences: Optional[List[str]] = None  # preferred workout types


class WorkoutPlan(BaseModel):
    """Workout plan model"""
    title: str
    description: str
    workouts: List[Dict[str, Any]]
    duration_weeks: int
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)


class WorkoutPlannerState(BaseModel):
    """State for the workout planner agent"""
    request: WorkoutRecommendationRequest
    intermediate_steps: List[Dict[str, Any]] = Field(default_factory=list)
    workout_plan: Optional[WorkoutPlan] = None


# Define the LangGraph agent
def create_workout_planner_agent():
    """Create a workout planner agent using LangGraph"""
    
    # Define the workout planning prompt
    workout_planning_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert fitness trainer specialized in creating personalized workout plans.
        Create a detailed workout plan based on the user's goals, fitness level, and preferences.
        
        The workout plan should include:
        1. A title for the plan
        2. A brief description explaining the benefits and focus of the plan
        3. A list of workouts for each day, spread across a recommended number of weeks
        4. Each workout should include exercises, sets, reps, and rest periods
        5. Progressive overload should be incorporated over the weeks
        
        Format your response as valid JSON with the following structure:
        {
            "title": "Plan Title",
            "description": "Plan description",
            "workouts": [
                {
                    "day": 1,
                    "name": "Workout name",
                    "focus": "Area of focus",
                    "duration": "Estimated duration in minutes",
                    "exercises": [
                        {
                            "name": "Exercise name",
                            "sets": 3,
                            "reps": 10,
                            "rest": "Rest period in seconds",
                            "notes": "Optional notes or form tips"
                        }
                    ]
                }
            ],
            "duration_weeks": 4
        }
        """),
        ("human", "Create a workout plan for a user with the following details: {request_json}")
    ])
    
    # Define the nodes for the graph
    def generate_workout_plan(state: WorkoutPlannerState) -> WorkoutPlannerState:
        """Generate workout plan based on the request"""
        request_json = state.request.json()
        response = workout_planning_prompt.invoke({"request_json": request_json})
        parsed_response = StrOutputParser().invoke(response)
        
        try:
            # Extract the JSON part from the response
            workout_plan_data = json.loads(parsed_response)
            
            # Create a workout plan
            workout_plan = WorkoutPlan(
                title=workout_plan_data["title"],
                description=workout_plan_data["description"],
                workouts=workout_plan_data["workouts"],
                duration_weeks=workout_plan_data["duration_weeks"]
            )
            
            state.workout_plan = workout_plan
            state.intermediate_steps.append({"action": "generate_workout_plan", "result": "success"})
        except Exception as e:
            state.intermediate_steps.append({"action": "generate_workout_plan", "result": "error", "error": str(e)})
        
        return state
    
    # Build the graph
    workflow = StateGraph(WorkoutPlannerState)
    
    # Add the nodes
    workflow.add_node("generate_workout_plan", generate_workout_plan)
    
    # Define the edges
    workflow.add_edge("generate_workout_plan", END)
    
    # Set the entry point
    workflow.set_entry_point("generate_workout_plan")
    
    # Compile the graph
    return workflow.compile()


# Function to generate a workout plan
async def generate_workout_plan(request: WorkoutRecommendationRequest) -> WorkoutPlan:
    """
    Generate a workout plan using the LangGraph agent.
    
    Args:
        request: Workout recommendation request
        
    Returns:
        Generated workout plan
    """
    # Create the agent
    agent = create_workout_planner_agent()
    
    # Initialize the state
    state = WorkoutPlannerState(request=request)
    
    # Run the agent
    result = agent.invoke(state)
    
    # Extract and return the workout plan
    return result.workout_plan
