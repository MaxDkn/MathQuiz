"""
to activate virtual environment on Windows:
> Set-ExecutionPolicy Unrestricted -Scope Process
"""
from fastapi.requests import Request
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
import logging
from typing import Optional, List, Union
from pydantic import BaseModel, Field
import uvicorn
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from multiple_choice_quiz import generate_mcq_question

app = FastAPI()
logger = logging.getLogger('uvicorn.error')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow specified origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


class QuestionData(BaseModel):
    question: str
    index_answer: int
    suggested_answer: List
    subject: str


def default_subject():
    return ["Algebra", "Arithmetic", "Trigonometry", "Geometry"]


class ChooseSubject(BaseModel):
    subjects: Optional[List[Optional[str]]] = default_subject()
    latex: Optional[bool] = True


@app.post('/api/test')
async def testing_frontend():
    return {
        "question": "Quelle est la valeur de $\\cos^2(-\\frac{\\pi}{2})$ ?",
        "suggested_answer": ["$2(x+1) (x-2)$", "$\\dfrac{\\sqrt{2}}{2}$", "$\\sum_{i=4}^{10}(5i-1)^2$", "$\\dfrac{\\sqrt{x}}{y}$"],
        "index_answer": 0,
        "subject": "Trigonometry"
    }


@app.post('/api/generate', response_model=QuestionData)
async def generate_a_question(subjects: Optional[ChooseSubject]):
    return generate_mcq_question(**subjects.model_dump())


#  Deploy React application from the build
try:
    app.mount('/static', StaticFiles(directory="../ui/build/static"), 'static')
    templates = Jinja2Templates(directory="../ui/build")
except Exception as e:
    logger.warning(f'Cannot display react application ({e.__str__()}).')
else:
    logger.info('React App successfully found running on ["/"]')

    @app.get('/{rest_of_path:path}', tags=['React App'])
    async def react_app(req: Request, rest_of_path: str):
        return templates.TemplateResponse('index.html', {'request': req})

if __name__ == '__main__':
    uvicorn.run(app)
