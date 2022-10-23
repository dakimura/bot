from typing import TypedDict, Optional, List


class Order(TypedDict):
    symbol: str
    type: str
    side: str
    qty: Optional[str]
    created_at: str


class Status(TypedDict):
    equity: str
    buying_power: str
    order_history: List[Order]

