## D - Application

(impostor-discord-bot-env) PS D:\Esteban Proyectos\impostor-discord-bot> pytest tests/unit/application --no-cov -q
..................................                         [100%]
34 passed in 0.15s
(impostor-discord-bot-env) PS D:\Esteban Proyectos\impostor-discord-bot> 


(impostor-discord-bot-env) PS D:\Esteban Proyectos\impostor-discord-bot> Get-ChildItem tests/unit/application -Recurse -Filter *.py |
>>     Select-String -Pattern "discord|sqlalchemy|asyncpg|Postgres"
(impostor-discord-bot-env) PS D:\Esteban Proyectos\impostor-discord-bot> 


(impostor-discord-bot-env) PS D:\Esteban Proyectos\impostor-discord-bot> pytest tests/unit/application `
>>     -o addopts="" `
>>     --cov=src/impostor_bot/application `
>>     --cov-branch `
>>     --cov-report=term-missing
====================== test session starts ======================
platform win32 -- Python 3.12.14, pytest-9.1.1, pluggy-1.6.0
rootdir: D:\Esteban Proyectos\impostor-discord-bot
configfile: pytest.ini
plugins: asyncio-1.4.0, cov-7.1.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 34 items                                               

tests\unit\application\test_create_game.py ....            [ 11%]
tests\unit\application\test_finish_cancel_game.py .......  [ 32%]
tests\unit\application\test_game_concurrency.py ....       [ 44%]
tests\unit\application\test_get_game_status.py ..          [ 50%]
tests\unit\application\test_join_leave_game.py .........   [ 76%]
tests\unit\application\test_start_game.py ........         [100%]

======================== tests coverage =========================
_______ coverage: platform win32, python 3.12.14-final-0 ________

Name                                              Stmts   Miss Branch BrPart  Cover   Missing
---------------------------------------------------------------------------------------------
src\impostor_bot\application\__init__.py              0      0  0      0   100%
src\impostor_bot\application\cancel_game.py          19      0  4      0   100%
src\impostor_bot\application\create_game.py          17      0  2      0   100%
src\impostor_bot\application\exceptions.py            4      0  0      0   100%
src\impostor_bot\application\finish_game.py          19      0  4      0   100%
src\impostor_bot\application\get_game_status.py      12      0  2      0   100%
src\impostor_bot\application\join_game.py            18      0  2      0   100%
src\impostor_bot\application\leave_game.py           18      0  2      0   100%
src\impostor_bot\application\start_game.py           31      0  4      0   100%
---------------------------------------------------------------------------------------------
TOTAL                                               138      0 20      0   100%
====================== 34 passed in 0.37s =======================
(impostor-discord-bot-env) PS D:\Esteban Proyectos\impostor-discord-bot> 