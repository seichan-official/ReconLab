from sqlmodel import Session, select
from app.models.target import Target


def create_target(url: str, db: Session) -> Target:
    target = Target(url=url)
    db.add(target)
    db.commit()
    db.refresh(target)
    return target


def get_target(target_id: int, db: Session) -> Target | None:
    return db.exec(select(Target).where(Target.id == target_id)).first()


def list_targets(db: Session) -> list[Target]:
    return db.exec(select(Target)).all()


def delete_target(target_id: int, db: Session) -> bool:
    target = get_target(target_id, db)
    if not target:
        return False
    db.delete(target)
    db.commit()
    return True
