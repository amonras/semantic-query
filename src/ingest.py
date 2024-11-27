from embedding import Embedding
from scripts.download_codigo_civil import download_civil_code, get_document_structure
from storage import get_storage


def ingest():
    print("Ingesting the consolidated Civil Code...")
    text = download_civil_code()

    print("Dividing into articles...")
    main_node = get_document_structure(text)

    store = get_storage()
    store.store(main_node)


if __name__ == "__main__":
    ingest()
