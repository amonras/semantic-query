from typing import Callable, List
import re
from langchain_text_splitters import TextSplitter


class ArticleSplitter(TextSplitter):
    def __init__(self,
                 chunk_size: int = 4000,
                 chunk_overlap: int = 200,
                 length_function: Callable[[str], int] = len,
                 keep_separator: bool = False,
                 add_start_index: bool = False,
                 strip_whitespace: bool = True,
                 title_pattern: str = r"^(?:[A-Z][a-z]*\s*)+$"
                 ):
        super().__init__(chunk_size=chunk_size,
                         chunk_overlap=chunk_overlap,
                         length_function=length_function,
                         keep_separator=keep_separator,
                         add_start_index=add_start_index,
                         strip_whitespace=strip_whitespace)
        self.title_pattern = title_pattern

    def split_text(self, text: str) -> List[str]:
        """
        Split the text into articles.
        :param text:
        :return:
        """
        articles = []
        article = ""
        for line in text.split("\n"):
            if re.match(self.title_pattern, line):
                if article:
                    articles.append(article)
                article = line
            else:
                article += f"\n{line}"
        articles.append(article)
        return articles
