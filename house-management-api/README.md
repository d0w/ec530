# README.md

https://fastapi.tiangolo.com/virtual-environments/#create-a-virtual-environment

# House Management API

This project is a RESTful API built with FastAPI for managing houses, users, rooms, and devices. It provides endpoints to create, retrieve, update, and delete resources related to house management.

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd house-management-api
   ```

2. Install the dependencies:
   ```
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
```