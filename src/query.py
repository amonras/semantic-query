from storage import get_storage


def query():
    store = get_storage()
    results = store.query()

    for result in results:
        print(result)


if __name__ == "__main__":
    query()

