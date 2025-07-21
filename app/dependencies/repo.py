from app.repositories.stock_repo import StockRepo

def get_repo() -> StockRepo:
    return StockRepo() 