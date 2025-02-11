"""
to activate virtual environment on Windows:
> Set-ExecutionPolicy Unrestricted -Scope Process
to create npm install on Windows:
> Set-ExecutionPolicy Restricted -Scope CurrentUser
to use npm on Windows:
> Set-ExecutionPolicy Unrestricted -Scope CurrentUser
"""
import logging
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List
from fastapi.requests import Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

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
    suggested_answer: List
    index_answer: int
    subject: str


def default_subject():
    return ["Algebra", "Arithmetic", "Trigonometry", "Geometry"]


class ChooseSubject(BaseModel):
    subjects: Optional[List[Optional[str]]] = default_subject()
    latex: Optional[bool] = True


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
        return templates.TemplateResponse(f'index.html', {'request': req})

if __name__ == '__main__':
    uvicorn.run(app)
