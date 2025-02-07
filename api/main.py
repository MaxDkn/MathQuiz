"""
to activate virtual environnement on Windows:
> Set-ExecutionPolicy Unrestricted -Scope Process
"""
from fastapi.requests import Request
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
import logging
from typing import Optional, List, Union
from pydantic import BaseModel
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
    answer: Union[bool, str, int]
    others_answers: Optional[List]
    subject: str
    response_type: str


class ChooseSubject(BaseModel):
    subjects: Optional[List[Optional[str]]] = ["Algebra", "Arithmetic", "Trigonometry", "Geometry"]


@app.post('/api/test')
async def testing_frontend():
    data = {
        "question": "Quelle est la valeur de $\cos^2(-\frac{\pi}{2})$ ?",
        "suggested_answer": ["$0$", "$\frac{\sqrt{2}}{2}$"],
        "index_answer": 0,
        "subject": "Trigonometry"
    }
    return ORJSONResponse(content=data)


@app.post('/api/test1')
async def testing_frontend(subjects: ChooseSubject):
    data = {
        "question": "Quelle est la valeur de \cos\left(-\frac{7\pi}{4}\right) ?",
        "suggested_answer": [
            r"\frac{\sqrt{2}}{2}",
            r"\frac{1}{2}",
            r"\frac{\sqrt{3}}{2}",
            r"-\frac{\sqrt{2}}{2}"
        ],
        "index_answer": 0,
        "subject": "Trigonometry"
    }
    return ORJSONResponse(content=data)


@app.post('/api/generate')
async def generate_a_question(subjects: ChooseSubject):
    return generate_mcq_question(**subjects.model_dump())


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
