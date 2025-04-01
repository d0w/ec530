```bash
docker run --name sheets-db -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres
docker exec -it sheets-db psql -U postgres
docker stop sheets-db
docker rm sheets-db
```