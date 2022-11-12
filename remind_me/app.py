import boto3
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.parser import event_parser, BaseModel
from datetime import datetime
import os
import string
import random


scheduler = boto3.client('scheduler')
logger = Logger()


class Reminder(BaseModel):
    content: str
    when: datetime
    timezone: str

@event_parser(model=Reminder)
@logger.inject_lambda_context
def handler(event:Reminder, context) -> str:

    random_suffix = ( ''.join(random.choice(string.ascii_lowercase) for i in range(10)) )
    scheduler.create_schedule(
        Name=f"{os.environ['SCHEDULER_NAME']}-{random_suffix}",
        ScheduleExpression=f"at({event.when.strftime('%Y-%m-%dT%H:%M')})",
        Target={
            "Arn": os.environ["WEBHOOK_SNS_ARN"],
            "RoleArn": os.environ["SNS_PUBLISH_ROLE_ARN"],
            "Input": event.content
        },
        FlexibleTimeWindow={ "Mode": "OFF" },
        ScheduleExpressionTimezone=event.timezone)