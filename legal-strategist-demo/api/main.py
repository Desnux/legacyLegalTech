import logging

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import ext_db
from routers.analyzer import (
    demand_text_analyzer,
)
from routers.auth import (
    token,
)
from routers.case import case
from routers.corrector import (
    demand_text_corrector,
)
from routers.extractor import (
    address_extractor,
    bill_extractor,
    demand_exception_extractor,
    demand_list_extractor,
    demand_text_extractor,
    demand_text_input_extractor,
    dispatch_resolution_extractor,
    promissory_note_extractor,
)
from routers.generator import (
    demand_exception_generator,
    demand_text_generator,
    dispatch_resolution_generator,
    missing_payment_argument_generator,
)
from routers.network import (
    chat,
    email,
)
from routers.scrapper import (
    digital_curators,
)
from routers.sender import (
    demand_sender,
    demand_text_sender,
)
from routers.simulator import case_simulator, chat_simulator
from routers.suggester import (
    demand_exception_suggester,
    dispatch_resolution_suggester,
)


logging.basicConfig(level=logging.INFO, format="%(levelname)s:\t  %(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.pool").setLevel(logging.ERROR)

@asynccontextmanager
async def lifespan(app: FastAPI):
    ext_db.init_db()
    yield

app = FastAPI(title="API de Estrategia Legal", root_path="/v1", lifespan=lifespan, strict_slashes=False)

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

app.include_router(demand_text_analyzer.router, prefix="/analyze")
app.include_router(token.router, prefix="/auth")
app.include_router(case.router, prefix="/case")
app.include_router(demand_text_corrector.router, prefix="/correct")
app.include_router(address_extractor.router, prefix="/extract")
app.include_router(bill_extractor.router, prefix="/extract")
app.include_router(demand_exception_extractor.router, prefix="/extract")
app.include_router(demand_list_extractor.router, prefix="/extract")
app.include_router(demand_text_extractor.router, prefix="/extract")
app.include_router(demand_text_input_extractor.router, prefix="/extract")
app.include_router(dispatch_resolution_extractor.router, prefix="/extract")
app.include_router(promissory_note_extractor.router, prefix="/extract")
app.include_router(demand_exception_generator.router, prefix="/generate")
app.include_router(demand_text_generator.router, prefix="/generate")
app.include_router(dispatch_resolution_generator.router, prefix="/generate")
app.include_router(missing_payment_argument_generator.router, prefix="/generate")
app.include_router(chat.router, prefix="/network")
app.include_router(email.router, prefix="/network")
app.include_router(digital_curators.router, prefix="/scrapper")
app.include_router(demand_sender.router, prefix="/send")
app.include_router(demand_text_sender.router, prefix="/send")
app.include_router(case_simulator.router, prefix="/simulate")
app.include_router(chat_simulator.router, prefix="/simulate")
app.include_router(demand_exception_suggester.router, prefix="/suggest")
app.include_router(dispatch_resolution_suggester.router, prefix="/suggest")
