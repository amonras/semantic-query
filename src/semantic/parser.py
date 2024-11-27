"""
This file provides the functionality to parse a PDF document and return its content as a list of documents.
"""
from pathlib import Path
from typing import Optional

from openparse.schemas import ParsedDocument


def parse(source_path: Path, target_path: Optional[Path] = None, engine='openparse') -> ParsedDocument:
    if engine == 'openparse':
        import openparse

        parser = openparse.DocumentParser()
        parsed_doc: ParsedDocument = parser.parse(source_path)

        if target_path:
            with open(target_path, "w") as file:
                file.write(parsed_doc.json())
        else:
            for node in parsed_doc.nodes:
                print(node)

        return parsed_doc
    else:
        from llmsherpa.readers import LayoutPDFReader

        llmsherpa_api_url = "http://localhost:5001/api/parseDocument?renderFormat=all"
        pdf_reader = LayoutPDFReader(llmsherpa_api_url)
        doc = pdf_reader.read_pdf(source_path.__str__())



