import pytest
from datetime import datetime
from unittest.mock import MagicMock
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.models import Base, Order, Customer
from src.order_repository import OrderRepository
from alchemy_mock.mocking import UnifiedAlchemyMagicMock

import psycopg2

import collections
import collections.abc

# Alias the ABCs from collections.abc back to collections
collections.Mapping = collections.abc.Mapping


class TestRepository:
    @pytest.fixture
    def session_mock(self, mocker):
        session = mocker.MagicMock()
        session.query.return_value = session
        session.join.return_value = session
        session.filter.return_value = session
        return session

    @pytest.fixture
    def db_engine(self, postgresql):
        # Format the connection URL
        url = f"postgresql+psycopg2://{postgresql.info.user}:{postgresql.info.password}@{postgresql.info.host}:{postgresql.info.port}/{postgresql.info.dbname}"

        # SQLAlchemy engine creation using a creator function if needed
        engine = create_engine(
            "postgresql+psycopg2://",
            creator=lambda: psycopg2.connect(postgresql.info.dsn),
        )

        # Create a new session
        Session = sessionmaker(bind=engine)
        session = Session()

        # Create the schema if it does not exist
        session.execute(text("CREATE SCHEMA IF NOT EXISTS datamart"))
        session.commit()

        # Create all tables
        Base.metadata.create_all(engine)

        return engine

    @pytest.fixture
    def db_session(self, db_engine):
        """Creates a new database session for a test."""
        connection = db_engine.connect()
        transaction = connection.begin()
        session = sessionmaker(bind=connection)()
        yield session
        session.close()
        transaction.rollback()
        connection.close()

    def test_customer_orders(self, db_session):
        # Here you would add some customers and orders to the database
        customer = Customer(name="John Doe", email="john@example.com")
        db_session.add(customer)
        db_session.commit()

        order = Order(customer_id=customer.id, order_date="2023-05-01")
        db_session.add(order)
        db_session.commit()

        # Now test your repository or other business logic
        repo = OrderRepository(db_session)
        orders = repo.get_customer_orders(customer.id)
        assert len(orders) == 1
        assert orders[0].customer_id == customer.id

    @pytest.fixture
    def session(self) -> UnifiedAlchemyMagicMock:
        # Create a mock session
        session = UnifiedAlchemyMagicMock()

        # Setting up mock responses for specific queries
        # This will ensure that when the session queries orders of customer_id=101,
        # It returns the specified orders.
        session.add(
            [
                Order(id=201, customer_id=101, order_date=datetime(2023, 5, 1)),
                Order(id=202, customer_id=101, order_date=datetime(2023, 5, 2)),
            ],
        )

        return session

    def test_query_orders_by_customer2(self):
        session = UnifiedAlchemyMagicMock()

        session.add(Order(id=201, customer_id=101, order_date=datetime(2023, 5, 1)))
        session.add(Order(id=202, customer_id=101, order_date=datetime(2023, 5, 2)))
        dd = session.query(Order).all()
        print(dd)

        # # Configure the mock query to filter when executing the query
        # session.query(Order).filter(Order.customer_id == 101).all.return_value = [
        #     Order(id=201, customer_id=101, order_date=datetime(2023, 5, 1)),
        #     Order(id=202, customer_id=101, order_date=datetime(2023, 5, 2)),
        # ]

        # session.query(Order).filter(Order.customer_id == 101).all.return_value = [
        #     Order(id=201, customer_id=101, order_date=datetime(2023, 5, 1)),
        #     Order(id=202, customer_id=101, order_date=datetime(2023, 5, 2)),
        # ]

        # # Execution and Assertions (these parts remain unchanged)
        # result = session.query(Order).filter(Order.customer_id == 101).all()
        # assert len(result) == 2

    def test_query_orders_by_customer(self):
        # Create a mock session
        session = UnifiedAlchemyMagicMock()

        # Add mock customers
        customers = [
            Customer(id=101, name="John Doe", email="john@example.com"),
            Customer(id=102, name="Jane Smith", email="jane@example.com"),
            Customer(id=103, name="Jim Beam", email="jim@example.com"),
            Customer(id=104, name="Jack Daniels", email="jack@example.com"),
        ]

        # Add mock orders
        orders = [
            Order(id=201, customer_id=101, order_date=datetime(2023, 5, 1)),
            Order(id=202, customer_id=101, order_date=datetime(2023, 5, 2)),
            Order(id=203, customer_id=102, order_date=datetime(2023, 5, 3)),
        ]

        # Simulate adding these to the session
        for customer in customers:
            session.add(customer)
        for order in orders:
            session.add(order)

        result = session.query(Order).filter(Order.customer_id == 101).all()

        customer_id = 101

        order_repository = OrderRepository(session)

        orders = order_repository.get_customer_orders(customer_id)

        # Mock query: Fetch orders of customer_id=101
        result = session.query(Order).filter(Order.customer_id == 101).all()
        assert len(result) == 3  # Expecting 2 orders for customer 101

        # Mock query: Fetch orders for a non-existent customer
        result = session.query(Order).filter(Order.customer_id == 999).all()
        assert len(result) == 0  # Expecting no orders for customer 999

    def test_get_customer_orders(self, session_mock):
        mock_orders = [MagicMock(spec=Order) for _ in range(3)]

        session_mock.all.return_value = mock_orders

        order_repository = OrderRepository(session_mock)

        customer_id = 44
        orders = order_repository.get_customer_orders(customer_id)

        # Assertions
        assert orders == mock_orders
        session_mock.query.assert_called_once_with(Order)
        session_mock.join.assert_called_once_with(Customer)
        session_mock.filter.assert_called_once_with(Customer.id == customer_id)
        session_mock.all.assert_called_once()
