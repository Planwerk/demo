"""Unit tests for Alembic configuration and migration structure."""

import ast
import configparser
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent


class TestAlembicConfiguration:
    """Tests for alembic.ini and directory structure (REQ-005)."""

    def test_alembic_ini_exists(self) -> None:
        assert (BACKEND_DIR / "alembic.ini").is_file()

    def test_alembic_ini_script_location(self) -> None:
        cfg = configparser.ConfigParser()
        cfg.read(BACKEND_DIR / "alembic.ini")
        assert cfg.get("alembic", "script_location") == "alembic"

    def test_alembic_ini_has_file_template(self) -> None:
        cfg = configparser.ConfigParser()
        cfg.read(BACKEND_DIR / "alembic.ini")
        template = cfg.get("alembic", "file_template")
        assert "%(year)d" in template
        assert "%(rev)s" in template

    def test_alembic_env_py_exists(self) -> None:
        assert (BACKEND_DIR / "alembic" / "env.py").is_file()

    def test_alembic_env_imports_base_metadata(self) -> None:
        env_source = (BACKEND_DIR / "alembic" / "env.py").read_text()
        assert "Base" in env_source
        assert "target_metadata" in env_source

    def test_alembic_env_imports_models(self) -> None:
        env_source = (BACKEND_DIR / "alembic" / "env.py").read_text()
        assert "from app.models import" in env_source

    def test_alembic_env_uses_async_engine(self) -> None:
        env_source = (BACKEND_DIR / "alembic" / "env.py").read_text()
        assert "create_async_engine" in env_source

    def test_alembic_env_uses_null_pool_with_async_engine(self) -> None:
        env_source = (BACKEND_DIR / "alembic" / "env.py").read_text()
        assert "NullPool" in env_source

    def test_alembic_env_uses_settings_database_url(self) -> None:
        env_source = (BACKEND_DIR / "alembic" / "env.py").read_text()
        assert "settings.DATABASE_URL" in env_source

    def test_alembic_script_template_exists(self) -> None:
        assert (BACKEND_DIR / "alembic" / "script.py.mako").is_file()

    def test_alembic_versions_directory_exists(self) -> None:
        assert (BACKEND_DIR / "alembic" / "versions").is_dir()


class TestInitialMigration:
    """Tests for the initial migration file (REQ-006)."""

    def _get_migration_files(self) -> list[Path]:
        versions_dir = BACKEND_DIR / "alembic" / "versions"
        return [f for f in versions_dir.glob("*.py") if f.name != "__init__.py"]

    def _get_initial_migration_file(self) -> Path:
        """Return the initial migration file deterministically.

        Sorts by filename so adding new migrations doesn't change which file
        these tests validate.
        """
        files = sorted(self._get_migration_files(), key=lambda p: p.name)
        assert files, "No migration files found in alembic/versions"
        return files[0]

    def test_migration_file_exists(self) -> None:
        files = self._get_migration_files()
        assert len(files) >= 1

    def test_migration_creates_users_table(self) -> None:
        source = self._get_initial_migration_file().read_text()
        assert 'create_table' in source
        assert '"users"' in source

    def test_migration_creates_status_updates_table(self) -> None:
        source = self._get_initial_migration_file().read_text()
        assert 'create_table' in source
        assert '"status_updates"' in source

    def test_migration_users_created_before_status_updates(self) -> None:
        source = self._get_initial_migration_file().read_text()
        users_pos = source.index('"users"')
        status_pos = source.index('"status_updates"')
        assert users_pos < status_pos

    def test_migration_downgrade_drops_status_updates_before_users(self) -> None:
        source = self._get_initial_migration_file().read_text()
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "downgrade":
                body_source = ast.get_source_segment(source, node)
                assert body_source is not None
                status_pos = body_source.index("status_updates")
                users_pos = body_source.index('"users"')
                assert status_pos < users_pos
                break

    def test_migration_has_revision_id(self) -> None:
        source = self._get_initial_migration_file().read_text()
        assert "revision" in source

    def test_migration_has_upgrade_and_downgrade(self) -> None:
        source = self._get_initial_migration_file().read_text()
        assert "def upgrade()" in source
        assert "def downgrade()" in source

    def test_migration_users_has_unique_constraints(self) -> None:
        source = self._get_initial_migration_file().read_text()
        assert 'UniqueConstraint("username")' in source
        assert 'UniqueConstraint("email")' in source

    def test_migration_status_updates_has_foreign_key(self) -> None:
        source = self._get_initial_migration_file().read_text()
        assert "ForeignKeyConstraint" in source
        assert '"users.id"' in source

    def test_migration_status_updates_has_user_id_index(self) -> None:
        source = self._get_initial_migration_file().read_text()
        assert "ix_status_updates_user_id" in source

    def test_migration_uses_server_default_for_uuid(self) -> None:
        source = self._get_initial_migration_file().read_text()
        assert 'server_default=sa.text("gen_random_uuid()")' in source

    def test_migration_status_updates_fk_has_cascade_delete(self) -> None:
        source = self._get_initial_migration_file().read_text()
        assert 'ondelete="CASCADE"' in source

    def test_migration_status_updates_has_category_check_constraint(self) -> None:
        source = self._get_initial_migration_file().read_text()
        assert "ck_status_updates_category" in source
