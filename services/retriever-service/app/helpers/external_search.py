from googlesearch import SearchResult, search


class ExternalSearch():
    def __init__(
        self, 
        unique: bool=True,
        advanced: bool=True,
        num_results=5, 
        sleep_interval: int=5, 
        lang: str="vi", 
        region: str="vi"
    ):
        self.unique = unique
        self.advanced = advanced
        self.num_results = num_results
        self.sleep_interval = sleep_interval
        self.lang = lang
        self.region = region

    def __extract_html(self, content):
        pass

    def __google_search(self, content: str) -> list[SearchResult]:
        return search(
            content, 
            num_results=self.num_results, 
            lang=self.lang, 
            sleep_interval=self.sleep_interval, 
            advanced=self.advanced, 
            unique=self.unique, 
            region=self.region
        )