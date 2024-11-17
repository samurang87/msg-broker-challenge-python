## Summary of requirements

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