Install superset docker connect to TRINO
1. Clone this repo
2. Create database for Superset (SQLite):
`docker exec -it superset_app superset db upgrade`
`docker exec -it superset_app superset init`

3. Create admin :
``` bash
docker exec -it superset_app superset fab create-admin \
   --username admin \
   --firstname Superset \
   --lastname Admin \
   --email admin@superset.com \
   --password admin
```

4. Install Trino connections:
``` bash
docker exec -it superset_app bash
pip install trino[sqlalchemy]
exit
```


5. Start Supetset:
`docker-compose down`
`docker-compose up -d`

6. Login with username and password in port `2509`
7. Connect Trino to Superset:
- `Data` -> `Databases`
- Click to `+ Database` 
- Select `Trino` from list
- In4 for connect :
    + Display Name : Trino DB
    + URI: trino://admin@`trino_container`:2509/minio/minio

8. Use Trino:
- Select : `Sources` -> `Tables` or `Sources` -> `Datasets`
