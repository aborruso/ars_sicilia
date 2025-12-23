import requests
from urllib.parse import urlencode, quote
import time
import re
from bs4 import BeautifulSoup
from typing import Optional, List, Dict, Any


class ARSClient:
    """Client for ARS Sicilia Disegni di Legge API."""

    BASE_URL = "https://dati.ars.sicilia.it"

    def __init__(self, cookie_jar=None):
        """
        Initialize ARS API client.

        Args:
            cookie_jar: Optional cookie jar for session persistence
        """
        self.session = requests.Session()
        if cookie_jar:
            self.session.cookies.update(cookie_jar)
        self.current_query_id = None
        self.current_query = None

    def _get_timestamp(self) -> int:
        """Get current timestamp for cache busting."""
        return int(time.time() * 1000)

    def search(
        self,
        legisl: int,
        anno: Optional[str] = None,
        legge: Optional[str] = None,
        query_text: Optional[str] = None,
        terms: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute a search query and return results page.

        Args:
            legisl: Legislature number (10-18)
            anno: Optional year filter (e.g., "2024")
            legge: Optional bill number
            query_text: Custom query in ARS syntax
            terms: Simple search terms

        Returns:
            Dict with response data including total_results
        """
        if not query_text:
            if terms:
                query_text = terms
            else:
                query_text = f"({legisl}.LEGISL)"

        # Store the original query (unencoded)
        self.current_query = query_text

        params = {
            "legisl": str(legisl),
            "anno": anno or "",
            "legge": legge or "",
            "iter": "",
            "iterComm": "",
            "iterAltro": "",
            "iterComm2": "",
            "iterAltro2": "",
            "tipo": "E",
            "terms": "",
            "searchAction": "execute",
            "queryText": query_text,
        }

        # Execute search POST
        response = self.session.post(
            f"{self.BASE_URL}/home/cerca/221.jsp",
            data=params,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        # The POST doesn't redirect via HTTP, but we need to manually call
        # the results page with the query
        results_page = self.get_results_page(ica_query=self.current_query)

        return {
            "status_code": response.status_code,
            "post_url": response.url,
            "results_url": f"{self.BASE_URL}/icaro/default.jsp",
            "cookies": dict(self.session.cookies),
            "total_results": results_page.get("total_results"),
            "query": self.current_query,
        }

    def get_results_page(
        self, ica_db: str = "221", ica_query: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get main results page.

        Args:
            ica_db: Database ID (default: 221 for Disegni di Legge)
            ica_query: Optional query in ARS syntax

        Returns:
            Dict with page data
        """
        params = {"icaDB": ica_db, "_": self._get_timestamp()}

        if ica_query:
            params["icaQuery"] = ica_query

        response = self.session.get(f"{self.BASE_URL}/icaro/default.jsp", params=params)
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract total results
        results_header = soup.find(
            lambda tag: tag.name == "h3" and re.search(r"\(\d+\)", tag.get_text())
        )
        total_results = None
        if results_header:
            match = re.search(r"\((\d+)\)", results_header.get_text())
            if match:
                total_results = int(match.group(1))

        # Extract query ID from footer (e.g., "QRY1 ((18.LEGISL))")
        query_id = None
        qry_div = soup.find("footer")
        if qry_div:
            match = re.search(r"QRY(\d+)", qry_div.get_text())
            if match:
                query_id = int(match.group(1))
                self.current_query_id = query_id

        return {
            "status_code": response.status_code,
            "html": response.text,
            "soup": soup,
            "total_results": total_results,
            "query_id": query_id or self.current_query_id,
        }

    def get_results_list(self, page: int = 1, use_ajax: bool = True) -> Dict[str, Any]:
        """
        Get paginated results list.

        Args:
            page: Page number (1-based)
            use_ajax: If True, calls AJAX endpoint directly

        Returns:
            Dict with results data
        """
        params = {"_": self._get_timestamp()}

        if use_ajax:
            url = f"{self.BASE_URL}/icaro/shortList.jsp"
            if page > 1:
                params["setPage"] = str(page)
            headers = {"X-Requested-With": "XMLHttpRequest"}
        else:
            url = f"{self.BASE_URL}/icaro/default.jsp"
            params["icaAction"] = "showQuery"
            params["id"] = "1"
            params["doc"] = "FALSE"
            headers = {}

        response = self.session.get(url, params=params, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract pagination info
        pagination = {}
        pagina_di = soup.find("span", class_="pagina_di")
        if pagina_di:
            match = re.search(r"Pagina\s+(\d+)\s+di\s+(\d+)", pagina_di.get_text())
            if match:
                pagination["current_page"] = int(match.group(1))
                pagination["total_pages"] = int(match.group(2))

        # Extract results
        results = []
        result_items = soup.find("ul", id="shortListTable")
        if result_items:
            items = result_items.find_all("li", recursive=False)[1:]  # Skip header

            for idx, item in enumerate(items, 1):
                result = self._parse_result_item(item, idx)
                if result:
                    results.append(result)

        return {
            "status_code": response.status_code,
            "html": response.text,
            "soup": soup,
            "results": results,
            "pagination": pagination,
            "page": page,
        }

    def _parse_result_item(self, item, index: int) -> Optional[Dict[str, Any]]:
        """Parse a single result item from HTML."""
        try:
            divs = item.find_all("div", class_="intesta")

            if len(divs) < 4:
                return None

            # Legislature
            legisl = divs[0].get_text(strip=True)

            # Number
            number = divs[1].get_text(strip=True)

            # Date (DD.MM.YY format)
            date_str = divs[2].get_text(strip=True)

            # Title
            title_div = item.find("div", class_="intesta_50")
            if title_div:
                title_link = title_div.find("a")
                if title_link:
                    title = title_link.get_text(strip=True)
                else:
                    h3 = title_div.find("h3")
                    title = h3.get_text(strip=True) if h3 else ""
            else:
                title = ""

            return {
                "index": index,
                "legislature": legisl,
                "number": number,
                "date": date_str,
                "title": title,
            }
        except Exception as e:
            print(f"Error parsing result item {index}: {e}")
            return None

    def get_document(self, doc_id: int) -> Dict[str, Any]:
        """
        Get document detail page.

        Args:
            doc_id: Document ID (1-indexed position in results)

        Returns:
            Dict with document data
        """
        params = {"icaAction": "showDoc", "id": str(doc_id), "_": self._get_timestamp()}

        response = self.session.get(f"{self.BASE_URL}/icaro/default.jsp", params=params)
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract document info from header
        doc_info = {}
        title_heading = soup.find(
            lambda tag: tag.name == "h1" and re.search(r"DDL N\.", tag.get_text())
        )
        if title_heading:
            title_text = title_heading.get_text()
            match = re.search(r"DDL N\.(\d+)\s+DEL\s+(\d+)\s+(\w+)\s+(\d+)", title_text)
            if match:
                doc_info["bill_number"] = match.group(1)
                doc_info["date_day"] = match.group(2)
                doc_info["date_month"] = match.group(3)
                doc_info["date_year"] = match.group(4)

        # Extract sections
        sections = {}
        blocchi = soup.find_all("div", class_="blocchi_info")
        for blocco in blocchi:
            title_div = blocco.find("div", class_="title")
            content_div = blocco.find("div", class_="testo_gestionale")

            if title_div and content_div:
                section_title = title_div.get_text(strip=True)
                sections[section_title.lower()] = content_div.get_text(strip=True)

        return {
            "status_code": response.status_code,
            "url": response.url,
            "html": response.text,
            "soup": soup,
            "info": doc_info,
            "sections": sections,
        }

    def get_document_content(self, query_id: int, doc_id: int) -> Dict[str, Any]:
        """
        Get full document content via AJAX.

        Args:
            query_id: Query ID (from search results)
            doc_id: Document ID (1-indexed)

        Returns:
            Dict with document content
        """
        params = {
            "icaQueryId": str(query_id),
            "icaDocId": str(doc_id),
            "_": self._get_timestamp(),
        }

        response = self.session.get(
            f"{self.BASE_URL}/icaro/doc221-1.jsp",
            params=params,
            headers={"X-Requested-With": "XMLHttpRequest"},
        )

        soup = BeautifulSoup(response.text, "html.parser")

        # Parse document sections
        content = {}
        blocchi = soup.find_all("div", class_="blocchi_info")

        for blocco in blocchi:
            title_div = blocco.find("div", class_="title")
            content_div = blocco.find("div", class_="testo_gestionale")

            if title_div and content_div:
                section_title = title_div.get_text(strip=True)

                # Handle different section types
                if section_title == "Titolo":
                    content["title"] = content_div.get_text(strip=True)
                elif section_title == "Iter":
                    # Parse iteration statuses
                    iter_data = {}
                    paragraphs = content_div.find_all("p")
                    for p in paragraphs:
                        strong = p.find("strong")
                        if strong:
                            key = strong.get_text(strip=True)
                            value = p.get_text().replace(key, "", 1).strip()
                            iter_data[key.lower()] = value
                    content["iteration"] = iter_data
                else:
                    content[section_title.lower()] = content_div.get_text(strip=True)

        # Parse full text from tab div
        tab_div = soup.find("div", class_="tab")
        if tab_div:
            testo_div = tab_div.find("div", class_="testo_gestionale")
            if testo_div:
                pre = testo_div.find("pre")
                if pre:
                    content["full_text"] = pre.get_text()
                else:
                    content["full_text"] = testo_div.get_text()

        return {
            "status_code": response.status_code,
            "html": response.text,
            "soup": soup,
            "content": content,
        }

    def show_query(self, query_id: int) -> Dict[str, Any]:
        """Return to query results list."""
        params = {
            "icaAction": "showQuery",
            "id": str(query_id),
            "doc": "FALSE",
            "_": self._get_timestamp(),
        }

        response = self.session.get(f"{self.BASE_URL}/icaro/default.jsp", params=params)

        return {"status_code": response.status_code, "text": response.text}

    def close_query(self, query_id: int) -> Dict[str, Any]:
        """Close/delete a search query."""
        params = {
            "icaAction": "closeQuery",
            "id": str(query_id),
            "_": self._get_timestamp(),
        }

        response = self.session.get(f"{self.BASE_URL}/icaro/default.jsp", params=params)

        return {"status_code": response.status_code, "text": response.text}

    def keep_alive(self, counter: int) -> Dict[str, Any]:
        """Send keep-alive request to maintain session."""
        params = {"cnt": str(counter), "_": self._get_timestamp()}

        response = self.session.get(f"{self.BASE_URL}/icaro/alive.jsp", params=params)

        return {"status_code": response.status_code, "text": response.text}

    def get_all_bills(
        self, legisl: int, max_pages: Optional[int] = None, delay: float = 1.0
    ) -> List[Dict[str, Any]]:
        """
        Get all bills from a legislature (paginated).

        Args:
            legisl: Legislature number
            max_pages: Maximum pages to fetch (None for all)
            delay: Seconds to wait between page requests

        Returns:
            List of all result dictionaries
        """
        all_results = []
        page = 1

        while True:
            # Fetch current page
            result = self.get_results_list(page=page)

            if result["results"]:
                all_results.extend(result["results"])
                print(f"Fetched page {page}: {len(result['results'])} results")
            else:
                print(f"No more results on page {page}")
                break

            # Check pagination
            if "pagination" in result:
                total_pages = result["pagination"].get("total_pages", 1)
                if page >= total_pages:
                    print(f"Reached end: page {page} of {total_pages}")
                    break

            if max_pages and page >= max_pages:
                print(f"Reached max_pages limit: {page}")
                break

            page += 1

            # Rate limiting
            time.sleep(delay)

        return all_results

    def search_by_query(self, query: str, legisl: int = 18) -> List[Dict[str, Any]]:
        """
        Search using custom query syntax.

        Args:
            query: Query in ARS syntax
            legisl: Legislature number

        Returns:
            List of matching results
        """
        # Execute search
        result = self.search(legisl=legisl, query_text=query)

        # Get first page of results
        list_result = self.get_results_list(page=1)

        if list_result["results"]:
            return list_result["results"]

        return []

    def get_bill_by_number(
        self, bill_number: str, legisl: int = 18
    ) -> Optional[Dict[str, Any]]:
        """
        Get a specific bill by number.

        Args:
            bill_number: Bill number (e.g., "1052")
            legisl: Legislature number

        Returns:
            Bill dictionary or None if not found
        """
        query = f"(({legisl}.LEGISL) AND {bill_number}.NUMDDL)"
        results = self.search_by_query(query, legisl)

        if results:
            for result in results:
                if result.get("number") == bill_number:
                    # Get full document
                    content = self.get_document_content(
                        self.current_query_id, result["index"]
                    )
                    return {**result, "content": content.get("content", {})}

        return None


def parse_date(date_str: str) -> Optional[str]:
    """Parse DD.MM.YY format to ISO date."""
    try:
        parts = date_str.split(".")
        if len(parts) == 3:
            day = parts[0].zfill(2)
            month = parts[1].zfill(2)
            year = "20" + parts[2]
            return f"{year}-{month}-{day}"
    except Exception:
        pass
    return None


def save_cookies(client: ARSClient, filename: str = "cookies.txt") -> None:
    """Save session cookies to file."""
    with open(filename, "w") as f:
        for name, value in client.session.cookies.items():
            f.write(f"{name}\t{value}\n")
    print(f"Cookies saved to {filename}")


def load_cookies(filename: str = "cookies.txt"):
    """Load session cookies from file."""
    from http.cookiejar import LWPCookieJar

    jar = requests.cookies.RequestsCookieJar()
    try:
        with open(filename, "r") as f:
            for line in f:
                parts = line.strip().split("\t")
                if len(parts) == 2:
                    jar.set(name=parts[0], value=parts[1], domain=".ars.sicilia.it")
        print(f"Cookies loaded from {filename}")
    except FileNotFoundError:
        print(f"No cookie file found: {filename}")
    return jar


if __name__ == "__main__":
    # Example usage
    client = ARSClient()

    # Search for all bills in legislature 18
    print("Searching legislature 18...")
    result = client.search(legisl=18)
    print(f"Search completed. Total results: {result['total_results']}")
    print(f"Query ID: {client.current_query_id}")

    # Get first page of results
    print("\nFetching results list...")
    list_result = client.get_results_list(page=1)
    print(f"Page 1 of {list_result['pagination'].get('total_pages', '?')}")

    # Display first 5 results
    if list_result["results"]:
        print("\nFirst 5 results:")
        for i, item in enumerate(list_result["results"][:5], 1):
            print(
                f"{i}. [{item['legislature']}/{item['number']}] {item['date']} - {item['title']}"
            )

        # Get first document content
        print(f"\nFetching content for first document...")
        content = client.get_document_content(client.current_query_id, 1)
        print(f"Document sections: {list(content['content'].keys())}")
    else:
        print("No results found")
