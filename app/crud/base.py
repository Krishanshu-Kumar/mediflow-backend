from typing import Any, TypeVar, Optional, List, Type
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from uuid import UUID

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


def get_by_id(
    db: Session,
    model_cls: Type[ModelType],
    id_val: Any,
) -> Optional[ModelType]:
    return db.query(model_cls).filter(getattr(model_cls, "id") == id_val).first()



def get_multi(
    db: Session,
    model_cls: Type[ModelType],
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
) -> List[ModelType]:
    query = db.query(model_cls)
    if active_only and hasattr(model_cls, "is_active"):
        query = query.filter(getattr(model_cls, "is_active"))
    return query.offset(skip).limit(limit).all()


def update_fields(
    db: Session,
    model_cls: Type[ModelType],
    id_val: Any,
    **fields: Any,
) -> Optional[ModelType]:
    instance = get_by_id(db, model_cls, id_val)
    if not instance:
        return None
    apply_updates(instance, fields)
    return commit_refresh(db, instance)


def update_instance(
    db: Session,
    model_cls: Type[ModelType],
    id_val: Any,
    update_schema: Any,
    updated_by: Optional[UUID] = None,
) -> Optional[ModelType]:
    update_data = schema_to_dict(update_schema, exclude_unset=True)
    if updated_by:
        update_data["updated_by"] = updated_by
    return update_fields(db, model_cls, id_val, **update_data)


def create_instance(
    db: Session,
    model_cls: Type[ModelType],
    create_schema: Any,
    created_by: Optional[UUID] = None,
) -> ModelType:
    data = schema_to_dict(create_schema)
    if created_by:
        data["created_by"] = created_by
    instance = model_cls(**data)
    db.add(instance)
    return commit_refresh(db, instance)

