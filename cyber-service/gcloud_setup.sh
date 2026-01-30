PROJECT_ID=docheart # configure the id of your google cloud project

gcloud auth login
gcloud config set run/region eu-west1
gcloud auth configure-docker
gcloud config set project $PROJECT_ID