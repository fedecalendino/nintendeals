from datetime import datetime


class Price:
    def __init__(self, nsuid: str, country: str, currency: str, value: float):
        self.nsuid: str = nsuid

        self.country: str = country
        self.currency: str = currency
        self.value: float = value

        self.sale_value: float = None
        self.sale_start: datetime = None
        self.sale_end: datetime = None

    @property
    def sale_discount(self) -> int:
        if not self.on_sale:
            return 0

        return round(100 * self.sale_value / self.value)

    @property
    def is_free_to_play(self) -> bool:
        return self.value == 0.0

    @property
    def is_sale_active(self) -> bool:
        if not self.on_sale:
            return False

        now = datetime.utcnow()
        return self.sale_end > now > self.sale_start

    @property
    def on_sale(self) -> bool:
        return self.sale_value is not None

    def __repr__(self) -> str:
        if self.on_sale:
            return f"{self.currency} {self.sale_value}*"

        return f"{self.currency} {self.value}"
