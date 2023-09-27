# Chat PDF
Study project. Application Large Language Model for PDF documents.

[![MIT License](https://img.shields.io/badge/license-MIT-green)](https://github.com/Unfeir/goit_llm/LICENSE)
![Version](https://img.shields.io/badge/version-v0.1.0-green)


Our cutting-edge application seamlessly combines the power of PDF files and state-of-the-art Large Language Models (LLMs) to revolutionize how you work with textual documents.
Gone are the days of tediously scrolling through lengthy PDFs to find the information you need.
With our application, you can harness the intelligence of LLMs to read and comprehend PDF files, making it effortless to extract valuable insights, answers, and knowledge from your documents.
        
....
## Prerequisites
Before you begin, ensure that you have the following prerequisites installed on your system:

- Python 3.10 or higher
- Poetry

## Installation
1. Clone the project repository:
```
git clone <repository_url>
```

2. Navigate to the project directory:
```
cd <project_directory>
```
3. Install the project dependencies using Poetry:
```
poetry install
```
Poetry will create a virtual environment and install the required packages specified in the pyproject.toml file.

## Launching
To launch the development server and start the FastAPI project, follow these steps:

1. Activate the project's virtual environment:
```
poetry shell
```
2. Run the following command to start the development server:
```
uvicorn app.utils.main:app --reload   
```
- ```main``` refers to the name of the main file where your FastAPI app instance is created.
- ```--reload``` enables auto-reloading of the server whenever code changes are detected (useful during development).
3. Once the server has started, you should see output similar to the following:

```
INFO: Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```
Open your web browser and navigate to http://127.0.0.1:8000 to access the API.

4. Swager documentation could be found here: http://127.0.0.1:8000/docs


## Launching on Docker with Databases

1) Run the following command to start the development server:
```
docker-compose up
```
Swager documentation could be found here: http://127.0.0.1:8000/docs
Chat at http://127.0.0.1:8000/

2) Run the following command to stop
```
docker-compose down
```

## Alembic migrations:
init migration:
```
    alembic init -t async migrations
```
make new migration:
```
    alembic revision --autogenerate -m 'Init'  # change name
```
push migration:
```
    alembic upgrade head
```
*Notice after initializing migrations, you must change the settings in the file:
1) target_metadata = None - >  = Base.metadata
2) config.set_main_option("sqlalchemy.url", SQLALCHEMY_DATABASE_URL)


...

## Application features

A web service similar in functionality to ChatGPT. 
 After registration, users can log in, upload texts from their own documents (PDFs) or choose a specific one from previously uploaded ones and send questions based on these materials via chat to get contextually informed answers. Also, when selecting previously uploaded documents, the history of communication is provided.

The application may be interesting for individual use both in the workflows of organizations and for personal purposes. The main purpose of the application is to automate the retrieval of specific information from a relatively large data set.

...


### Used technologies
- Python (programming language)
- FastAPI (web framework)
- Uvicorn (ASGI server)
- Websockets
- JavaScript
- Postgres + asyncpg
- Docker for quick and simple development
- LLM
- PyTorch + Transformers


......


### Developers - Fast Rabbit Team
- [Andrii Kylymnyk](https://github.com/theneonwhale)
- [Anton Holovin](https://github.com/Unfeir)
- [Denys Tantsiura](https://github.com/DenysTantsiura)

#### License
This project is licensed under the MIT License.
