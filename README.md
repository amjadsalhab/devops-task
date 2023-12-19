# DevOps-Task
Devops task for ChalkTalk interview process

## Flask Services

This repository contains two Flask services: a User Service and an Order Service.

## User Service

The User Service is a simple Flask application that provides endpoints for managing users. It uses SQLAlchemy for database operations and AWS SSM for retrieving the database connection string.

The User Service provides the following endpoints:

- `POST /user`: Creates a new user. The request body should be a JSON object with a `name` field.
- `GET /users`: Retrieves all users.
- `GET /user/<int:user_id>`: Retrieves a specific user by their ID.

## Order Service

The Order Service is a Flask application that provides endpoints for managing orders. It uses SQLAlchemy for database operations, AWS SSM for retrieving the database connection string and the base URL of the User Service, and makes HTTP requests to the User Service to retrieve user data.

The Order Service provides the following endpoints:

- `POST /order`: Creates a new order. The request body should be a JSON object with `user_id` and `product` fields.
- `GET /order/<int:order_id>`: Retrieves a specific order by its ID, along with the data of the user who placed the order.
- `GET /orders/all`: Retrieves all orders, along with the data of the users who placed them.

## Running the Services
Docker Compose File Summary

Services: Defines two separate services, user-service and order-service, which correspond to the two Flask applications you have for users and orders.

User Service
Build Context: The Docker image for the user service is built from the ./users directory.
Build Arguments: An argument ENVIRONMENT=local is passed to the Docker build process, which can be used in the Dockerfile.
Ports: The service is accessible on port 8098 on the host machine and maps to port 80 inside the container.
Networks: The service is attached to a custom network named local-network.
Volumes: Binds the ~/.aws directory from the host machine to /root/.aws inside the container, allowing the service to access AWS credentials.

Order Service
Build Context: The Docker image for the order service is built from the ./orders directory.
Build Arguments: Similar to the user service, it uses ENVIRONMENT=local as a build argument.
Ports: The service is accessible on port 8099 on the host machine and maps to port 80 inside the container.
Networks: Also attached to the local-network.
Volumes: Like the user service, it binds the ~/.aws directory for AWS credentials.

Networks
Local Network: A custom network named local-network is defined using the default bridge driver, which allows containers to communicate with each other.


Running the Services with Docker Compose

To run the services using Docker Compose, follow these steps:
Install Docker and Docker Compose: Ensure you have Docker and Docker Compose installed on your machine.
Navigate to the Directory: Open a terminal and navigate to the directory containing the docker-compose.yml file.
Run Docker Compose: Execute the following command to build and start the services:

docker-compose up --build

The --build flag ensures that the images are built before starting the containers. If you want to run the services in the background, you can add the -d flag to the command:

docker-compose up --build -d

Access the Services: Once the services are running, you can access the user service at http://localhost:8098 and the order service at http://localhost:8099.
Stop the Services: To stop the services, you can use the following command:

docker-compose down

This command stops and removes the containers, networks, and volumes created by docker-compose up.


Remember to replace ~/.aws with the actual path to your AWS credentials if it's different on your system. This setup assumes that you have a Dockerfile in each of the users and orders directories that the Docker Compose file can use to build the images.



## Deploying services

Jenkins deployment jobs are here :- https://jenkins.amjad-salhab.com/job/DEPLOYMENTS/

Jenkins username/password
username:- chalktalk
password:- chalktalk123

Deployment pipeline are straight forward and consist of the follwoing stages:-

- General Information: Prints out the environment variables and general information about the deployment.
- Build Container Image: Uses Kaniko to build a Docker image from the Dockerfile located in the service path and pushes it to the specified ECR registry.
- Deploy to AWS ECS: Updates the ECS service with the new Docker image by creating a new task definition revision and updating the service.
- Wait Service To Rollout: Waits for the ECS service to finish updating by checking the running count of the primary deployment against the desired count.
- (optional) send slack notifications 

The pipeline assumes that the necessary tools (Kaniko for building images, AWS CLI for interacting with AWS services) are available docker agents, and that the Jenkins environment has the necessary permissions to interact with AWS services like ECR and ECS.

## Databases backup script (should be in separate repo but included here for simplicity)

Usage
The script is run from the command line with various options:

It's already used by schedule jenkins jobs

Jobs url :- https://jenkins.amjad-salhab.com/job/DB_BACKUPS/

Jenkins username/password

username:- chalktalk
password:- chalktalk123

./mysql-backup.sh --environment environment_name --mode backup_mode --database database_name --creds-file-path path_to_credentials_file [--tables table1,table2,...]

Options
--environment: Specifies the environment (e.g., production, staging)
--mode: Specifies the backup mode, which can be either full or custom
--database: Specifies the name of the database to backup
--creds-file-path: Specifies the path to the MySQL credentials file
--tables: (Optional) Specifies a comma-separated list of tables to backup. This option is required if the mode is custom
Example
Here's an example of how to use the script to backup the users table in the orders database in a staging environment:

./mysql-backup.sh --environment staging --mode custom --database orders --creds-file-path ./staging.cnf --tables users

What the Script Does
The script first validates the input parameters. If the mode is custom and no tables are specified, it exits with an error message.

The script then sets the MYSQL_TEST_LOGIN_FILE environment variable to the path of the MySQL credentials file

If the mode is full, the script uses the mysqldump command to backup the entire database to a file named full.sql. It then compresses this file into a tarball named full.tar.gz and uploads it to an S3 bucket

If the mode is custom, the script creates a directory named custom and uses mysqldump to backup each specified table to a separate file in this directory. It then compresses the directory into a tarball named custom.tar.gz and uploads it to an S3 bucket
The script assumes that the AWS CLI is installed and configured with the necessary permissions to upload files to the specified S3 bucket


## Regards
## By Amjad Salhab