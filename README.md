# Nomad

## Overview
This project utilizes Python for data retrieval and integrates with a low-latency, real-time C++ overlay, providing dynamic analysis to enhance decision-making efficiency.

## One-time Setup (Windows 11)

### 1. Setup Virtual Environment (venv)
- **Create virtual environment:**
  ```sh
  python -m venv venv
  ```
- **Activate virtual environment:**
  ```sh
  venv\Scripts\Activate
  ```

### 2. Install Dependencies

#### 📌 Python
- Install **Python 3.13.2** or greater.
- Install required Python dependencies:
  ```sh
  pip install -r requirements.txt
  ```

#### 📌 C++
1. **Install CMake**:
   ```sh
   winget install Kitware.CMake
   ```
2. **Install MinGW-w64 GCC 13.2.0 or greater**:
   - Download from [winlibs.com](https://winlibs.com/).
   - Extract to your preferred folder (e.g., `D:\mingw64`).
   - Add `mingw64\bin` to system **environment variables**:
     1. Open **Environment Variables** in Windows.
     2. Under **System Variables**, find **Path** and click **Edit**.
     3. Click **New** and add:
        ```sh
        D:\mingw64\bin
        ```
     4. Verify the installation by running:
        ```sh
        g++ --version
        ```

---

## Setup, Build, and Run Nomad

The build_release.bat and build_debug.bat scripts performs all these steps except running.

### 0. Activate Virtual Environment
```sh
venv\Scripts\Activate
```

### 1. Install Nomad using setup file
```sh
pip install -e .
```

### 2. Clean Previous Builds
```sh
Remove-Item -Recurse -Force build
```

### 3. Generate Build Files
#### 🔹 Release Build
```sh
cmake -B build/release -DCMAKE_BUILD_TYPE=Release -G "MinGW Makefiles"
```
#### 🔹 Debug Build
```sh
cmake -B build/debug -DCMAKE_BUILD_TYPE=Debug -G "MinGW Makefiles"
```

### 4. Compile & Build
#### 🔹 Release Build
```sh
cmake --build build/release
```
#### 🔹 Debug Build
```sh
cmake --build build/debug
```

### 5. Run Nomad
#### 🔹 Release Build
```sh
./build/release/bin/Nomad.exe
```
#### 🔹 Debug Build
```sh
./build/debug/bin/Nomad.exe
```
