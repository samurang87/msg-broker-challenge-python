# Message broker challenge

## Challenge description

The goal of this challenge is to implement a message broker that can handle multiple topics and multiple subscribers. The broker will be able to receive messages from publishers and send them to subscribers. The subscribers will be able to subscribe to multiple topics with a single subscription, using a wildcard character.

In this project, the use-case for this message broker is a file watcher that publishes messages to the broker when a file is modified. The subscribers will be able to read the diff of the file and the time of the change. The subscriber will log the changes to all files and print timestamp and diff to terminal for changes in important files (files that have the word “important” in their file path).

## Requirements

### Message broker
- The main application will be a message broker, to which one can publish or subscribe to messages.
- The broker will be able to handle multiple topics.
- The subscriber will be able to subscribe to multiple topics with a single subscription, using a wildcard character. When matching the topic name of a published message against subscriptions from left to right, as soon as a wildcard is encountered in the subscription, it matches. For example: the
topic abc matches with ab~ but doesn’t match with b~. Just ~ would match all possible topics.

### Publisher
- The application publishing to the broker will publish a message once a file in a file server is modified.
- Users are not allowed to create new files in the server, only changing existing files.
- Changes to all files in the server must be published to the broker.

### Subscriber
- The subscriber will be able to read the diff in the file and the time of the change.
- The subscriber will log the changes to all files.
- The subscriber will print timestamp and diff to terminal for changes in important files (files that have the word “important” in their file path).
- The wildcard character will be used to distinguish important files from the rest.

## Solution design

For the purpose of the toy application, the three applications are part of the same project and share a common set of Pydantic models as API contract.

All the containers are built with the same docker image, and use different entry points provided by the docker compose file.

I chose FastAPI for both the broker and the reviewer applications because it is quick to set up, while being a powerful framework. The broker exposes an endpoint to publish messages and one to subscribe to topics. The reviewer subscribes to the topics and provides a callback url to the broker to receive the messages.

As this is a toy application, without scalability requirements:
- the message broker only uses one thread and an in-memory storage
- the reviewer application also uses one thread only and a file to store the logs.

## Real world solution design

### Scalability

The in-memory storage would be limiting in a real-world scenario, where a single instance of a message broker would need to be able to handle multiple connections, not to mention be able to scare horizontally with multiple instances behind a load balancer.
In this case, more appropriate storage solutions would be key-value stores like Redis or databases like PostgreSQL.

I could also reduce the API layer to a thinner one on top of RabbitMQ or Kafka, which already satisfy by themselves most of the requirements of the broker. I could also a rate limiter to control the number of requests to the broker, preventing it from being overwhelmed by too many requests in a short period.

Regarding the reviewer application, I would use a NoSQL database to store the logs, like Elasticsearch.

Features that need to be added to the broker are the possibility to unsubscribe from topics, error handling, retries, dead letter queues for messages that could not be delivered, and message expiration.

### Security

In a real-world scenario, I would add authentication and authorization to the broker and reviewer applications. Being this service-to-service communication, if I were using a cloud solution, I would provide each application with its own service account, and generate temporary credentials.

I would also add encryption to the messages exchanged between each application.

### Prerequisites
- Python 3.13
- Docker
- Docker Compose
- uv (see [installation guide](https://docs.astral.sh/uv/getting-started/installation/))

### Set up the project and run tests

1. Set up the environment and dependencies using `uv`:
    ```bash
    uv venv
    uv sync
    ```

2. Run the tests using `pytest`:
    ```bash
    uv run pytest
    ```

### Run the Application Locally with Docker Compose

1. Build and start the services:
    ```bash
    docker-compose up --build
    ```

2. Test the system manually
- check the id's of the containers
    ```bash
    docker ps
    ```
- exec into the watcher container and modify some files
    ```bash
    docker exec -it ffb3b915656d bash
    appuser@ffb3b915656d:/app$ cd /tmp/important-docs/
    appuser@ffb3b915656d:/tmp/important-docs$ echo "hello there" >> secret.txt

    appuser@ffb3b915656d:/tmp/important-docs$ cd ..
    appuser@ffb3b915656d:/tmp$ echo "love poetry" >> shakespeare.txt
    appuser@ffb3b915656d:/tmp$
    ```
- exec into the reviewer container and check the logs
    ```bash
    docker exec -it 6a05d3f0e7dd bash
    appuser@6a05d3f0e7dd:/app$ cat reviewer_app.log
    2024-11-22 20:53:20,868 - reviewer_app_file - INFO - 2024-11-22T20:53:20.843856 /tmp/important-docs/secret.txt
    2024-11-22 20:54:56,810 - reviewer_app_file - INFO - 2024-11-22T20:54:56.802723 /tmp/shakespeare.txt
    ```
- check the stdout logs of docker-compose to see that only the important file changes have been logged
    ```bash
    reviewer-1  | 2024-11-22 20:53:20,869 - reviewer_app_stdout - INFO - 2024-11-22T20:53:20.843856 /tmp/important-docs/secret.txt ---
    reviewer-1  | +++
    reviewer-1  | @@ -1 +1,2 @@
    reviewer-1  |  Super secret content
    reviewer-1  | +hello there
    ```
- you can also run a second subscriber from your terminal, to try out a different subscription
    ```bash
    CALLBACK_URL=http://host.docker.internal:8002/callback python -m reviewer.cli /tmp/to-do/~
    ```

3. Stop the services
