import json
from pathlib import Path
from typing import Callable, Dict, List, Optional, Union

from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseLoader


class JSONLoader(BaseLoader):
    def __init__(
            self,
            file_path: Union[str, Path],
            content_key: Optional[str] = None,
            json_lines: bool = False,
    ):
        self.file_path = Path(file_path).resolve()
        self._content_key = content_key
        self._json_lines = json_lines

    def create_documents(self, processed_data):
        documents = []
        for item in processed_data:
            content = ''.join(item)
            document = Document(page_content=content, metadata={})
            documents.append(document)
        return documents

    #处理dict{}
    def process_item(self, item, prefix=""):
        if isinstance(item, dict):
            result = []
            if self._content_key is not None:
                if self._content_key not in item.keys():
                    print("The content key doesn't exist.")
                    print(item)
                    return result
                else:
                    new_prefix = f"{prefix}.{self._content_key}" if prefix else self._content_key
                    result.extend(self.process_item(item[self._content_key], new_prefix))
                    return result
            for key, value in item.items():
                new_prefix = f"{prefix}.{key}" if prefix else key
                result.extend(self.process_item(value, new_prefix))
            return result
        elif isinstance(item, list):
            result = []
            for value in item:
                result.extend(self.process_item(value, prefix))
            return result
        else:
            return [f"{prefix}: {item}"]

    def process_json(self, data):
        if isinstance(data, list):
            processed_data = []
            for item in data:
                processed_data.extend(self.process_item(item))
            return processed_data
        elif isinstance(data, dict):
            return self.process_item(data)
        else:
            return []

    def load(self) -> List[Document]:
        """Load and return documents from the JSON file."""
        docs = []
        if self._json_lines == True:
            with self.file_path.open(encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        data = json.loads(line)
                        processed_json = self.process_json(data)
                        docs = docs + self.create_documents(processed_json)
        elif self._json_lines == False:
            with open(self.file_path, 'r') as json_file:
                try:
                    data = json.load(json_file)
                    processed_json = self.process_json(data)
                    docs = self.create_documents(processed_json)
                except json.JSONDecodeError:
                    print("Error: Invalid JSON format in the file.")
        return docs


