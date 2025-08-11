import json
import logging
import os
from typing import Any, Dict
import httpx
from mcp.server.fastmcp import FastMCP

# 포트폴리오 전용 MCP 서버 설정
mcp = FastMCP("StockAgent")


def _load_json(source: str) -> Dict[str, Any]:
    """source가 URL이면 HTTP로, 아니면 로컬 파일로 JSON을 로드."""
    if source.startswith("http://") or source.startswith("https://"):
        with httpx.Client(timeout=20.0) as client:
            resp = client.get(source)
            resp.raise_for_status()
            return resp.json()
    with open(source, "r", encoding="utf-8") as f:
        return json.load(f)


def get_portfolio_by_key(access_key: str, source: str = "aa.json") -> Dict[str, Any]:
    data = _load_json(source)
    if access_key not in data:
        raise KeyError(f"존재하지 않는 access_key: {access_key}")
    return data[access_key]


@mcp.tool()
def is_portfolio_question(question: str) -> Dict[str, Any]:
    """
    사용자의 질문이 포트폴리오 관련 질문인지 확인합니다.
    
    이 도구는 LLM이 사용자의 질문이 포트폴리오 관련인지 판단할 때 사용됩니다.
    
    Parameters:
    - question: 사용자가 한 질문
    
    Returns:
    - is_portfolio_related: 포트폴리오 관련 질문인지 여부 (boolean)
    - reason: 판단 이유 (string)
    """
    portfolio_keywords = [
        "포트폴리오", "내 주식", "내 투자", "보유 주식", "투자 현황", 
        "내 계좌", "내 자산", "투자 성과", "수익률", "보유 종목"
    ]
    
    question_lower = question.lower()
    is_related = any(keyword in question_lower for keyword in portfolio_keywords)
    
    reason = "포트폴리오 관련 키워드가 포함되어 있습니다." if is_related else "포트폴리오 관련 키워드가 없습니다."
    
    return {
        "is_portfolio_related": is_related,
        "reason": reason,
        "detected_keywords": [kw for kw in portfolio_keywords if kw in question_lower]
    }


@mcp.tool()
def get_portfolio(access_key: str | None = None, source: str = "https://jsonbin.io/689589fcf7e7a370d1f70914") -> Dict[str, Any]:
    """
    사용자의 주식 포트폴리오 정보를 조회합니다.
    
    이 도구는 다음 상황에서만 사용하세요:
    - 사용자가 자신의 포트폴리오 정보를 요청할 때
    - 사용자가 주식 투자 현황을 알고 싶어할 때
    - 사용자가 투자 성과나 포트폴리오 구성에 대해 질문할 때
    
    사용하지 말아야 할 상황:
    - 일반적인 주식 정보나 시장 정보 요청
    - 포트폴리오와 관련 없는 질문
    - 투자 조언이나 추천 요청

    Parameters:
    - access_key: 조회할 사용자의 고유 식별자 (기본값: "user123")
    - source: 포트폴리오 데이터가 저장된 JSON 위치 (기본: https://jsonbin.io/689589fcf7e7a370d1f70914)
    
    Returns:
    - 사용자의 포트폴리오 정보 (보유 주식, 수량, 투자 금액 등)
    """
    if not access_key:
        access_key = os.getenv("DEFAULT_ACCESS_KEY", "user123")
    return get_portfolio_by_key(access_key, source)


if __name__ == "__main__":
    # 등록된 도구들 출력
    print("=== MCP 서버 시작 ===")
    print(f"서버 이름: {mcp.name}")
    print("등록된 도구들:")
    print("- get_portfolio: 포트폴리오 정보 조회")
    print("- is_portfolio_question: 포트폴리오 관련 질문 확인")
    print("==================")
    
    # MCP 서버 시작
    mcp.run()

