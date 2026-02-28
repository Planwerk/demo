"""Unit tests for ORM models (User and StatusUpdate)."""

import uuid
from typing import Any

import pytest
from sqlalchemy import inspect
from sqlalchemy.schema import ColumnDefault

from app.database import Base
from app.models.status import VALID_CATEGORIES, StatusUpdate
from app.models.user import User


class TestUserModel:
    """Tests for the User ORM model."""

    def test_user_inherits_from_base(self) -> None:
        assert issubclass(User, Base)

    def test_user_tablename(self) -> None:
        assert User.__tablename__ == "users"

    def test_user_columns_exist(self) -> None:
        mapper = inspect(User)
        column_names = {col.key for col in mapper.columns}
        expected = {
            "id",
            "username",
            "display_name",
            "email",
            "password_hash",
            "avatar_url",
            "xp",
            "current_streak",
            "longest_streak",
            "last_post_date",
            "created_at",
        }
        assert expected == column_names

    def test_user_id_is_uuid_primary_key(self) -> None:
        mapper = inspect(User)
        col = mapper.columns["id"]
        assert col.primary_key
        assert col.default is not None  # has a default (uuid4)

    def test_user_username_unique_not_nullable(self) -> None:
        mapper = inspect(User)
        col = mapper.columns["username"]
        assert col.unique
        assert not col.nullable

    def test_user_email_unique_not_nullable(self) -> None:
        mapper = inspect(User)
        col = mapper.columns["email"]
        assert col.unique
        assert not col.nullable

    def test_user_password_hash_not_nullable(self) -> None:
        mapper = inspect(User)
        col = mapper.columns["password_hash"]
        assert not col.nullable

    def test_user_avatar_url_nullable(self) -> None:
        mapper = inspect(User)
        col = mapper.columns["avatar_url"]
        assert col.nullable

    @pytest.mark.parametrize("column", ["xp", "current_streak", "longest_streak"])
    def test_user_counter_default_zero(self, column: str) -> None:
        mapper = inspect(User)
        col = mapper.columns[column]
        assert not col.nullable
        assert col.default is not None
        assert col.server_default is not None

    def test_user_last_post_date_nullable(self) -> None:
        mapper = inspect(User)
        col = mapper.columns["last_post_date"]
        assert col.nullable

    def test_user_created_at_not_nullable(self) -> None:
        mapper = inspect(User)
        col = mapper.columns["created_at"]
        assert not col.nullable
        assert col.server_default is not None

    def test_user_has_status_updates_relationship(self) -> None:
        mapper = inspect(User)
        assert "status_updates" in mapper.relationships

    def test_user_instantiation(self) -> None:
        user = User(
            username="alice",
            display_name="Alice",
            email="alice@example.com",
            password_hash="hashed",
        )
        assert user.username == "alice"
        assert user.display_name == "Alice"
        assert user.email == "alice@example.com"
        assert user.password_hash == "hashed"
        assert user.avatar_url is None
        assert user.last_post_date is None

    @pytest.mark.parametrize("column", ["xp", "current_streak", "longest_streak"])
    def test_user_counter_column_default_value(self, column: str) -> None:
        mapper = inspect(User)
        default = mapper.columns[column].default
        assert isinstance(default, ColumnDefault)
        arg: Any = default.arg
        assert arg == 0

    def test_user_repr(self) -> None:
        user = User(username="alice", display_name="Alice", email="a@b.com", password_hash="x")
        r = repr(user)
        assert "alice" in r
        assert "User" in r

    def test_user_index_on_username(self) -> None:
        mapper = inspect(User)
        col = mapper.columns["username"]
        assert col.index or col.unique  # unique implies an index

    def test_user_index_on_email(self) -> None:
        mapper = inspect(User)
        col = mapper.columns["email"]
        assert col.index or col.unique


class TestStatusUpdateModel:
    """Tests for the StatusUpdate ORM model."""

    def test_status_update_inherits_from_base(self) -> None:
        assert issubclass(StatusUpdate, Base)

    def test_status_update_tablename(self) -> None:
        assert StatusUpdate.__tablename__ == "status_updates"

    def test_status_update_columns_exist(self) -> None:
        mapper = inspect(StatusUpdate)
        column_names = {col.key for col in mapper.columns}
        expected = {"id", "user_id", "message", "category", "created_at"}
        assert expected == column_names

    def test_status_update_id_is_uuid_primary_key(self) -> None:
        mapper = inspect(StatusUpdate)
        col = mapper.columns["id"]
        assert col.primary_key
        assert col.default is not None

    def test_status_update_user_id_foreign_key(self) -> None:
        mapper = inspect(StatusUpdate)
        col = mapper.columns["user_id"]
        assert not col.nullable
        fk_targets = {fk.target_fullname for fk in col.foreign_keys}
        assert "users.id" in fk_targets

    def test_status_update_message_not_nullable(self) -> None:
        mapper = inspect(StatusUpdate)
        col = mapper.columns["message"]
        assert not col.nullable

    def test_status_update_category_not_nullable(self) -> None:
        mapper = inspect(StatusUpdate)
        col = mapper.columns["category"]
        assert not col.nullable

    def test_status_update_created_at_not_nullable(self) -> None:
        mapper = inspect(StatusUpdate)
        col = mapper.columns["created_at"]
        assert not col.nullable
        assert col.server_default is not None

    def test_status_update_has_user_relationship(self) -> None:
        mapper = inspect(StatusUpdate)
        assert "user" in mapper.relationships

    def test_status_update_user_id_indexed(self) -> None:
        mapper = inspect(StatusUpdate)
        col = mapper.columns["user_id"]
        assert col.index is True

    def test_status_update_instantiation(self) -> None:
        user_id = uuid.uuid4()
        status = StatusUpdate(
            user_id=user_id,
            message="Working on feature X",
            category="in-progress",
        )
        assert status.user_id == user_id
        assert status.message == "Working on feature X"
        assert status.category == "in-progress"

    def test_status_update_repr(self) -> None:
        status = StatusUpdate(
            user_id=uuid.uuid4(),
            message="Test",
            category="done",
        )
        r = repr(status)
        assert "StatusUpdate" in r

    def test_status_update_category_values(self) -> None:
        """Category column should accept the defined status values."""
        for category in VALID_CATEGORIES:
            status = StatusUpdate(
                user_id=uuid.uuid4(),
                message="test",
                category=category,
            )
            assert status.category == category

    def test_status_update_has_category_check_constraint(self) -> None:
        """StatusUpdate table should have a check constraint on category."""
        constraints = StatusUpdate.__table__.constraints
        check_constraints = [c for c in constraints if c.__class__.__name__ == "CheckConstraint"]
        assert any("category" in str(c.sqltext) for c in check_constraints)

    def test_status_update_user_id_fk_has_cascade_delete(self) -> None:
        """FK on user_id should have ON DELETE CASCADE."""
        mapper = inspect(StatusUpdate)
        col = mapper.columns["user_id"]
        for fk in col.foreign_keys:
            assert fk.ondelete == "CASCADE"


class TestModelRelationships:
    """Tests for cross-model relationships."""

    def test_user_status_updates_relationship_back_populates(self) -> None:
        mapper = inspect(User)
        rel = mapper.relationships["status_updates"]
        assert rel.back_populates == "user"

    def test_status_update_user_relationship_back_populates(self) -> None:
        mapper = inspect(StatusUpdate)
        rel = mapper.relationships["user"]
        assert rel.back_populates == "status_updates"


class TestModelExports:
    """Tests for app.models.__init__.py exports."""

    def test_models_package_exports_user(self) -> None:
        from app.models import User as ExportedUser

        assert ExportedUser is User

    def test_models_package_exports_status_update(self) -> None:
        from app.models import StatusUpdate as ExportedStatus

        assert ExportedStatus is StatusUpdate

    def test_models_all_defined(self) -> None:
        import app.models

        assert hasattr(app.models, "__all__")
        assert "User" in app.models.__all__
        assert "StatusUpdate" in app.models.__all__
