from watchdog.events import FileSystemEvent


def test_on_modified_directory_ignored(
    cached_content, file_change_handler, publisher_client
):
    event = FileSystemEvent(src_path="/path/to/modified/directory/")
    file_change_handler.on_modified(event)
    file_change_handler.cached_content = cached_content
    assert publisher_client.no_message_published()


def test_on_modified_file_without_changes_ignored(
    file_change_handler, publisher_client, temp_file
):
    event = FileSystemEvent(src_path=temp_file)
    file_change_handler.on_modified(event)
    assert publisher_client.no_message_published()


def test_on_modified_file_successfully_published(
    file_change_handler, publisher_client, temp_file
):
    with open(temp_file, "w") as f:
        f.write("Content of file1 is a recipe")
    event = FileSystemEvent(src_path=temp_file)
    file_change_handler.on_modified(event)
    file_change_handler.cached_content = {
        temp_file: "Content of file1 is a recipe",
        "/path/to/file2.txt": "Content of file2",
    }
    assert publisher_client.one_message_published()
