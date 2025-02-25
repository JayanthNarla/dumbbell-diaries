import asyncio
from datetime import datetime, timedelta, timezone, UTC
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

# MongoDB connection string from .env
MONGODB_URI = "mongodb+srv://dumbbelldiariesofficial:DBD!aries25@dumbbelldiaries.838zh.mongodb.net/?retryWrites=true&w=majority&appName=dumbbelldiaries"
DB_NAME = "dumbbell_diaries"

# Sample data
users_data = [
    {
        "_id": ObjectId(),
        "email": "john.doe@example.com",
        "username": "johndoe",
        "full_name": "John Doe",
        "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewFX1FKFAQNkbBvq",  # password: test123
        "is_active": True,
        "is_admin": True,  # First user is admin
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "profile_picture": "https://example.com/profiles/john.jpg",
        "bio": "Fitness enthusiast, love weightlifting and CrossFit",
        "following": [],
        "followers": []
    },
    {
        "_id": ObjectId(),
        "email": "jane.smith@example.com",
        "username": "janesmith",
        "full_name": "Jane Smith",
        "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewFX1FKFAQNkbBvq",
        "is_active": True,
        "is_admin": False,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "profile_picture": "https://example.com/profiles/jane.jpg",
        "bio": "Yoga instructor and nutrition coach",
        "following": [],
        "followers": []
    },
    {
        "_id": ObjectId(),
        "email": "mike.wilson@example.com",
        "username": "mikewilson",
        "full_name": "Mike Wilson",
        "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewFX1FKFAQNkbBvq",
        "is_active": True,
        "is_admin": False,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "profile_picture": "https://example.com/profiles/mike.jpg",
        "bio": "Powerlifting enthusiast | Personal Trainer",
        "following": [],
        "followers": []
    },
    {
        "_id": ObjectId(),
        "email": "sarah.lee@example.com",
        "username": "sarahlee",
        "full_name": "Sarah Lee",
        "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewFX1FKFAQNkbBvq",
        "is_active": True,
        "is_admin": False,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "profile_picture": "https://example.com/profiles/sarah.jpg",
        "bio": "Running coach | Marathon finisher | Plant-based athlete",
        "following": [],
        "followers": []
    },
    {
        "_id": ObjectId(),
        "email": "alex.brown@example.com",
        "username": "alexbrown",
        "full_name": "Alex Brown",
        "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewFX1FKFAQNkbBvq",
        "is_active": True,
        "is_admin": False,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "profile_picture": "https://example.com/profiles/alex.jpg",
        "bio": "Calisthenics & Street Workout | Teaching bodyweight mastery",
        "following": [],
        "followers": []
    },
    {
        "_id": ObjectId(),
        "email": "emma.taylor@example.com",
        "username": "emmataylor",
        "full_name": "Emma Taylor",
        "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewFX1FKFAQNkbBvq",
        "is_active": True,
        "is_admin": False,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "profile_picture": "https://example.com/profiles/emma.jpg",
        "bio": "HIIT & Dance Fitness Instructor | Making fitness fun!",
        "following": [],
        "followers": []
    },
    {
        "_id": ObjectId(),
        "email": "david.chen@example.com",
        "username": "davidchen",
        "full_name": "David Chen",
        "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewFX1FKFAQNkbBvq",
        "is_active": True,
        "is_admin": False,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "profile_picture": "https://example.com/profiles/david.jpg",
        "bio": "Olympic Weightlifting | National Competitor | Coach",
        "following": [],
        "followers": []
    }
]

workouts_data = [
    {
        "_id": ObjectId(),
        "user_id": users_data[0]["_id"],  # John's workout
        "title": "Full Body Strength Training",
        "description": "Complete full body workout focusing on compound movements",
        "duration": 3600,  # 1 hour in seconds
        "calories_burned": 500,
        "exercises": [
            {
                "name": "Barbell Squat",
                "sets": 4,
                "reps": 8,
                "weight": 100,
                "notes": "Focus on form and depth"
            },
            {
                "name": "Bench Press",
                "sets": 4,
                "reps": 8,
                "weight": 80,
                "notes": "Keep elbows tucked"
            }
        ],
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "date": datetime.now(UTC),
        "is_public": True,
        "likes": [],
        "comments": []
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[1]["_id"],  # Jane's workout
        "title": "Yoga Flow and Meditation",
        "description": "Gentle yoga flow followed by guided meditation",
        "duration": 2700,  # 45 minutes in seconds
        "calories_burned": 200,
        "exercises": [
            {
                "name": "Sun Salutation",
                "sets": 3,
                "duration": 300,  # 5 minutes
                "notes": "Flow with breath"
            },
            {
                "name": "Warrior Sequence",
                "sets": 2,
                "duration": 600,  # 10 minutes
                "notes": "Hold each pose for 5 breaths"
            }
        ],
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "date": datetime.now(UTC) - timedelta(days=1),
        "is_public": True,
        "likes": [],
        "comments": []
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[2]["_id"],  # Mike's workout
        "title": "Power Lifting Session",
        "description": "Heavy lifting day focusing on deadlifts and accessories",
        "duration": 4500,  # 75 minutes in seconds
        "calories_burned": 600,
        "exercises": [
            {
                "name": "Deadlift",
                "sets": 5,
                "reps": 5,
                "weight": 160,
                "notes": "Progressive sets, last set AMRAP"
            },
            {
                "name": "Romanian Deadlift",
                "sets": 3,
                "reps": 12,
                "weight": 100,
                "notes": "Focus on hamstring stretch"
            }
        ],
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "date": datetime.now(UTC) - timedelta(days=2),
        "is_public": True,
        "likes": [],
        "comments": []
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[3]["_id"],  # Sarah's workout
        "title": "Marathon Training Run",
        "description": "Long distance endurance run with intervals",
        "duration": 7200,  # 2 hours in seconds
        "calories_burned": 800,
        "exercises": [
            {
                "name": "Warm-up Jog",
                "duration": 600,  # 10 minutes
                "notes": "Easy pace to warm up"
            },
            {
                "name": "Distance Run",
                "duration": 5400,  # 90 minutes
                "notes": "Maintain steady pace with 1-minute sprints every 10 minutes"
            }
        ],
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "date": datetime.now(UTC) - timedelta(days=3),
        "is_public": True,
        "likes": [],
        "comments": []
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[4]["_id"],  # Alex's workout
        "title": "Calisthenics Skills",
        "description": "Advanced bodyweight movements and skill work",
        "duration": 3600,  # 1 hour in seconds
        "calories_burned": 400,
        "exercises": [
            {
                "name": "Handstand Practice",
                "sets": 5,
                "duration": 60,  # 1 minute holds
                "notes": "Focus on balance and alignment"
            },
            {
                "name": "Muscle Up Progression",
                "sets": 4,
                "reps": 3,
                "notes": "Clean form over quantity"
            }
        ],
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "date": datetime.now(UTC) - timedelta(days=1),
        "is_public": True,
        "likes": [],
        "comments": []
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[5]["_id"],  # Emma's workout
        "title": "Dance HIIT Fusion",
        "description": "High-energy dance cardio with HIIT intervals",
        "duration": 2700,  # 45 minutes in seconds
        "calories_burned": 450,
        "exercises": [
            {
                "name": "Dance Warmup",
                "duration": 300,  # 5 minutes
                "notes": "Dynamic stretching with music"
            },
            {
                "name": "HIIT Dance Intervals",
                "sets": 4,
                "duration": 300,  # 5 minutes each
                "notes": "30 seconds intense, 30 seconds recovery"
            }
        ],
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "date": datetime.now(UTC) - timedelta(days=1),
        "is_public": True,
        "likes": [],
        "comments": []
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[6]["_id"],  # David's workout
        "title": "Olympic Lifting Technique",
        "description": "Technical session focusing on clean and jerk",
        "duration": 5400,  # 90 minutes in seconds
        "calories_burned": 500,
        "exercises": [
            {
                "name": "Clean Technique",
                "sets": 6,
                "reps": 3,
                "weight": 80,
                "notes": "Focus on pull under bar"
            },
            {
                "name": "Jerk Practice",
                "sets": 6,
                "reps": 2,
                "weight": 70,
                "notes": "Work on split position"
            }
        ],
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "date": datetime.now(UTC) - timedelta(days=2),
        "is_public": True,
        "likes": [],
        "comments": []
    }
]

food_logs_data = [
    {
        "_id": ObjectId(),
        "user_id": users_data[0]["_id"],  # John's food log
        "date": datetime.now(UTC),
        "meals": [
            {
                "meal_type": "breakfast",
                "foods": [
                    {
                        "name": "Oatmeal with Berries",
                        "serving_size": 100,
                        "serving_unit": "grams",
                        "calories": 350,
                        "protein": 12,
                        "carbs": 60,
                        "fat": 8
                    },
                    {
                        "name": "Protein Shake",
                        "serving_size": 300,
                        "serving_unit": "ml",
                        "calories": 150,
                        "protein": 25,
                        "carbs": 5,
                        "fat": 2
                    }
                ],
                "notes": "Pre-workout breakfast"
            }
        ],
        "total_calories": 500,
        "total_protein": 37,
        "total_carbs": 65,
        "total_fat": 10,
        "water_intake": 500,
        "notes": "Feeling energetic",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[1]["_id"],  # Jane's food log
        "date": datetime.now(UTC),
        "meals": [
            {
                "meal_type": "lunch",
                "foods": [
                    {
                        "name": "Quinoa Buddha Bowl",
                        "serving_size": 350,
                        "serving_unit": "grams",
                        "calories": 450,
                        "protein": 15,
                        "carbs": 70,
                        "fat": 12
                    },
                    {
                        "name": "Green Smoothie",
                        "serving_size": 400,
                        "serving_unit": "ml",
                        "calories": 200,
                        "protein": 5,
                        "carbs": 40,
                        "fat": 3
                    }
                ],
                "notes": "Post-yoga lunch"
            }
        ],
        "total_calories": 650,
        "total_protein": 20,
        "total_carbs": 110,
        "total_fat": 15,
        "water_intake": 750,
        "notes": "Feeling refreshed after yoga",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[2]["_id"],  # Mike's food log
        "date": datetime.now(UTC),
        "meals": [
            {
                "meal_type": "dinner",
                "foods": [
                    {
                        "name": "Grilled Chicken Breast",
                        "serving_size": 200,
                        "serving_unit": "grams",
                        "calories": 330,
                        "protein": 62,
                        "carbs": 0,
                        "fat": 7
                    },
                    {
                        "name": "Sweet Potato",
                        "serving_size": 200,
                        "serving_unit": "grams",
                        "calories": 180,
                        "protein": 2,
                        "carbs": 41,
                        "fat": 0
                    }
                ],
                "notes": "Post-workout meal"
            }
        ],
        "total_calories": 510,
        "total_protein": 64,
        "total_carbs": 41,
        "total_fat": 7,
        "water_intake": 1000,
        "notes": "High protein dinner after lifting",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[3]["_id"],  # Sarah's food log
        "date": datetime.now(UTC),
        "meals": [
            {
                "meal_type": "breakfast",
                "foods": [
                    {
                        "name": "Whole Grain Toast with Avocado",
                        "serving_size": 2,
                        "serving_unit": "slices",
                        "calories": 320,
                        "protein": 8,
                        "carbs": 35,
                        "fat": 18
                    },
                    {
                        "name": "Plant-based Protein Smoothie",
                        "serving_size": 500,
                        "serving_unit": "ml",
                        "calories": 250,
                        "protein": 20,
                        "carbs": 30,
                        "fat": 5
                    }
                ],
                "notes": "Pre-run fuel"
            }
        ],
        "total_calories": 570,
        "total_protein": 28,
        "total_carbs": 65,
        "total_fat": 23,
        "water_intake": 800,
        "notes": "Plant-based pre-run breakfast",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[4]["_id"],  # Alex's food log
        "date": datetime.now(UTC),
        "meals": [
            {
                "meal_type": "lunch",
                "foods": [
                    {
                        "name": "Tuna Salad",
                        "serving_size": 250,
                        "serving_unit": "grams",
                        "calories": 280,
                        "protein": 35,
                        "carbs": 8,
                        "fat": 14
                    },
                    {
                        "name": "Mixed Nuts",
                        "serving_size": 30,
                        "serving_unit": "grams",
                        "calories": 180,
                        "protein": 6,
                        "carbs": 6,
                        "fat": 16
                    }
                ],
                "notes": "Light lunch before calisthenics"
            }
        ],
        "total_calories": 460,
        "total_protein": 41,
        "total_carbs": 14,
        "total_fat": 30,
        "water_intake": 600,
        "notes": "Keeping it light for afternoon training",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[5]["_id"],  # Emma's food log
        "date": datetime.now(UTC),
        "meals": [
            {
                "meal_type": "snack",
                "foods": [
                    {
                        "name": "Greek Yogurt with Honey",
                        "serving_size": 200,
                        "serving_unit": "grams",
                        "calories": 180,
                        "protein": 18,
                        "carbs": 20,
                        "fat": 5
                    },
                    {
                        "name": "Banana",
                        "serving_size": 1,
                        "serving_unit": "piece",
                        "calories": 105,
                        "protein": 1,
                        "carbs": 27,
                        "fat": 0
                    }
                ],
                "notes": "Pre-dance class snack"
            }
        ],
        "total_calories": 285,
        "total_protein": 19,
        "total_carbs": 47,
        "total_fat": 5,
        "water_intake": 400,
        "notes": "Quick energy boost before class",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[6]["_id"],  # David's food log
        "date": datetime.now(UTC),
        "meals": [
            {
                "meal_type": "dinner",
                "foods": [
                    {
                        "name": "Salmon Fillet",
                        "serving_size": 200,
                        "serving_unit": "grams",
                        "calories": 412,
                        "protein": 46,
                        "carbs": 0,
                        "fat": 28
                    },
                    {
                        "name": "Brown Rice",
                        "serving_size": 150,
                        "serving_unit": "grams",
                        "calories": 165,
                        "protein": 3,
                        "carbs": 35,
                        "fat": 1
                    }
                ],
                "notes": "Recovery meal after training"
            }
        ],
        "total_calories": 577,
        "total_protein": 49,
        "total_carbs": 35,
        "total_fat": 29,
        "water_intake": 900,
        "notes": "Post-Olympic lifting dinner",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    }
]

measurements_data = [
    {
        "_id": ObjectId(),
        "user_id": users_data[0]["_id"],  # John's measurements
        "date": datetime.now(UTC),
        "weight": 80.5,  # in kg
        "height": 180.0,  # in cm
        "body_fat": 15.0,  # percentage
        "chest": 100.0,  # in cm
        "waist": 85.0,
        "hips": 95.0,
        "arms": {"left": 35.0, "right": 35.5},
        "legs": {"left": 60.0, "right": 60.0},
        "notes": "Monthly measurement check-in",
        "photo_urls": ["https://example.com/progress/john_1.jpg"],
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[1]["_id"],  # Jane's measurements
        "date": datetime.now(UTC),
        "weight": 65.0,
        "height": 165.0,
        "body_fat": 20.0,
        "chest": 90.0,
        "waist": 70.0,
        "hips": 95.0,
        "arms": {"left": 28.0, "right": 28.0},
        "legs": {"left": 55.0, "right": 55.0},
        "notes": "Post-yoga measurement",
        "photo_urls": ["https://example.com/progress/jane_1.jpg"],
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[2]["_id"],  # Mike's measurements
        "date": datetime.now(UTC),
        "weight": 95.0,
        "height": 185.0,
        "body_fat": 12.0,
        "chest": 110.0,
        "waist": 90.0,
        "hips": 100.0,
        "arms": {"left": 42.0, "right": 42.5},
        "legs": {"left": 65.0, "right": 65.0},
        "notes": "Bulking phase measurements",
        "photo_urls": ["https://example.com/progress/mike_1.jpg"],
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[3]["_id"],  # Sarah's measurements
        "date": datetime.now(UTC),
        "weight": 58.0,
        "height": 170.0,
        "body_fat": 18.0,
        "chest": 85.0,
        "waist": 65.0,
        "hips": 90.0,
        "arms": {"left": 27.0, "right": 27.0},
        "legs": {"left": 52.0, "right": 52.0},
        "notes": "Pre-marathon measurements",
        "photo_urls": ["https://example.com/progress/sarah_1.jpg"],
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[4]["_id"],  # Alex's measurements
        "date": datetime.now(UTC),
        "weight": 75.0,
        "height": 175.0,
        "body_fat": 10.0,
        "chest": 98.0,
        "waist": 80.0,
        "hips": 92.0,
        "arms": {"left": 33.0, "right": 33.0},
        "legs": {"left": 58.0, "right": 58.0},
        "notes": "Lean and maintaining for calisthenics",
        "photo_urls": ["https://example.com/progress/alex_1.jpg"],
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[5]["_id"],  # Emma's measurements
        "date": datetime.now(UTC),
        "weight": 62.0,
        "height": 168.0,
        "body_fat": 19.0,
        "chest": 88.0,
        "waist": 68.0,
        "hips": 92.0,
        "arms": {"left": 29.0, "right": 29.0},
        "legs": {"left": 54.0, "right": 54.0},
        "notes": "Dance fitness progress check",
        "photo_urls": ["https://example.com/progress/emma_1.jpg"],
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[6]["_id"],  # David's measurements
        "date": datetime.now(UTC),
        "weight": 85.0,
        "height": 178.0,
        "body_fat": 13.0,
        "chest": 105.0,
        "waist": 83.0,
        "hips": 98.0,
        "arms": {"left": 38.0, "right": 38.0},
        "legs": {"left": 62.0, "right": 62.0},
        "notes": "Olympic lifting competition prep measurements",
        "photo_urls": ["https://example.com/progress/david_1.jpg"],
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    }
]

workout_templates_data = [
    {
        "_id": ObjectId(),
        "name": "Beginner Full Body Strength",
        "description": "A balanced full-body workout for beginners",
        "difficulty": "beginner",
        "estimated_duration": 45,  # minutes
        "category": "strength",
        "exercises": [
            {
                "api_exercise_id": "0001",  # Reference to external API exercise ID
                "name": "Barbell Back Squat",  # Cache the name for quick reference
                "sets": 3,
                "reps": 10,
                "rest": 90,  # seconds
                "notes": "Focus on form over weight"
            },
            {
                "api_exercise_id": "0002",  # Reference to external API exercise ID
                "name": "Push-ups",  # Cache the name for quick reference
                "sets": 3,
                "reps": 12,
                "rest": 60,
                "notes": "Modify on knees if needed"
            }
        ],
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "created_by": users_data[0]["_id"],  # Created by John
        "is_public": True,
        "likes_count": 0,
        "tags": ["beginner", "strength", "full-body"]
    },
    {
        "_id": ObjectId(),
        "name": "Yoga Flow for Flexibility",
        "description": "Gentle yoga sequence focusing on flexibility and mindfulness",
        "difficulty": "intermediate",
        "estimated_duration": 60,
        "category": "yoga",
        "exercises": [
            {
                "api_exercise_id": "y001",
                "name": "Sun Salutation A",
                "sets": 3,
                "duration": 300,
                "rest": 30,
                "notes": "Flow with breath"
            },
            {
                "api_exercise_id": "y002",
                "name": "Hip Opening Series",
                "duration": 600,
                "notes": "Hold each pose for 5-10 breaths"
            }
        ],
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "created_by": users_data[1]["_id"],
        "is_public": True,
        "likes_count": 0,
        "tags": ["yoga", "flexibility", "mindfulness"]
    },
    {
        "_id": ObjectId(),
        "name": "Olympic Lifting Basics",
        "description": "Introduction to Olympic weightlifting movements",
        "difficulty": "intermediate",
        "estimated_duration": 75,
        "category": "olympic_weightlifting",
        "exercises": [
            {
                "api_exercise_id": "o001",
                "name": "Clean Pull",
                "sets": 5,
                "reps": 3,
                "rest": 120,
                "notes": "Focus on extension and pull under"
            },
            {
                "api_exercise_id": "o002",
                "name": "Jerk Balance",
                "sets": 4,
                "reps": 5,
                "rest": 90,
                "notes": "Practice split position"
            }
        ],
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "created_by": users_data[6]["_id"],
        "is_public": True,
        "likes_count": 0,
        "tags": ["olympic lifting", "technique", "strength"]
    },
    {
        "_id": ObjectId(),
        "name": "5K Training Run",
        "description": "Structured running workout for 5K preparation",
        "difficulty": "intermediate",
        "estimated_duration": 40,
        "category": "cardio",
        "exercises": [
            {
                "api_exercise_id": "r001",
                "name": "Warm-up Jog",
                "duration": 600,
                "notes": "Easy pace to warm up"
            },
            {
                "api_exercise_id": "r002",
                "name": "Speed Intervals",
                "sets": 8,
                "duration": 200,
                "rest": 100,
                "notes": "80% max effort"
            }
        ],
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "created_by": users_data[3]["_id"],
        "is_public": True,
        "likes_count": 0,
        "tags": ["running", "cardio", "intervals"]
    },
    {
        "_id": ObjectId(),
        "name": "Bodyweight Mastery",
        "description": "Advanced calisthenics skill development",
        "difficulty": "advanced",
        "estimated_duration": 60,
        "category": "calisthenics",
        "exercises": [
            {
                "api_exercise_id": "c001",
                "name": "Handstand Practice",
                "sets": 5,
                "duration": 60,
                "rest": 60,
                "notes": "Focus on alignment and balance"
            },
            {
                "api_exercise_id": "c002",
                "name": "Planche Progression",
                "sets": 4,
                "duration": 30,
                "rest": 90,
                "notes": "Use resistance bands if needed"
            }
        ],
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "created_by": users_data[4]["_id"],
        "is_public": True,
        "likes_count": 0,
        "tags": ["calisthenics", "bodyweight", "skills"]
    },
    {
        "_id": ObjectId(),
        "name": "Dance HIIT Blast",
        "description": "High-intensity dance workout for cardio and fun",
        "difficulty": "intermediate",
        "estimated_duration": 30,
        "category": "cardio",
        "exercises": [
            {
                "api_exercise_id": "d001",
                "name": "Dance Warm-up",
                "duration": 300,
                "notes": "Dynamic stretching with music"
            },
            {
                "api_exercise_id": "d002",
                "name": "Cardio Dance Intervals",
                "sets": 6,
                "duration": 180,
                "rest": 60,
                "notes": "Follow the beat and keep intensity high"
            }
        ],
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "created_by": users_data[5]["_id"],
        "is_public": True,
        "likes_count": 0,
        "tags": ["dance", "hiit", "cardio"]
    },
    {
        "_id": ObjectId(),
        "name": "Power Lifting Focus",
        "description": "Strength training focused on the big three lifts",
        "difficulty": "advanced",
        "estimated_duration": 90,
        "category": "strength",
        "exercises": [
            {
                "api_exercise_id": "p001",
                "name": "Competition Squat",
                "sets": 5,
                "reps": 5,
                "rest": 180,
                "notes": "Focus on competition form"
            },
            {
                "api_exercise_id": "p002",
                "name": "Competition Bench",
                "sets": 5,
                "reps": 5,
                "rest": 180,
                "notes": "Practice commands"
            }
        ],
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "created_by": users_data[2]["_id"],
        "is_public": True,
        "likes_count": 0,
        "tags": ["powerlifting", "strength", "competition"]
    }
]

goals_data = [
    {
        "_id": ObjectId(),
        "user_id": users_data[0]["_id"],  # John's weight loss goal
        "title": "Summer Weight Loss Challenge",
        "description": "Lose 10kg through a combination of strength training and cardio",
        "goal_type": "weight",
        "target_value": 75.0,  # target weight in kg
        "start_value": 85.0,
        "current_value": 82.5,
        "target_date": datetime.now(UTC) + timedelta(days=90),
        "status": "in_progress",
        "progress_history": [
            {"date": datetime.now(UTC) - timedelta(days=30), "value": 85.0},
            {"date": datetime.now(UTC) - timedelta(days=15), "value": 83.8},
            {"date": datetime.now(UTC), "value": 82.5}
        ],
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[1]["_id"],  # Jane's body fat goal
        "title": "Body Recomposition Goal",
        "description": "Reduce body fat percentage while maintaining muscle mass",
        "goal_type": "body_fat",
        "target_value": 18.0,  # target body fat percentage
        "start_value": 22.0,
        "current_value": 20.5,
        "target_date": datetime.now(UTC) + timedelta(days=120),
        "status": "in_progress",
        "progress_history": [
            {"date": datetime.now(UTC) - timedelta(days=45), "value": 22.0},
            {"date": datetime.now(UTC) - timedelta(days=30), "value": 21.2},
            {"date": datetime.now(UTC), "value": 20.5}
        ],
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[2]["_id"],  # Mike's strength goal
        "title": "Powerlifting PR Challenge",
        "description": "Increase deadlift max to 200kg",
        "goal_type": "workout",
        "target_value": 200.0,  # target deadlift weight in kg
        "start_value": 160.0,
        "current_value": 175.0,
        "target_date": datetime.now(UTC) + timedelta(days=180),
        "status": "in_progress",
        "custom_data": {
            "exercise": "deadlift",
            "training_frequency": "3x per week",
            "program": "5/3/1"
        },
        "progress_history": [
            {"date": datetime.now(UTC) - timedelta(days=60), "value": 160.0},
            {"date": datetime.now(UTC) - timedelta(days=30), "value": 170.0},
            {"date": datetime.now(UTC), "value": 175.0}
        ],
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[3]["_id"],  # Sarah's marathon goal
        "title": "First Marathon Completion",
        "description": "Complete a full marathon under 4 hours",
        "goal_type": "custom",
        "target_date": datetime.now(UTC) + timedelta(days=150),
        "status": "not_started",
        "custom_data": {
            "distance": "42.2km",
            "target_time": "4:00:00",
            "training_plan": "16-week marathon program",
            "weekly_mileage": "50km"
        },
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[4]["_id"],  # Alex's nutrition goal
        "title": "Clean Eating Challenge",
        "description": "Maintain a balanced macro ratio and hit daily protein targets",
        "goal_type": "nutrition",
        "target_value": 180.0,  # daily protein target in grams
        "start_value": 120.0,
        "current_value": 150.0,
        "target_date": datetime.now(UTC) + timedelta(days=30),
        "status": "in_progress",
        "custom_data": {
            "protein_target": "180g",
            "carb_target": "250g",
            "fat_target": "70g",
            "meals_per_day": 5
        },
        "progress_history": [
            {"date": datetime.now(UTC) - timedelta(days=14), "value": 120.0},
            {"date": datetime.now(UTC) - timedelta(days=7), "value": 135.0},
            {"date": datetime.now(UTC), "value": 150.0}
        ],
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[5]["_id"],  # Emma's flexibility goal
        "title": "Advanced Flexibility Achievement",
        "description": "Achieve full splits and advanced yoga poses",
        "goal_type": "measurement",
        "target_date": datetime.now(UTC) + timedelta(days=240),
        "status": "in_progress",
        "custom_data": {
            "poses": ["front splits", "middle splits", "scorpion pose"],
            "flexibility_metrics": {
                "hip_flexor": "current: 145°, target: 180°",
                "hamstring": "current: touch toes, target: palms flat"
            },
            "training_frequency": "5x per week"
        },
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[6]["_id"],  # David's completed goal
        "title": "Olympic Lifting Certification",
        "description": "Complete Level 1 Olympic Weightlifting certification",
        "goal_type": "custom",
        "target_date": datetime.now(UTC) - timedelta(days=30),
        "status": "completed",
        "custom_data": {
            "certification_type": "USAW Level 1",
            "requirements": [
                "Clean & Jerk proficiency",
                "Snatch proficiency",
                "Coaching methodology",
                "Program design"
            ],
            "completion_date": str(datetime.now(UTC) - timedelta(days=30))
        },
        "created_at": datetime.now(UTC) - timedelta(days=90),
        "updated_at": datetime.now(UTC) - timedelta(days=30)
    }
]

social_posts_data = [
    {
        "_id": ObjectId(),
        "user_id": users_data[0]["_id"],  # John's post
        "content": "Hit a new PR on squats today! 💪 Finally reached 150kg for 3 reps. Hard work pays off! #fitness #gains #strengthtraining",
        "media_urls": ["https://example.com/posts/john_squat.jpg", "https://example.com/posts/john_squat_video.mp4"],
        "workout_id": workouts_data[0]["_id"],  # Reference to his workout
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "likes": [users_data[1]["_id"], users_data[2]["_id"], users_data[4]["_id"]],  # Multiple users liked
        "comments": [
            {
                "user_id": users_data[1]["_id"],
                "content": "Amazing progress! Keep it up! 🎉",
                "created_at": datetime.now(UTC)
            },
            {
                "user_id": users_data[2]["_id"],
                "content": "Beast mode activated! What's your next target?",
                "created_at": datetime.now(UTC)
            }
        ]
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[1]["_id"],  # Jane's post
        "content": "Morning yoga session complete 🧘‍♀️ Today's focus was on mindfulness and flexibility. Sharing my favorite flow sequence for stress relief. #yoga #mindfulness #wellness",
        "media_urls": ["https://example.com/posts/jane_yoga.jpg", "https://example.com/posts/jane_yoga_tutorial.mp4"],
        "workout_id": workouts_data[1]["_id"],
        "created_at": datetime.now(UTC) - timedelta(hours=2),
        "updated_at": datetime.now(UTC) - timedelta(hours=2),
        "likes": [users_data[0]["_id"], users_data[3]["_id"], users_data[5]["_id"]],
        "comments": [
            {
                "user_id": users_data[5]["_id"],
                "content": "Love this flow! Can you share more details about the sequence?",
                "created_at": datetime.now(UTC) - timedelta(hours=1)
            }
        ]
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[2]["_id"],  # Mike's post
        "content": "Powerlifting meet prep going strong 💪 Today's deadlift session was brutal but satisfying. Form check on my last set - any tips from fellow lifters? #powerlifting #deadlift #formcheck",
        "media_urls": ["https://example.com/posts/mike_deadlift.mp4"],
        "workout_id": workouts_data[2]["_id"],
        "created_at": datetime.now(UTC) - timedelta(hours=4),
        "updated_at": datetime.now(UTC) - timedelta(hours=4),
        "likes": [users_data[0]["_id"], users_data[6]["_id"]],
        "comments": [
            {
                "user_id": users_data[6]["_id"],
                "content": "Looking solid! Try keeping your lats a bit tighter at the start.",
                "created_at": datetime.now(UTC) - timedelta(hours=3)
            }
        ]
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[3]["_id"],  # Sarah's post
        "content": "Marathon training update: Completed my longest run yet - 32km! 🏃‍♀️ Feeling stronger every week. Plant-based pre-run meal made all the difference. #running #marathon #plantbased",
        "media_urls": ["https://example.com/posts/sarah_run_stats.jpg", "https://example.com/posts/sarah_meal.jpg"],
        "workout_id": workouts_data[3]["_id"],
        "created_at": datetime.now(UTC) - timedelta(hours=6),
        "updated_at": datetime.now(UTC) - timedelta(hours=6),
        "likes": [users_data[1]["_id"], users_data[4]["_id"], users_data[5]["_id"]],
        "comments": [
            {
                "user_id": users_data[1]["_id"],
                "content": "Would love to know your pre-run meal recipe! 🌱",
                "created_at": datetime.now(UTC) - timedelta(hours=5)
            }
        ]
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[4]["_id"],  # Alex's post
        "content": "Finally nailed the muscle-up! 🔥 6 months of dedicated practice paying off. Swipe for progression videos and tips. #calisthenics #muscleup #streetworkout",
        "media_urls": [
            "https://example.com/posts/alex_muscleup.mp4",
            "https://example.com/posts/alex_progression1.mp4",
            "https://example.com/posts/alex_progression2.mp4"
        ],
        "workout_id": workouts_data[4]["_id"],
        "created_at": datetime.now(UTC) - timedelta(hours=8),
        "updated_at": datetime.now(UTC) - timedelta(hours=8),
        "likes": [users_data[0]["_id"], users_data[2]["_id"], users_data[6]["_id"]],
        "comments": [
            {
                "user_id": users_data[2]["_id"],
                "content": "Insane progress! Those progression videos are super helpful 👊",
                "created_at": datetime.now(UTC) - timedelta(hours=7)
            }
        ]
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[5]["_id"],  # Emma's post
        "content": "New dance HIIT routine dropping next week! 💃 Here's a sneak peek of the choreography. Music: 'Energy Boost' by FitBeats #dancefit #hiit #groupfitness",
        "media_urls": ["https://example.com/posts/emma_dance_preview.mp4"],
        "workout_id": workouts_data[5]["_id"],
        "created_at": datetime.now(UTC) - timedelta(hours=10),
        "updated_at": datetime.now(UTC) - timedelta(hours=10),
        "likes": [users_data[1]["_id"], users_data[3]["_id"]],
        "comments": [
            {
                "user_id": users_data[3]["_id"],
                "content": "Can't wait for this! Your routines are always so fun 🎵",
                "created_at": datetime.now(UTC) - timedelta(hours=9)
            }
        ]
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[6]["_id"],  # David's post
        "content": "Olympic lifting workshop recap! 🏋️‍♂️ Covered clean & jerk technique with some amazing athletes today. Swipe for key teaching points and common mistakes to avoid. #olympicweightlifting #coaching #technique",
        "media_urls": [
            "https://example.com/posts/david_workshop1.jpg",
            "https://example.com/posts/david_workshop2.jpg",
            "https://example.com/posts/david_technique.mp4"
        ],
        "workout_id": workouts_data[6]["_id"],
        "created_at": datetime.now(UTC) - timedelta(hours=12),
        "updated_at": datetime.now(UTC) - timedelta(hours=12),
        "likes": [users_data[0]["_id"], users_data[2]["_id"], users_data[4]["_id"]],
        "comments": [
            {
                "user_id": users_data[2]["_id"],
                "content": "Great tips! When's the next workshop?",
                "created_at": datetime.now(UTC) - timedelta(hours=11)
            },
            {
                "user_id": users_data[0]["_id"],
                "content": "Those technique breakdowns are gold! 🏆",
                "created_at": datetime.now(UTC) - timedelta(hours=10)
            }
        ]
    }
]

notifications_data = [
    {
        "_id": ObjectId(),
        "user_id": users_data[0]["_id"],  # Notification for John
        "type": "like",
        "title": "New Like",
        "message": "Jane Smith and 2 others liked your workout post",
        "is_read": False,
        "created_at": datetime.now(UTC),
        "metadata": {
            "post_id": social_posts_data[0]["_id"],
            "liker_ids": [users_data[1]["_id"], users_data[2]["_id"], users_data[4]["_id"]]
        }
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[1]["_id"],  # Notification for Jane
        "type": "goal_achieved",
        "title": "Goal Milestone Reached! 🎉",
        "message": "You're halfway to your body recomposition goal! Keep up the great work!",
        "is_read": True,
        "created_at": datetime.now(UTC) - timedelta(hours=2),
        "metadata": {
            "goal_id": goals_data[1]["_id"],
            "progress_percentage": 50,
            "current_value": 20.5,
            "target_value": 18.0
        }
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[2]["_id"],  # Notification for Mike
        "type": "comment",
        "title": "New Comment on Your Post",
        "message": "David Chen commented on your deadlift form check",
        "is_read": False,
        "created_at": datetime.now(UTC) - timedelta(hours=3),
        "metadata": {
            "post_id": social_posts_data[2]["_id"],
            "comment_id": ObjectId(),
            "commenter_id": users_data[6]["_id"]
        }
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[3]["_id"],  # Notification for Sarah
        "type": "workout_reminder",
        "title": "Marathon Training Reminder",
        "message": "Time for your scheduled long run! Weather forecast: Sunny, 18°C",
        "is_read": False,
        "created_at": datetime.now(UTC) - timedelta(hours=1),
        "metadata": {
            "workout_template_id": workout_templates_data[0]["_id"],
            "scheduled_time": str(datetime.now(UTC) + timedelta(hours=1)),
            "weather_data": {
                "condition": "sunny",
                "temperature": 18,
                "humidity": 65
            }
        }
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[4]["_id"],  # Notification for Alex
        "type": "achievement_unlocked",
        "title": "New Achievement Unlocked! 💪",
        "message": "Consistency Champion: You've worked out 30 days in a row!",
        "is_read": False,
        "created_at": datetime.now(UTC) - timedelta(hours=4),
        "metadata": {
            "achievement_type": "workout_streak",
            "streak_days": 30,
            "points_earned": 100,
            "badge_url": "https://example.com/badges/streak_30.png"
        }
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[5]["_id"],  # Notification for Emma
        "type": "follow",
        "title": "New Followers",
        "message": "Sarah Lee and 2 others started following you",
        "is_read": False,
        "created_at": datetime.now(UTC) - timedelta(hours=5),
        "metadata": {
            "follower_ids": [users_data[3]["_id"], users_data[1]["_id"], users_data[4]["_id"]],
            "follower_names": ["Sarah Lee", "Jane Smith", "Alex Brown"]
        }
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[6]["_id"],  # Notification for David
        "type": "nutrition_reminder",
        "title": "Nutrition Check-In",
        "message": "You haven't logged your meals today. Stay on track with your nutrition goals!",
        "is_read": False,
        "created_at": datetime.now(UTC) - timedelta(hours=6),
        "metadata": {
            "last_log_time": str(datetime.now(UTC) - timedelta(days=1)),
            "missed_meals": ["breakfast", "lunch"],
            "daily_targets": {
                "calories": 2800,
                "protein": 180,
                "current_progress": {
                    "calories": 0,
                    "protein": 0
                }
            }
        }
    }
]

device_tokens_data = [
    {
        "_id": ObjectId(),
        "user_id": users_data[0]["_id"],  # John's device
        "device_token": "fMk9iGN5TzKqV3wX7yL2Ej4H",
        "device_type": "ios",
        "is_active": True,
        "app_version": "2.1.0",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "last_used": datetime.now(UTC)
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[1]["_id"],  # Jane's device
        "device_token": "bPn8jKm4RwCt2vY5xQ9Zs3F",
        "device_type": "android",
        "is_active": True,
        "app_version": "2.0.1",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "last_used": datetime.now(UTC)
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[2]["_id"],  # Mike's device
        "device_token": "hWq6gBd9MzNx4cA7vU8Ry5T",
        "device_type": "web",
        "is_active": True,
        "app_version": "1.9.0",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "last_used": datetime.now(UTC)
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[3]["_id"],  # Sarah's primary device
        "device_token": "kDm5pJf2HtGw8nE3xB6Vy9S",
        "device_type": "ios",
        "is_active": True,
        "app_version": "2.1.0",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "last_used": datetime.now(UTC)
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[3]["_id"],  # Sarah's secondary device
        "device_token": "rLc4sXa7YuNm1wP9tQ5Bh6J",
        "device_type": "web",
        "is_active": True,
        "app_version": "2.0.0",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "last_used": datetime.now(UTC)
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[4]["_id"],  # Alex's device
        "device_token": "mZx3vKn8WqFt5yH2cR7Uj4G",
        "device_type": "android",
        "is_active": True,
        "app_version": "2.1.0",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "last_used": datetime.now(UTC)
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[5]["_id"],  # Emma's device
        "device_token": "tNp7wJc5VqBm3sY8xL4Dk2H",
        "device_type": "ios",
        "is_active": True,
        "app_version": "2.1.0",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "last_used": datetime.now(UTC)
    }
]

notification_settings_data = [
    {
        "_id": ObjectId(),
        "user_id": users_data[0]["_id"],  # John's notification settings
        "push_enabled": True,  # Master toggle for push notifications
        "email_enabled": True,  # Master toggle for email notifications
        "notification_types": {
            "likes": {"push": True, "email": False},
            "comments": {"push": True, "email": True},
            "follows": {"push": True, "email": True},
            "goal_reminders": {"push": True, "email": True},
            "workout_reminders": {"push": True, "email": False},
            "achievement_alerts": {"push": True, "email": True}
        },
        "quiet_hours": {
            "enabled": True,
            "start": "22:00",  # 10 PM
            "end": "07:00"     # 7 AM
        },
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[1]["_id"],  # Jane's notification settings
        "push_enabled": True,
        "email_enabled": False,
        "notification_types": {
            "likes": {"push": True, "email": False},
            "comments": {"push": True, "email": False},
            "follows": {"push": True, "email": False},
            "goal_reminders": {"push": True, "email": False},
            "workout_reminders": {"push": True, "email": False},
            "achievement_alerts": {"push": True, "email": False}
        },
        "quiet_hours": {
            "enabled": True,
            "start": "23:00",  # 11 PM
            "end": "06:00"     # 6 AM
        },
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[2]["_id"],  # Mike's notification settings
        "push_enabled": True,
        "email_enabled": True,
        "notification_types": {
            "likes": {"push": False, "email": True},
            "comments": {"push": True, "email": True},
            "follows": {"push": False, "email": True},
            "goal_reminders": {"push": True, "email": True},
            "workout_reminders": {"push": True, "email": True},
            "achievement_alerts": {"push": True, "email": True}
        },
        "quiet_hours": {
            "enabled": False,
            "start": "00:00",
            "end": "06:00"
        },
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[3]["_id"],  # Sarah's notification settings
        "push_enabled": True,
        "email_enabled": True,
        "notification_types": {
            "likes": {"push": True, "email": False},
            "comments": {"push": True, "email": True},
            "follows": {"push": True, "email": False},
            "goal_reminders": {"push": True, "email": True},
            "workout_reminders": {"push": True, "email": True},
            "achievement_alerts": {"push": False, "email": True}
        },
        "quiet_hours": {
            "enabled": True,
            "start": "21:00",  # 9 PM
            "end": "05:00"     # 5 AM (early runner)
        },
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[4]["_id"],  # Alex's notification settings
        "push_enabled": True,
        "email_enabled": False,
        "notification_types": {
            "likes": {"push": True, "email": False},
            "comments": {"push": True, "email": False},
            "follows": {"push": True, "email": False},
            "goal_reminders": {"push": True, "email": False},
            "workout_reminders": {"push": False, "email": False},
            "achievement_alerts": {"push": True, "email": False}
        },
        "quiet_hours": {
            "enabled": False,
            "start": "00:00",
            "end": "00:00"
        },
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[5]["_id"],  # Emma's notification settings
        "push_enabled": True,
        "email_enabled": True,
        "notification_types": {
            "likes": {"push": True, "email": True},
            "comments": {"push": True, "email": True},
            "follows": {"push": True, "email": True},
            "goal_reminders": {"push": False, "email": True},
            "workout_reminders": {"push": True, "email": True},
            "achievement_alerts": {"push": True, "email": True}
        },
        "quiet_hours": {
            "enabled": True,
            "start": "22:30",  # 10:30 PM
            "end": "06:30"     # 6:30 AM
        },
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[6]["_id"],  # David's notification settings
        "push_enabled": True,
        "email_enabled": True,
        "notification_types": {
            "likes": {"push": False, "email": True},
            "comments": {"push": True, "email": True},
            "follows": {"push": False, "email": True},
            "goal_reminders": {"push": True, "email": True},
            "workout_reminders": {"push": True, "email": False},
            "achievement_alerts": {"push": True, "email": True}
        },
        "quiet_hours": {
            "enabled": True,
            "start": "21:30",  # 9:30 PM
            "end": "04:30"     # 4:30 AM (early training)
        },
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    }
]

exercise_library_data = [
    {
        "_id": ObjectId(),
        "name": "Custom Resistance Band HIIT",
        "category": "cardio",
        "equipment": ["resistance bands"],
        "difficulty": "intermediate",
        "description": "A custom HIIT workout combining resistance bands with bodyweight exercises",
        "instructions": [
            "Start with resistance band around ankles",
            "Perform lateral jumps with band tension",
            "Move into squat position with band resistance",
            "Add arm pulls while in squat",
            "Repeat sequence for desired duration"
        ],
        "muscles_targeted": ["full body", "legs", "core", "shoulders"],
        "video_url": "https://example.com/exercises/custom_band_hiit.mp4",
        "created_by": users_data[0]["_id"],  # Created by John
        "is_custom": True,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    },
    {
        "_id": ObjectId(),
        "name": "Zen Flow Sequence",
        "category": "yoga",
        "equipment": ["yoga mat", "yoga blocks"],
        "difficulty": "intermediate",
        "description": "A custom-designed flow combining traditional yoga with modern mobility work",
        "instructions": [
            "Begin in child's pose with blocks",
            "Flow into modified sun salutation",
            "Incorporate mobility work for hips",
            "Add balance poses with block support",
            "End with custom meditation pose"
        ],
        "muscles_targeted": ["full body", "core", "flexibility", "balance"],
        "video_url": "https://example.com/exercises/zen_flow.mp4",
        "created_by": users_data[1]["_id"],  # Created by Jane
        "is_custom": True,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    },
    {
        "_id": ObjectId(),
        "name": "Power Clean Progression",
        "category": "olympic_weightlifting",
        "equipment": ["barbell", "bumper plates"],
        "difficulty": "advanced",
        "description": "Progressive training sequence for mastering the power clean",
        "instructions": [
            "Start with deadlift position",
            "Practice pull to hip complex",
            "Add explosive triple extension",
            "Work on catch position",
            "Combine movements into full power clean"
        ],
        "muscles_targeted": ["full body", "posterior chain", "shoulders", "traps"],
        "video_url": "https://example.com/exercises/power_clean.mp4",
        "created_by": users_data[6]["_id"],  # Created by David
        "is_custom": True,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    },
    {
        "_id": ObjectId(),
        "name": "Marathon Prep Run",
        "category": "cardio",
        "equipment": ["running shoes"],
        "difficulty": "intermediate",
        "description": "Structured long-distance run with pace variations",
        "instructions": [
            "10-minute easy warm-up",
            "30 minutes at marathon pace",
            "5 x 2-minute tempo intervals",
            "15 minutes steady state",
            "5-minute cool down"
        ],
        "muscles_targeted": ["legs", "cardiovascular", "core"],
        "video_url": "https://example.com/exercises/marathon_prep.mp4",
        "created_by": users_data[3]["_id"],  # Created by Sarah
        "is_custom": True,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    },
    {
        "_id": ObjectId(),
        "name": "Advanced Ring Routine",
        "category": "calisthenics",
        "equipment": ["gymnastic rings"],
        "difficulty": "advanced",
        "description": "Comprehensive ring workout for upper body strength",
        "instructions": [
            "Ring support hold warm-up",
            "False grip practice",
            "Ring rows progression",
            "Ring dip sequence",
            "Muscle-up preparation"
        ],
        "muscles_targeted": ["upper body", "core", "grip strength"],
        "video_url": "https://example.com/exercises/ring_routine.mp4",
        "created_by": users_data[4]["_id"],  # Created by Alex
        "is_custom": True,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    },
    {
        "_id": ObjectId(),
        "name": "Dance Cardio Fusion",
        "category": "cardio",
        "equipment": [],
        "difficulty": "intermediate",
        "description": "High-energy dance routine combining multiple styles",
        "instructions": [
            "Dynamic dance warm-up",
            "Hip-hop cardio sequence",
            "Latin dance intervals",
            "HIIT dance combinations",
            "Cool-down stretches"
        ],
        "muscles_targeted": ["full body", "core", "legs", "cardio"],
        "video_url": "https://example.com/exercises/dance_fusion.mp4",
        "created_by": users_data[5]["_id"],  # Created by Emma
        "is_custom": True,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    },
    {
        "_id": ObjectId(),
        "name": "Powerlifting Technique Series",
        "category": "strength",
        "equipment": ["barbell", "power rack", "bench"],
        "difficulty": "advanced",
        "description": "Technical breakdown of the main powerlifting movements",
        "instructions": [
            "Squat setup and execution",
            "Bench press technique",
            "Deadlift positioning",
            "Bracing patterns",
            "Competition commands practice"
        ],
        "muscles_targeted": ["full body", "posterior chain", "chest", "core"],
        "video_url": "https://example.com/exercises/powerlifting_tech.mp4",
        "created_by": users_data[2]["_id"],  # Created by Mike
        "is_custom": True,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    }
]



achievements_data = [
    {
        "_id": ObjectId(),
        "user_id": users_data[0]["_id"],  # John's achievements
        "achievements": [
            {
                "type": "workout_streak",
                "name": "7-Day Warrior",
                "description": "Completed workouts 7 days in a row",
                "earned_at": datetime.now(UTC) - timedelta(days=2),
                "progress": 7,
                "target": 7,
                "icon_url": "https://example.com/achievements/streak_7.png"
            },
            {
                "type": "weight_goal",
                "name": "First Goal Reached",
                "description": "Reached your first weight goal",
                "earned_at": datetime.now(UTC) - timedelta(days=5),
                "progress": 1,
                "target": 1,
                "icon_url": "https://example.com/achievements/goal_1.png"
            }
        ],
        "total_points": 200,
        "current_streak": 7,
        "longest_streak": 14,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[1]["_id"],  # Jane's achievements
        "achievements": [
            {
                "type": "class_completion",
                "name": "Yoga Master",
                "description": "Completed 50 yoga sessions",
                "earned_at": datetime.now(UTC) - timedelta(days=1),
                "progress": 50,
                "target": 50,
                "icon_url": "https://example.com/achievements/yoga_50.png"
            }
        ],
        "total_points": 300,
        "current_streak": 15,
        "longest_streak": 20,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[2]["_id"],  # Mike's achievements
        "achievements": [
            {
                "type": "strength_milestone",
                "name": "Heavy Lifter",
                "description": "Deadlifted 200kg",
                "earned_at": datetime.now(UTC) - timedelta(days=3),
                "progress": 200,
                "target": 200,
                "icon_url": "https://example.com/achievements/deadlift_200.png"
            }
        ],
        "total_points": 400,
        "current_streak": 5,
        "longest_streak": 25,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[3]["_id"],  # Sarah's achievements
        "achievements": [
            {
                "type": "distance_milestone",
                "name": "Marathon Ready",
                "description": "Completed a 30km training run",
                "earned_at": datetime.now(UTC) - timedelta(days=2),
                "progress": 30,
                "target": 30,
                "icon_url": "https://example.com/achievements/run_30k.png"
            }
        ],
        "total_points": 350,
        "current_streak": 12,
        "longest_streak": 30,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[4]["_id"],  # Alex's achievements
        "achievements": [
        {
            "type": "skill_mastery",
            "name": "Bodyweight Master",
            "description": "Achieved first muscle-up",
            "earned_at": datetime.now(UTC) - timedelta(days=1),
            "progress": 1,
            "target": 1,
            "icon_url": "https://example.com/achievements/muscle_up.png"
        },
        ],
        "total_points": 250,
        "current_streak": 8,
        "longest_streak": 15,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[5]["_id"],  # Emma's achievements
        "achievements": [
            {
                "type": "instructor_milestone",
                "name": "Class Leader",
                "description": "Led 100 dance fitness classes",
                "earned_at": datetime.now(UTC) - timedelta(days=4),
                "progress": 100,
                "target": 100,
                "icon_url": "https://example.com/achievements/classes_100.png"
            }
        ],
        "total_points": 450,
        "current_streak": 20,
        "longest_streak": 35,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    },
    {
        "_id": ObjectId(),
        "user_id": users_data[6]["_id"],  # David's achievements
        "achievements": [
            {
                "type": "competition_achievement",
                "name": "Competition Champion",
                "description": "Won first place in Olympic lifting competition",
                "earned_at": datetime.now(UTC) - timedelta(days=7),
                "progress": 1,
                "target": 1,
                "icon_url": "https://example.com/achievements/competition_1st.png"
            }
        ],
        "total_points": 500,
        "current_streak": 10,
        "longest_streak": 40,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC)
    }
]

async def insert_dummy_data():
    """Insert dummy data into MongoDB collections."""
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DB_NAME]
    
    # Clear existing data
    await db.users.delete_many({})
    await db.workouts.delete_many({})
    await db.food_logs.delete_many({})
    await db.measurements.delete_many({})
    await db.goals.delete_many({})
    await db.social_posts.delete_many({})
    await db.notifications.delete_many({})
    await db.device_tokens.delete_many({})
    await db.notification_settings.delete_many({})
    await db.exercise_library.delete_many({})
    await db.workout_templates.delete_many({})
    await db.achievements.delete_many({})
    
    # Insert new data
    await db.users.insert_many(users_data)
    await db.workouts.insert_many(workouts_data)
    await db.food_logs.insert_many(food_logs_data)
    await db.measurements.insert_many(measurements_data)
    await db.goals.insert_many(goals_data)
    await db.social_posts.insert_many(social_posts_data)
    await db.notifications.insert_many(notifications_data)
    await db.device_tokens.insert_many(device_tokens_data)
    await db.notification_settings.insert_many(notification_settings_data)
    await db.exercise_library.insert_many(exercise_library_data)
    await db.workout_templates.insert_many(workout_templates_data)
    await db.achievements.insert_many(achievements_data)
    
    # Update user following/followers
    await db.users.update_one(
        {"_id": users_data[0]["_id"]},
        {"$set": {"following": [users_data[1]["_id"]], "followers": [users_data[1]["_id"]]}}
    )
    await db.users.update_one(
        {"_id": users_data[1]["_id"]},
        {"$set": {"following": [users_data[0]["_id"]], "followers": [users_data[0]["_id"]]}}
    )
    
    print("✅ Users inserted:", len(users_data))
    print("✅ Workouts inserted:", len(workouts_data))
    print("✅ Food logs inserted:", len(food_logs_data))
    print("✅ Measurements inserted:", len(measurements_data))
    print("✅ Goals inserted:", len(goals_data))
    print("✅ Social posts inserted:", len(social_posts_data))
    print("✅ Notifications inserted:", len(notifications_data))
    print("✅ Device tokens inserted:", len(device_tokens_data))
    print("✅ Notification settings inserted:", len(notification_settings_data))
    print("✅ Exercise library entries inserted:", len(exercise_library_data))
    print("✅ Workout templates inserted:", len(workout_templates_data))
    print("✅ User achievements inserted:", len(achievements_data))
    
    # Close the connection
    client.close()

if __name__ == "__main__":
    asyncio.run(insert_dummy_data()) 