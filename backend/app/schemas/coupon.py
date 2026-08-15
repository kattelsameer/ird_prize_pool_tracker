from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CouponCreate(BaseModel):
    coupon_code: str = Field(min_length=1, max_length=64)
    transaction_date: date | None = None
    fiscal_year: str | None = Field(default=None, max_length=16)
    network: str | None = Field(default=None, max_length=80)

    @field_validator("coupon_code")
    @classmethod
    def coupon_code_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("coupon_code must not be blank")
        return value


class CouponUpdate(BaseModel):
    coupon_code: str | None = Field(default=None, min_length=1, max_length=64)
    transaction_date: date | None = None
    fiscal_year: str | None = Field(default=None, max_length=16)
    network: str | None = Field(default=None, max_length=80)


class CouponRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    coupon_id: str
    coupon_code: str
    normalized_coupon_code: str
    transaction_date: date | None
    fiscal_year: str | None
    network: str | None
    created_at: datetime
    updated_at: datetime
