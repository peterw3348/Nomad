@echo off
echo Activating virtual environment...
call venv\Scripts\Activate

echo Fetching data...
python -m src.api.data_dragon.data_dragon

echo Generating Debug build files...
cmake -B build/debug -DCMAKE_BUILD_TYPE=Debug -G "MinGW Makefiles"

echo Building Debug...
cmake --build build/debug