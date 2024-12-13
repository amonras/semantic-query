import pdfplumber

from models.node import Node


def extract_paragraphs(pdf_path) -> Node:
    paragraphs = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text_blocks = page.extract_words(use_text_flow=True)
            # Merge text blocks into paragraphs based on proximity
            current_paragraph = ""
            last_bottom = None
            for block in text_blocks:
                if last_bottom and block['top'] - last_bottom > 10:  # Gap indicates new paragraph
                    paragraphs.append(current_paragraph.strip())
                    current_paragraph = ""
                current_paragraph += f" {block['text']}"
                last_bottom = block['bottom']
            if current_paragraph:
                paragraphs.append(current_paragraph.strip())  # Append last paragraph

    paragraphs = [para for para in paragraphs if para != 'JURISPRUDENCIA' and len(para) >= 4]  # Remove empty paragraphs

    return Node(
        level='document',
        content=paragraphs[0],
        children=[
            Node(
                level='paragraph',
                content=para,
                children=[]
            )
            for para in paragraphs
        ]
    )
