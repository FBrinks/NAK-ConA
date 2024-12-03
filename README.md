# Setup Instructions for ConA - Lite on MacBook Pro

## Prerequisites

1. **Download and Install VS Code**
    - Visit the [VS Code download page](https://code.visualstudio.com/Download).
    - Download the macOS version.
    - Open the downloaded file and drag the VS Code icon to the Applications folder.

2. **Install Python3**
    - Visit the [Python download page](https://www.python.org/downloads/).
    - Download the latest version of Python3 for macOS.
    - Open the downloaded file and follow the installation instructions.

## Setting Up the Project

1. **Open the Project Folder in VS Code**
    - Open VS Code.
    - Click on `File` > `Open Folder...`.
    - Navigate to where you saved the file and click `Open`.

1. **Using GitHub to download the program**
- Open the terminal in VS Code by clicking on `Terminal` > `New Terminal`.
- In the terminal, run the following command to clone the repository:
  ```bash
  git clone https://github.com/FBrinks/NAK-ConA.git
  ```
- Navigate into the project directory:
  ```bash
  cd ConA-Lite
  ```

2. **Set Up a Virtual Environment**
    - Open the terminal in VS Code by clicking on `Terminal` > `New Terminal`.
    - In the terminal, run the following command to create a virtual environment named `conalite`:
    - Note that the name is arbitrary and you can choose any name you like
      ```bash
      python3 -m venv conalite
      ```

3. **Select the Python Interpreter**
    - Press `Cmd+Shift+P` to open the Command Palette.
    - Type `Python: Select Interpreter` and select it.
    - Choose the interpreter located at EX. `/Users/fredde.brink/3. Automatisering/ConA - Lite/ConALite/bin/python`.

4. **Activate the Virtual Environment**
    - In the terminal, run the following command to activate the virtual environment:
      ```bash
      source ConALite/bin/activate
      ```

## Installing Requirements

1. **Install Dependencies**
    - Ensure the virtual environment is activated.
    - In the terminal, run the following command to install the required packages from `requirements.txt`:
      ```bash
      pip install -r requirements.txt
      ```

2. To be able to use the File-search function and creation of producttexts you need to add a .env file to the root of the project and add your OPENAI_API_KEY=your-api-key The model i use in this project is "gpt-4o-2024-08-06".


## Troubleshooting

- **Virtual Environment Not Activating:**
  - Ensure the virtual environment was created correctly and you are running the `source` command from the correct directory.

- **Dependencies Not Installing:**
  - Confirm `requirements.txt` exists in the project folder.
  - Update `pip` with:
    ```bash
    pip install --upgrade pip
    ```


You are now ready to start working on the ConA - Lite project!
