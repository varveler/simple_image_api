# Asynchronous Image Processing API

> This API Documentation (OpenAPIv3) can be accessed via the following link:: 
> https://app.swaggerhub.com/apis/EVARVAL/SIMPLE_Image_Processing_And_Storing_API/1.0

This repository contains a simple REST API developed using Django, the Django REST Framework, and Celery. This API is designed to store and serve images. It provides an endpoint to upload images, retrieve the list of images, and get specific image details. 

Images uploaded are stored in an Amazon S3 bucket and are optimized for size. The API also provides options to resize images and filter them based on their titles.

An important feature of this API is the use of Celery for asynchronous task processing. Resizing, optimization and remote storage operations are managed in the background using Celery tasks. This approach allows the API to swiftly return a response to the client, rather than making the client wait for these potentially time-consuming operations to be completed.

To fulfill this functionality, a user initiates a POST request to upload an image. The file is initially stored in FileSystemStorage. Following this, a task is dispatched to Celery to conduct the necessary image resizing, optimization, and storage into an AWS S3 bucket. Upon the completion of these processes, the temporary file originally stored in FileSystemStorage is deleted.

This approach has several benefits. The API can handle more requests in a shorter amount of time so the **performance is improved**.  As the request isn't blocked by image processing, the **user experience is enhanced.** The workload can be distributed among multiple workers, allowing the system to **scale effectively** and handle larger loads efficiently.


# Project structure

    image_processing_api/
    |---docker                  #files for docker environment variables and builds
    |   |---db
    |   |   |---.env            # environment variables for db container
    |   |---nginx
    |   |   |---default.dev.conf # nginx configuration file
    |   |   |---dev-Dockerfile  # Docker file to build nginx
    |   |---rabbit
    |   |   |---.env            # environment variables for Rabbit MQ
    |---src                     # django project folder
    |   |---image_api                
    |   |   |---settings        # django configuration
    |   |   |   |---base.py
    |   |   |   |---development.py # this project uses this configuration file
    |   |   |   |---production.py
    |   |   |---asgi.py
    |   |   |---celery.py      # celery configuration
    |   |   |---urls.py        # urls base configuration file
    |   |   |---wsgi.py
    |   |---images             # images app
    |   |   |---migrations
    |   |   |   |---(...) 
    |   |   |---tests
    |   |   |   |---test_api.py      # tests for API endpoints
    |   |   |   |---test_services.py # tests for images processing tasks
    |   |   |---admin.py
    |   |   |---apps.py
    |   |   |---models.py
    |   |   |---serilaizers.py
    |   |   |---services.py     # image optimization functions
    |   |   |---tasks.py        # celerys asynchrounous tasks
    |   |   |---urls.py
    |   |   |---views.py
    |   |---media               # images app
    |   |   |---tempImageFiles  # temporal folder for user uploaded images
    |   |---.env.dev            # environmental variables for development
    |   |---custom_storage.py   # S3 storage configuration file
    |   |---Dockerfile          # Dockerfile for backend build
    |   |---manage.py
    |   |---requirements.txt
    |---docker-compose.yml
    |---image_api.postman_collection.json  # PostMan Collection for API manual testing
    |---README.md
    


## Local Setup

To get this project up and running locally follow the steps below:

### <u>Step 1:</u> Set AWS Credentials

AWS_STORAGE_BUCKET_NAME=your-s3-bucket-name
Add your AWS credentials to the `src/.env.dev` file. You will need to set your `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` and `AWS_STORAGE_BUCKET_NAME`. It should look like this:

```env
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_STORAGE_BUCKET_NAME=your-s3-bucket-name
AWS_S3_REGION_NAME=us-west-2  # see comment below
```
>  **WARNING:** For simplicity, chose **'us-west-2'** as your S3 bucket region when creating your s3 bucket, as the signature version can vary depending on the region. By default, this project is set to use the 's3v4' signature version, but this can be changed in the 'settings.base' file under the variable 'AWS_S3_SIGNATURE_VERSION'.


### <u>Step 2:</u> Build Docker Containers
To build the Docker containers for the project, navigate to the root directory of the project in your terminal and run the following command:
```bash
$ docker-compose build
```

### <u>Step 3:</u> Run Docker Containers
To run the Docker containers, use the following command:
```bash
$ docker-compose up
```

This command will run these containers:

- **db**: This container runs a PostgreSQL database. The named volume **db_data** is used for data persistence.

- **backend**: This is the main application server container. It builds from a Dockerfile located in ./src/. It runs Django migrations, collects static files and starts the application server with gunicorn. It depends on the db service and waits for it to be healthy before starting.

- **nginx**: This is the web server container. It handles incoming HTTP requests and forwards them to the backend service. It also serves static files directly. It builds from a Dockerfile located in ./docker/nginx

- **rabbit**: This container runs a RabbitMQ server. RabbitMQ is a message broker, which is used to handle message queues. It is used as a message broker for Celery, facilitating communication between the main application (backend) and the worker tasks.

- **worker**: This container runs Celery worker processes. These workers listen for tasks (like image processing jobs) on the message queue and perform them asynchronously.

- **beat**: This container runs the Celery Beat service. Celery Beat is a scheduler; it kicks off configured tasks at regular intervals or a specific future date. In this particular project, Celery Beat is not directly utilized. However, it's been set up for demonstration purposes and to be ready within the docker-compose file for potential future enhancements. One use case could be to automatically retry a failed task after a specific time interval. This would allow for more robust handling of transient errors in task dependencies (such as a temporarily unavailable external service).

### <u>Step 4:</u> Run Tests
Open a new terminal and run tests directly on the backend container with the following command:

```bash
$ docker exec -it api_backend python manage.py test
```

If everything went well you should see something like this:
```
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
--------------------------
Ran 8 tests in 0.123s

OK
```

> A Postman collection is included for manual testing. 
> This can be imported from the file image_api.postman_collection.json

