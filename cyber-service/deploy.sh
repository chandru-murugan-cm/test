PROJECT_ID=docheart # configure the id of your google cloud project
REPOSITORY_NAME=docheart # the name of the image repository in google cloud artifcat registry
SERVICE_NAME=example-service # configure the name of the service

docker build --build-arg env_file=.env -t europe-west1-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/$SERVICE_NAME ./service
docker push europe-west1-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/$SERVICE_NAME:latest
gcloud run deploy $SERVICE_NAME --image europe-west1-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/$SERVICE_NAME:latest --region europe-west1 --allow-unauthenticated