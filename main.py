from fastapi import FastAPI, Depends, HTTPException, Request
from db import get_db_connection
from openai_client import generate_user_response
from openai_client import ai_agent
import traceback
import logging
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def render_homepage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/aboutus/", response_class=HTMLResponse)
async def about_us(request: Request):
    return templates.TemplateResponse("about_us.html", {"request":request})

@app.post("/query/")
def run_query(natural_query: str, request: Request, db=Depends(get_db_connection)):
    try:
        print(f"\nIncoming Query: {natural_query}")  # Log the input

        ai_response = ai_agent(natural_query)
        print(f"AI Response: {ai_response}")  # Log AI response

        if not ai_response.strip().upper().startswith(("SELECT", "WITH")):
            return {
                "query": None,
                "result": None,
                "human_response": ai_response
            }

        # If it's a SQL query, use DB
        cursor = db.cursor()
        cursor.execute(ai_response)
        columns = [column[0] for column in cursor.description] if cursor.description else []
        result = [dict(zip(columns, row)) for row in cursor.fetchall()] if columns else []
        human_response = generate_user_response(result if result else "No rows returned.")

        cursor.close()
        db.close()

        if not result:
            return {
                "query": ai_response,
                "result": "No data found.",
                "human_response": "No relevant data was found in the database."
            }

        return {
            "query": ai_response,
            "result": result,
            "human_response": human_response if human_response else "No summary available."
        }

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error occurred:\n{error_details}")  # Log the traceback
        return {
            "error": "Internal Server Error",
            "details": error_details
        }
