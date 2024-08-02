-------------------------------------------------------
# OpenAI Ellish Chatbot Documentation and Instructions of Use

Created By: Woo Jin Lee, Regina Garfias, Daniil Rusanyuk

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Copyright

© 2024 Ellish inc. All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions, and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions, and the following disclaimer in the documentation and/or other materials provided with the distribution.
3. Neither the name of Woojin Lee nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

-------------------------------------------------------
# official_genailib_wl MANUAL

## official_genailib_wl Documentation of Instructions and Help

Welcome to the official_genailib_wl repository! This document will guide you through the steps required to set up and run the project.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Setting Up Environment Variables](#setting-up-environment-variables)
4. [Running the Project](#running-the-project)
5. [Usage](#usage)
6. [Testing](#testing)
7. [Other Commands](#other-commands)
8. [Contributing](#contributing)
9. [License](#license)

## Prerequisites

Before you begin, ensure you have met the following requirements:
- You have installed Git.
- You have installed Python (preferably Python 3.7 or later).
- You have installed `pip` (Python package installer).

### Installing Git

To install Git, follow the instructions for your operating system:

**Windows:**
1. Download the installer from [Git for Windows](https://gitforwindows.org/).
2. Run the installer and follow the instructions.

**macOS:**
Open Terminal and run:
brew install git

**Linux:**
Open Terminal and run:
sudo apt-get update
sudo apt-get install git

### Installing Python and Pip

**Windows and macOS:**
1. Download the installer from Python's official website.
2. Run the installer and ensure you check the box that says "Add Python to PATH."

**Linux:**
Open Terminal and run:
sudo apt-get update
sudo apt-get install python3
sudo apt-get install python3-pip

## Installation

Clone the repository and install the necessary Python packages:

1. Open Terminal.
2. Clone the repository:
git clone https://github.com/woojin-lee713/official_genailib_wl.git or use the ssh directory: git@github.com:woojin-lee713/official_genailib_wl.git
3. Navigate to the project directory:
cd official_genailib_wl
4. Install the required Python packages:
pip install -r requirements.txt

**Note:** Ensure you have installed all necessary dependencies specified in the `requirements.txt` file. These dependencies are crucial for the proper functioning of the project.

Examples of what you should install:
1. Test environments are both running on both gpt-4-turbo and gpt-3.5-turbo
2. You need quarto
3. You need nbdev
4. You need setuptools
5. Pip3 install openai
6. Pip3 install —upgrade openai (most up-to-date version 1.35.7)
7. Pip3 install python

## Setting Up Environment Variables

This project requires an OpenAI API key to function. You need to create a .env file in the root directory of the project and add your OpenAI API key.

Create a .env file in the project root directory:
touch .env

Open the .env file and add the following line, replacing your_openai_api_key with your actual OpenAI API key:
OPENAI_API_KEY=your_openai_api_key

## Running the Project

After setting up the environment variables, you can run the project:

Open Terminal.
Navigate to the project directory:
cd official_genailib_wl

Now run the program!
1. pixi run program
2. pixi run program -p "type here" -m "type here" (e.g. pixi run program -p "hello world" -m "gpt-3.5-turbo") (--prompt or -p | --model or -m)

### USAGE:

- Running the main script
python genailib_wl_folder/genailib_wl_file.py
^This script prompts you to enter a prompt and a model type if desired

Example input:
Enter the prompt (default: Hello World!): Riddle of the day!
Enter the model (default: gpt-3.5-turbo): gpt-4-turbo

Example output:
Sure, I'd love to give you a riddle! Here's one for you: I speak without a mouth and hear without ears. I have no body, but I come alive with the wind. What am I?

### TESTING:

- To run tests, use the following Pixi tasks:
- pixi run test
^runs pytest with coverage excluding end-to-end tests, shows test results and coverage percentages for different Python versions
- pixi run test_e2e
^runs pytest with coverage including e2e, also showing test results and coverage percentages

### OTHER COMMANDS:

- 'pixi run lint': Run linting checks
- 'pixi run format': Format code using a formatter
- 'pixi run typing': Check typing using mypy
- 'pixi run docs': Generate documentation using nbdev
- 'pixi run build': Build the package for distribution
- 'pixi run publish': Publish to test pypi (don't forget to change the version number before you build in pyproject.toml to create new built env .whl)

Please refer to the google docs below for more detailed overview of the terminal interface you could use with this git repository.

IMPORTANT GOOGLE DOCS (Terminal / Console Report): [Google Docs Link](https://docs.google.com/document/d/1pBADnjJIcB-QPoMmxiIm48xIxzSQJvDY3Yeka4wyJH8/edit?usp=sharing)

-------------------------------------------------------
# officialgenaiserverwl MANUAL

## officialgenaiserverwl Documentation of Instructions and Help

Welcome to the officialgenaiserverwl repository! This document will guide you through the steps required to set up and run the project.

## Table of Contents

1. Prerequisites
2. Installation
3. Setting Up Environment Variables
4. Running the Project
5. Contributing
6. License

## Prerequisites

Before you begin, ensure you have met the following requirements:
- You have installed Git.
- You have installed Python (preferably Python 3.7 or later).
- You have installed pip (Python package installer).

### Installing Git

To install Git, follow the instructions for your operating system:

**Windows:**
1. Download the installer from Git for Windows.
2. Run the installer and follow the instructions.

**macOS:**
Open Terminal and run: brew install git

**Linux:**
Open Terminal and run: sudo apt-get update sudo apt-get install git

### Installing Python and Pip

**Windows and macOS:**
1. Download the installer from Python's official website.
2. Run the installer and ensure you check the box that says "Add Python to PATH."

**Linux:**
Open Terminal and run: sudo apt-get update sudo apt-get install python3 sudo apt-get install python3-pip

### Installing Pixi

Pixi is required to run specific tasks for this project. To install Pixi, run the following command: pip install pixi

## Installation

Clone the repository and install the necessary Python packages:

1. Open Terminal.
2. Clone the repository: git clone https://github.com/woojin-lee713/officialgenaiserverwl.git or use the ssh directory: git@github.com:woojin-lee713/officialgenaiserverwl.git
3. Navigate to the project directory: cd officialgenaiserverwl
4. Install the required Python packages: pip install -r requirements.txt

## Setting Up Environment Variables

This project requires an OpenAI API key and a Flask secret key to function. You need to create a .env.secret file in the root directory of the project and add these keys. The original source code is safetly publish to the dokku environment and will NOT appear in any source code. If you would like to use this on your personal computer, please set your own unique Flask Key and OpenAI API Key.

Create a .env.secret file in the project root directory: touch .env.secret

Open the .env.secret file and add the following lines, replacing your_openai_api_key with your actual OpenAI API key and your_flask_secret_key with any random string (use #@%): OPENAI_API_KEY=your_openai_api_key FLASK_SECRET_KEY=your_flask_secret_key

## Running the Project

After setting up the environment variables, you can run the project using the following commands:

To populate the database (if applicable): pixi run populate

To start the server: pixi run server

## Deploy to Dokku
All the files set in this repository are file ready to be deployed to dokku as all configurations have been made to make it successful. In order

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch: git checkout -b feature-branch
3. Make your changes and commit them: git commit -m 'Add some feature'
4. Push to the branch: git push origin feature-branch
5. Create a pull request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

Thank you for using Ellish inc.
