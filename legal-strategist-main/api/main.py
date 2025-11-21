import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import ext_db
from routers.analyzer import router as analyze_router
from routers.auth import router as auth_router
from routers.case import router as case_router
from routers.extractor import router as extract_router
from routers.generator import router as generate_router
from routers.information import router as information_router
from routers.network import router as network_router
from routers.scrapper import router as scrapper_router
from routers.sender import router as send_router
from routers.simulator import router as simulate_router
from routers.suggester import router as suggest_router


logging.basicConfig(level=logging.INFO, format="%(levelname)s:\t  %(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.pool").setLevel(logging.ERROR)


@asynccontextmanager
async def lifespan(app: FastAPI):
    ext_db.init_db()
    yield


app = FastAPI(
    title="Estratega Legal | Titan Group",
    root_path="/v1",
    lifespan=lifespan,
    strict_slashes=False,
    openapi_tags=[
        {"name": "Analyze", "description": "Endpoints related to the analysis of information from documents or generated output."},
        {"name": "Auth", "description": "Endpoints related to user authentication and authorization."},
        {"name": "Case", "description": "Endpoints related to handling a case."},
        {"name": "Extract", "description": "Endpoints related to the extraction of information from documents or raw text."},
        {"name": "Generate", "description": "Endpoints related to the generation of documents."},
        {"name": "Information", "description": "Endpoints related to long term information."},
        {"name": "Network", "description": "Endpoints related to handling the request of other organization services."},
        {"name": "Scrapper", "description": "Endpoints related to scrapping information from external websites."},
        {"name": "Send", "description": "Endpoints related to sending information to third party services."},
        {"name": "Simulate", "description": "Endpoints related to the simulation of documents or case events."},
        {"name": "Suggest", "description": "Endpoints related to the suggestion of future steps to take in a case."},
    ],
)

origins = [
    "http://gpt-strategist.us-east-1.elasticbeanstalk.com:3002",
    "http://localhost:3002",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3002",
    "http://host.docker.internal:3000",
    "http://host.docker.internal:3002"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_router)
app.include_router(auth_router)
app.include_router(case_router)
app.include_router(extract_router)
app.include_router(generate_router)
app.include_router(information_router)
app.include_router(network_router)
app.include_router(scrapper_router)
app.include_router(send_router)
app.include_router(simulate_router)
app.include_router(suggest_router)
