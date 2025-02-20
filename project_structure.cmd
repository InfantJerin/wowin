@echo off
mkdir src\api src\core src\db src\models src\schemas src\services src\utils
mkdir tests\test_api tests\test_services tests\test_models
mkdir alembic\versions
mkdir scripts

REM Create empty files
type nul > src\__init__.py
type nul > src\api\__init__.py
type nul > src\api\routes.py
type nul > src\api\dependencies.py
type nul > src\core\__init__.py
type nul > src\core\config.py
type nul > src\core\security.py
type nul > src\core\logging.py
type nul > src\db\__init__.py
type nul > src\db\session.py
type nul > src\db\base.py
type nul > src\models\__init__.py
type nul > src\models\domain.py
type nul > src\schemas\__init__.py
type nul > src\schemas\domain.py
type nul > src\services\__init__.py
type nul > src\services\domain_service.py
type nul > src\utils\__init__.py
type nul > src\utils\helpers.py
type nul > tests\__init__.py
type nul > tests\conftest.py
type nul > scripts\start.bat
type nul > scripts\setup_db.bat