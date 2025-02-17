# House Management API
## Author 
Derek Xu

## About
This project is a RESTful API built with FastAPI for managing houses, users, rooms, and devices. It provides endpoints to create, retrieve, update, and delete resources related to house management. The API utilizes Pydantics for type/input validation

Some useful notes:
- This does not use a DB. As a proof of concept, this uses memory with no persistent storage for now.

Resources Used:
- https://fastapi.tiangolo.com/virtual-environments/#create-a-virtual-environment
- https://medium.com/codenx/fastapi-pydantic-d809e046007f 

## Documentation
All API documentation uses SwaggerUI and OpenAPI specification at:

`base_url/docs`

or by default:

`http://127.0.0.1:8000/docs`

You can also view the OpenAPI specification here:

[housemanagement-openapi.json](housemanagement-openapi.json)

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd house-management-api
   ```

2. Activate a python environment and install the dependencies:
   ```
   python -m venv .venv
   # activate venv depending on OS
   pip install -r requirements.txt
   ```

3. Set up the environment variables in the `.env` file.

## Usage

To run the API, execute the following command:

```
uvicorn src.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## Testing

To run the tests, use the following command:

```
pytest
# or
python -m pytest tests/
```

# Data Specs
House
- Name
- addr
- gps
- owner
- occupants

Room
- Name
- floor
- sqft
- house
- type

Device
- type
- name
- room
- settings
- data
- status

User
- name
- username
- phone
- privillege
- email
