
# To Run
Install Docker Desktop

**Warning, running these commands will require the installation of ~5 GB of data**

1) Run `docker volume create ollama` to create an external volume that you can run other containers to use.
2) Run `docker compose up -d` 
3) Create a python virtual env. Activate it, and install dependencies
4) `python main.py`

To exit

1) Exit the python program
2) Run `docker compose down`
   1) Run `docker compose down -v` to remove volumes

# Old Commands
```bash
docker run --name sheets-db -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres
docker exec -it sheets-db psql -U postgres
docker stop sheets-db
docker rm sheets-db
```

```bash
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
docker rm -v ollama
```