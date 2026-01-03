from sqlalchemy.orm import sessionmaker
from models import Game, Supplier
from core.db import engine

SessionLocal = sessionmaker(bind=engine)


def seed_data():
    session = SessionLocal()
    
    try:
        game = session.query(Game).filter_by(id=1).first()
        if not game:
            game = Game(id=1, name="One Piece")
            session.add(game)
            print(f"Created Game: {game.name} (id={game.id})")
        else:
            print(f"Game with id=1 already exists: {game.name}")
        
        supplier = session.query(Supplier).filter_by(id=1).first()
        if not supplier:
            supplier = Supplier(id=1, name="Liga")
            session.add(supplier)
            print(f"Created Supplier: {supplier.name} (id={supplier.id})")
        else:
            print(f"Supplier with id=1 already exists: {supplier.name}")
        
        session.commit()
        print("Seed data successfully added!")
        
    except Exception as e:
        session.rollback()
        print(f"Error seeding data: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_data()

