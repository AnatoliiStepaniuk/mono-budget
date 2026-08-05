from datetime import datetime

from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.event_handler.openapi.models import Server

from pydantic import BaseModel, Field
from typing import List


from db_client import get_transactions_in_range

app = APIGatewayRestResolver(enable_validation=True)


class Transaction(BaseModel):
    time: int
    category: str
    amount: float

class TransactionsRequest(BaseModel):
    from_date: str = Field(alias="fromDate", description="Start date (inclusive) of the transactions query timerange in format YYYY-MM-DD. The instant of the beginning of this date (UTC) will be used in query 00:00:00.000", default=None)
    to_date: str = Field(alias="toDate", description="End date (exclusive) of the transactions query timerange in format YYYY-MM-DD. The instant of the beginning of this date (UTC) will be used in query 00:00:00.000", default=None)
    categories: List[str] = Field(description="List of transaction categories to include. If not-included or empty, means \"all categories\". Full of list of categories: living,food,health,transport,growth,relax,travel,look,other,parents,hobby,girlfriend,donate", default=[])


@app.get("/openapispec", include_in_schema=False)
def get_openapi():
    servers = [

        Server(url="https://fv3nr78xig.execute-api.eu-central-1.amazonaws.com/Prod"), # TODO unhardcode (maybe just use a cognito domain?)
    ]
    return app.get_openapi_json_schema(title="My API", version="1.0.0", openapi_version="3.1.0", servers=servers, description="Powertools OpenAPI")


@app.post("/transactions")
def get_transactions(input: TransactionsRequest) -> List[Transaction]:

    from_seconds = date_to_utc_seconds(input.from_date)
    to_seconds = date_to_utc_seconds(input.to_date)

    print(f"fromSeconds: {from_seconds}, toSeconds: {to_seconds}, categories: {input.categories}")
    #
    return to_transaction_objects(get_transactions_in_range(from_seconds, to_seconds, input.categories))


def date_to_utc_seconds(date_string):
    parsed_date = datetime.strptime(date_string, "%Y-%m-%d")
    return int((parsed_date - datetime(1970, 1, 1)).total_seconds())


def to_transaction_objects(transactions):
    transaction_objects = [
        Transaction(
            time=transaction['time'],
            category=transaction['category'],
            amount= transaction['amount'] / (-100)
        )
        for transaction in transactions
    ]

    return transaction_objects

def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)