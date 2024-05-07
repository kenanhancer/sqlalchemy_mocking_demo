from sqlalchemy.orm import Session
from src.models import Order


class OrderRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_customer_orders(self, customer_id: int):

        orders = self.session.query(Order).filter(Order.customer_id == 101).all()

        return orders
