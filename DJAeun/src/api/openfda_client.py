"""OpenFDA API 클라이언트 - 실시간 API 호출"""
import requests
from typing import Optional
from src.config import OPENFDA_BASE_URL, OPENFDA_API_KEY, OPENFDA_LABEL_ENDPOINT, SEARCH_LIMIT


class OpenFDAClient:
    """OpenFDA API 호출을 담당하는 클라이언트 클래스"""

    def __init__(self):
        self.base_url = OPENFDA_BASE_URL
        self.api_key = OPENFDA_API_KEY
        self.timeout = 30

    def _build_url(self, endpoint: str, search_query: str, limit: int = SEARCH_LIMIT) -> str:
        """API 요청 URL 생성"""
        url = f"{self.base_url}{endpoint}"
        params = f"?search={search_query}&limit={limit}"
        if self.api_key:
            params += f"&api_key={self.api_key}"
        return url + params

    def _make_request(self, url: str) -> dict:
        """API 요청 실행 및 응답 반환"""
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                return {"error": "No results found", "results": []}
            return {"error": str(e), "results": []}
        except requests.RequestException as e:
            return {"error": str(e), "results": []}

    def search_drug_label(self, field: str, term: str) -> list[dict]:
        """
        의약품 라벨 정보 검색
        - field: 검색 필드 (openfda.brand_name, openfda.generic_name, indications_and_usage 등)
        - term: 검색어
        """
        # 검색어에 공백이 있으면 따옴표로 감싸기
        if " " in term:
            search_query = f'{field}:"{term}"'
        else:
            search_query = f"{field}:{term}"

        url = self._build_url(OPENFDA_LABEL_ENDPOINT, search_query)
        data = self._make_request(url)
        return data.get("results", [])


def search_by_brand_name(brand_name: str) -> list[dict]:
    """브랜드명으로 검색"""
    client = OpenFDAClient()
    return client.search_drug_label("openfda.brand_name", brand_name)


def search_by_generic_name(generic_name: str) -> list[dict]:
    """일반명(성분명)으로 검색"""
    client = OpenFDAClient()
    return client.search_drug_label("openfda.generic_name", generic_name)


def search_by_indication(indication: str) -> list[dict]:
    """적응증(효능)으로 검색"""
    client = OpenFDAClient()
    return client.search_drug_label("indications_and_usage", indication)
