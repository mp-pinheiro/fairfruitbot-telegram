"""TODO: This module is deprecated."""

from fetchers import Fetcher


class NewsFetcher(Fetcher):
    def __init__(self):
        super().__init__()
        self._url = "https://joaobidu.com.br/ultimas-noticias/"

    def _fetch_details(self, soup):
        # fetch news summary
        doc = soup.find("div", {"class": "p402_premium"})
        summary = ""
        element_map = {}
        for element in doc:
            if element.name == "p":
                if element.string and element.string.strip():
                    # probably a title
                    if not element.get("class") or not (
                        element.get("class") and element.get("class")[0] == "idCP"
                    ):
                        # gets rid of weird id on last element
                        summary += f"\n\n<b>{element.string.strip()}</b>\n"
                else:
                    # probably a normal text
                    children = element.findChildren()
                    for child in children:
                        # iterate over children
                        if child.string and child.string.strip():
                            if child.name == "p":
                                # if <p> element, probably a normal paragraph
                                element_map[child.string.strip()] = child.name
                                summary += child.string.strip()
                            elif child.string.strip() in element_map:
                                # if the same string is found with a different
                                # element, it's probably an annoying ad, so
                                # remove it
                                summary = summary.replace(child.string.strip(), "")

        return {"summary": summary}

    def _fetch_latest(self, soup):
        parent = soup.find("div", class_="destaqueNoticia")

        relative = parent.find("a")["href"].split("/")[-1]
        url = self._url.format(news=f"{relative}.phtml")
        title = parent.find("div", class_="infoNoticia").find("h2").string

        return {"url": url, "title": title}

    def fetch(self):
        response = {}

        # extract latest news
        url = self._url.format(news="")
        soup = self._make_soup(url)
        data = self._fetch_latest(soup)
        response.update(data)

        # extract details
        soup = self._make_soup(data["url"])
        data = self._fetch_details(soup)
        response.update(data)

        return response
