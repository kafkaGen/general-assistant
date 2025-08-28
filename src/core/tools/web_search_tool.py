import json

from langchain_core.tools import StructuredTool
from tavily import AsyncTavilyClient

from src.settings.tools import WebSearchToolSettings


class WebSearchTool:
    def __init__(
        self,
        settings: WebSearchToolSettings,
    ) -> None:
        self.settings = settings

        self._tavily_client = AsyncTavilyClient()

    async def search_web(self, query: str) -> str:
        """
        Search the internet for the most recent and relevant public information
        on provided topic.

        Args:
            query (str): A natural language question or topic for search engine.
                         Example: "EU elections outcome", "latest LLM breakthroughs"

        Returns:
            str: A JSON string with:
                - results (List[dict]): Each entry includes:
                    - title (str)
                    - url (str): URL of the search result
                    - content (str): short summary/snippet
                    - metadata (dict): metadata of the search result

        Usage Note:
            Use this tool when you need to find fresh information not present in the
            assistant's memory to answer the user's question.
        """
        response = await self._tavily_client.search(
            query=query,
            search_depth="advanced",
            max_results=self.settings.max_results,
        )
        result_str = json.dumps(response["results"], indent=4)

        return result_str

    # async def fetch_webpage_text(self, urls: str | list[str]) -> dict:
    #     """
    #     Extract full text content from given web URLs.

    #     Args:
    #         urls (str or List[str]): One or more URLs to extract content from.
    #                                  Example: "https://example.com" or ["https://a.com",
    #                                  "https://b.com"]

    #     Returns:
    #         dict: A structured dictionary with:
    #             - results (List[dict]): Each entry includes:
    #                 - url (str)
    #                 - title (str)
    #                 - content (str): cleaned readable text
    #                 - metadata (dict)

    #     Usage Note:
    #         Use this tool when URLs are known and full article or page content is
    #         needed for deeper analysis.
    #     """
    #     response = await self._tavily_client.extract(
    #         urls=urls,
    #         extract_depth="advanced",
    #         include_images=True,
    #     )
    #     return response

    def get_tools(self):
        return [
            StructuredTool.from_function(
                func=self.search_web,
                name=self.search_web.__name__,
                description=str(self.search_web.__doc__),
                coroutine=self.search_web,
            ),
            # StructuredTool.from_function(
            #     func=self.fetch_webpage_text,
            #     name=self.fetch_webpage_text.__name__,
            #     description=str(self.fetch_webpage_text.__doc__),
            #     coroutine=self.fetch_webpage_text,
            # ),
        ]
