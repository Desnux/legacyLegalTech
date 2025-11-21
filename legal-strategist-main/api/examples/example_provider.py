import os
import random

from langchain_core.documents import Document

from models.pydantic import MissingPaymentDocumentType, StorageType


JUDICIAL_COLLECTION_DEMAND_EXCEPTION_EXAMPLES_PATH = "examples/local/judicial_collection_demand_exception"
JUDICIAL_COLLECTION_DEMAND_TEXT_EXAMPLES_PATH = "examples/local/judicial_collection_demand_text"
MISSING_PAYMENT_ARGUMENT_EXAMPLES_PATH = "examples/local/missing_payment_argument"


class ExampleProvider:
    def __init__(self, storage_type: StorageType = StorageType.LOCAL) -> None:
        self.storage_type = storage_type

    def get_judicial_collection_demand_exception(self, section: str, seed: int = 0) -> list[Document]:
        if self.storage_type == StorageType.S3:
            raise ValueError("No text files found in the specified storage.")
        directory = f"{JUDICIAL_COLLECTION_DEMAND_EXCEPTION_EXAMPLES_PATH}/{section}"
        return self._get_content(directory, seed)

    def get_judicial_collection_demand_text(self, section: str, seed: int = 0) -> list[Document]:
        if self.storage_type == StorageType.S3:
            raise ValueError("No text files found in the specified storage.")
        directory = f"{JUDICIAL_COLLECTION_DEMAND_TEXT_EXAMPLES_PATH}/{section}"
        return self._get_content(directory, seed)
    
    def get_missing_payment_argument(self, document_type: MissingPaymentDocumentType, seed: int = 0) -> list[Document]:
        if self.storage_type == StorageType.S3:
            raise ValueError("No text files found in the specified storage.")
        directory = f"{MISSING_PAYMENT_ARGUMENT_EXAMPLES_PATH}/{document_type.value}"
        return self._get_content(directory, seed)

    def _get_content(self, directory: str, seed: int) -> list[Document]:
        local_random = random.Random(seed if seed != 0 else None)
        if not os.path.isdir(directory):
            raise FileNotFoundError(f"Directory {directory} does not exist.")

        files = [f for f in os.listdir(directory) if f.endswith(".txt")]
        if not files:
            raise ValueError("No text files found in the specified storage.")
        
        random_index = local_random.randint(0, len(files) - 1)
        example_file = files[random_index]
        with open(os.path.join(os.getcwd(), directory, example_file)) as f:
            example_content = f.read()

        return [Document(page_content=content) for content in example_content.splitlines()]
