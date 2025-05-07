from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

class ClientProfile(BaseModel):
    age: int
    sex: str  # "male" or "female"
    height_cm: float
    weight_kg: float
    goal: str  # "fat_loss", "muscle_gain", "maintenance"
    activity_level: str  # "sedentary", "light", "moderate", "active", "very_active"
    diet_preference: str  # "none", "vegan", "keto", etc.
    workouts_per_week: int

class PlanResponse(BaseModel):
    calories: int
    macros: dict
    workout_plan: List[str]
    meal_plan: List[str]

def calculate_tdee(profile: ClientProfile) -> float:
    if profile.sex == "male":
        bmr = 10 * profile.weight_kg + 6.25 * profile.height_cm - 5 * profile.age + 5
    else:
        bmr = 10 * profile.weight_kg + 6.25 * profile.height_cm - 5 * profile.age - 161

    activity_multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9
    }
    multiplier = activity_multipliers.get(profile.activity_level, 1.2)
    return bmr * multiplier

def generate_macros(calories: float, profile: ClientProfile) -> dict:
    if profile.goal == "fat_loss":
        calories -= 500
    elif profile.goal == "muscle_gain":
        calories += 250

    protein = 2.2 * profile.weight_kg
    fats = 0.8 * profile.weight_kg
    protein_cals = protein * 4
    fat_cals = fats * 9
    carbs_cals = calories - (protein_cals + fat_cals)
    carbs = carbs_cals / 4

    return {
        "calories": int(calories),
        "protein_g": int(protein),
        "fats_g": int(fats),
        "carbs_g": int(carbs)
    }

def generate_workout_plan(profile: ClientProfile) -> List[str]:
    return [f"Day {i+1}: Full Body Strength Training" for i in range(profile.workouts_per_week)]

def generate_meal_plan(profile: ClientProfile) -> List[str]:
    if profile.diet_preference == "vegan":
        return ["Tofu stir-fry", "Quinoa salad", "Oatmeal with almond butter"]
    elif profile.diet_preference == "keto":
        return ["Bacon & eggs", "Avocado chicken salad", "Salmon with veggies"]
    else:
        return ["Grilled chicken & rice", "Greek yogurt with honey", "Steak with sweet potatoes"]

@app.post("/generate_plan", response_model=PlanResponse)
def generate_plan(profile: ClientProfile):
    try:
        calories = calculate_tdee(profile)
        macros = generate_macros(calories, profile)
        workout_plan = generate_workout_plan(profile)
        meal_plan = generate_meal_plan(profile)

        return PlanResponse(
            calories=macros["calories"],
            macros={
                "protein_g": macros["protein_g"],
                "fats_g": macros["fats_g"],
                "carbs_g": macros["carbs_g"]
            },
            workout_plan=workout_plan,
            meal_plan=meal_plan
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
