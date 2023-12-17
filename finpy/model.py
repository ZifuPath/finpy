import datetime
from typing import List,Optional
from pydantic import BaseModel,Field,field_validator,ValidationError
class OptionSchema(BaseModel):
    openInterest: Optional[float]
    changeinOpenInterest: Optional[float]
    pchangeinOpenInterest: Optional[float]
    totalTradedVolume: Optional[int]
    impliedVolatility: Optional[float]
    lastPrice: Optional[float]
    change: Optional[float]
    pChange: Optional[float]

class Chain(BaseModel):
    PE: Optional[OptionSchema] =None
    CE: Optional[OptionSchema] =None
    expiryDate: str
    strikePrice: int

class ChainData(BaseModel):
    response: List[Chain]

class CandleInput(BaseModel):
    symbol: str
    start_date: str
    end_date: str

    @field_validator('start_date','end_date')
    def validate_date(cls,value):
        try:
            datetime.datetime.strptime(value,"%d-%m-%Y")
            return value
        except ValidationError as e:
            raise ValueError(e.errors())

class EquityRow(BaseModel):
    symbol: str = Field(alias='CH_SYMBOL')
    datetime: str = Field(alias='TIMESTAMP')
    open: float = Field(alias='CH_OPENING_PRICE')
    high: float = Field(alias='CH_TRADE_HIGH_PRICE')
    low: float = Field(alias='CH_TRADE_LOW_PRICE')
    close: float =Field(alias='CH_CLOSING_PRICE')
    prev_close: float = Field( alias='CH_PREVIOUS_CLS_PRICE')
    volume: float = Field(alias='CH_TOT_TRADED_VAL')
    vwap: float = Field(alias='VWAP')

class EquityData(BaseModel):
    response: List[EquityRow]

