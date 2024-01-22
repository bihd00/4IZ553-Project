from neo4j import Session
from fastapi import Depends
from typing import Generator
from typing import Annotated
from be.neo import driver


def get_db() -> Generator[Session, None, None]:
    db = driver.session()
    try:
        yield db
    finally:
        db.close()

SessionDep = Annotated[Session, Depends(get_db)]