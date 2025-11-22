"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },

    # Sports-related activities (2 added)
    "Soccer Team": {
        "description": "Competitive soccer training and matches",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 6:00 PM",
        "max_participants": 22,
        "participants": ["alex@mergington.edu", "natalie@mergington.edu"]
    },
    "Swimming Club": {
        "description": "Lap swimming, technique work, and occasional meets",
        "schedule": "Tuesdays and Thursdays, 5:00 PM - 6:30 PM",
        "max_participants": 18,
        "participants": ["tyler@mergington.edu", "mia@mergington.edu"]
    },

    # Artistic activities (2 added)
    "Art Club": {
        "description": "Drawing, painting, and mixed-media workshops",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 16,
        "participants": ["isabella@mergington.edu", "liam@mergington.edu"]
    },
    "Choir": {
        "description": "Vocal training and performances for all skill levels",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 40,
        "participants": ["ava@mergington.edu", "lucas@mergington.edu"]
    },

    # Intellectual activities (2 added)
    "Debate Team": {
        "description": "Learn argumentation, public speaking, and compete in debates",
        "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
        "max_participants": 14,
        "participants": ["henry@mergington.edu", "grace@mergington.edu"]
    },
    "Math Olympiad": {
        "description": "Problem solving and preparation for math competitions",
        "schedule": "Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["oliver@mergington.edu", "sophia2@mergington.edu"]
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Normalize email to avoid duplicates due to case/whitespace
    normalized_email = email.strip().lower()

    # Ensure participants list exists
    participants = activity.setdefault("participants", [])

    # Check for duplicate signup
    if normalized_email in (p.strip().lower() for p in participants):
        raise HTTPException(status_code=400, detail="Student is already signed up for this activity")

    # Enforce max participants if configured
    max_p = activity.get("max_participants")
    if isinstance(max_p, int) and len(participants) >= max_p:
        raise HTTPException(status_code=400, detail="Activity is full")

    # Validate student is not already signed up for another activity at the same time
    activity_schedule = activity.get("schedule")
    for other_activity_name, other_activity in activities.items():
        if other_activity_name == activity_name:
            continue
        if normalized_email in (p.strip().lower() for p in other_activity.get("participants", [])):
            if other_activity.get("schedule") == activity_schedule:
                raise HTTPException(
                    status_code=400,
                    detail=f"Student is already signed up for {other_activity_name} at the same time"
                )
    # Add student
    participants.append(normalized_email)
    return {"message": f"Signed up {normalized_email} for {activity_name}"}


@app.delete("/activities/{activity_name}/signup")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[activity_name]
    normalized_email = email.strip().lower()
    participants = activity.get("participants", [])

    # Find and remove participant
    for i, p in enumerate(participants):
        if p.strip().lower() == normalized_email:
            participants.pop(i)
            return {"message": f"Unregistered {normalized_email} from {activity_name}"}

    raise HTTPException(status_code=404, detail="Student not found in participants")
