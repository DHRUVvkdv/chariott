docker build -t codefest-backend .
docker run --rm -p 8000:8000 --entrypoint python --env-file .env codefest-backend main.py

CodefestBackendInfraStack

aws lambda update-function-url-config \
 --function-name CodefestBackendInfraStack-ApiFunctionCE271BD4-xrpFQqE6RoMd \
 --cors '{
"AllowOrigins": ["https://main.d2gakz683sax2c.amplifyapp.com", "http://localhost:3000"],
"AllowMethods": ["*"],
"AllowHeaders": ["*"],
"AllowCredentials": true,
"MaxAge": 300
}'

aws lambda get-function-url-config \
 --function-name CodefestBackendInfraStack-ApiFunctionCE271BD4-xrpFQqE6RoMd

aws lambda update-function-url-config \
 --function-name CodefestBackendInfraStack-ApiFunctionCE271BD4-xrpFQqE6RoMd \
 --cors '{
"AllowOrigins": [],
"AllowMethods": [],
"AllowHeaders": [],
"AllowCredentials": false,
"MaxAge": 0
}'

npm install -g @mermaid-js/mermaid-cli
mmdc -i userDB.mmd -o diagram.svg
mmdc -i userDB.mmd -o diagram.png
