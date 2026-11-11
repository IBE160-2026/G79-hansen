from fastapi import APIRouter

from app.contracts.learning import DemoFixture, DemoRequest, LearningBundle
from app.services.demo import generate_demo, get_fixture

router = APIRouter(prefix="/api/v1/demo", tags=["fixed demo"])


@router.get("/fixture", response_model=DemoFixture)
def fixture() -> DemoFixture:
    return get_fixture()


@router.post("/generate", response_model=LearningBundle)
def generate(request: DemoRequest) -> LearningBundle:
    # Request validation permits only the named fixture and schema version.
    return generate_demo()
