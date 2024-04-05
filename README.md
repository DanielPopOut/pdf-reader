# Run the thing

1. Install pyenv
2. Install python 3.12 `pyenv install 3.12`
3. Create a virtual env `pyenv virtualenv 3.12 <venv name>`
4. Activate the virtual env `pyenv activate <venv name>`
5. Install using pipenv `pipenv install`
6. duplicate .env.example to .env `cp .env.example .env`
7. run the flask server `flask --app server run`
