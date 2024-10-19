docker build -t codefest-backend .
docker run --rm -p 8000:8000 --entrypoint python --env-file .env codefest-backend main.py

CodefestBackendInfraStack
