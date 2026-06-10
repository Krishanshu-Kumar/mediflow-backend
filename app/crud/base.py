from typing import Any, TypeVar
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")


def schema_to_dict(schema: Any, **kwargs: Any) -> dict:
    if hasattr(schema, "model_dump"):
        return schema.model_dump(**kwargs)
    return schema.dict(**kwargs)


def commit_refresh(db: Session, model: ModelType) -> ModelType:
    try:
        db.commit()
        db.refresh(model)
        return model

    except IntegrityError:
        db.rollback()
        raise

    except SQLAlchemyError:
        db.rollback()
        raise


def apply_updates(model: ModelType, updates: dict) -> None:
    for key, value in updates.items():
        setattr(model, key, value)
