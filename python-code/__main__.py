import json
import os
import tempfile

import pulumi
import pulumi_aws as aws
from dotenv import load_dotenv

import create_package_zip

load_dotenv()

PROJECT_NAME = f"{pulumi.get_project()}-{pulumi.get_stack()}"

MEMORY_SIZE = 1024
TIMEOUT = 15
RUNTIME = aws.lambda_.Runtime.PYTHON3D12
TIMEZONE = "Asia/Singapore"

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME")
UPSTASH_REDIS_REST_URL = os.getenv("UPSTASH_REDIS_REST_URL")
UPSTASH_REDIS_REST_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN")

role = aws.iam.Role(
    f"{PROJECT_NAME}-role",
    assume_role_policy=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "lambda.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                }
            ],
        }
    ),
)

aws.iam.RolePolicyAttachment(
    f"{PROJECT_NAME}-policy",
    role=role.name,
    policy_arn=aws.iam.ManagedPolicy.AWS_LAMBDA_BASIC_EXECUTION_ROLE,
)

temp_dir = tempfile.TemporaryDirectory().name
zip_file = "python.zip"

create_package_zip.main(temp_dir, zip_file)

package_layer = aws.lambda_.LayerVersion(
    f"{PROJECT_NAME}-layer",
    layer_name=f"{PROJECT_NAME}-layer",
    code=pulumi.AssetArchive({".": pulumi.FileArchive(f"{temp_dir}/{zip_file}")}),
    compatible_runtimes=[aws.lambda_.Runtime.PYTHON3D12],
)


def create_lambda_function(name, handler, code):
    return aws.lambda_.Function(
        f"{PROJECT_NAME}-{name}-function",
        code=code,
        role=role.arn,
        environment=aws.lambda_.FunctionEnvironmentArgs(
            variables={
                "TZ": "Asia/Singapore",
                "MONGODB_URI": MONGODB_URI,
                "MONGODB_DB_NAME": MONGODB_DB_NAME,
                "UPSTASH_REDIS_REST_URL": UPSTASH_REDIS_REST_URL,
                "UPSTASH_REDIS_REST_TOKEN": UPSTASH_REDIS_REST_TOKEN,
            }
        ),
        handler=handler,
        runtime=RUNTIME,
        memory_size=MEMORY_SIZE,
        timeout=TIMEOUT,
        layers=[package_layer.arn],
    )


def create_asset_archive(update_file):
    base_files = ["db.py", "download_file.py", "updater.py"]
    files = {
        "config": pulumi.FileArchive("config"),
        "utils": pulumi.FileArchive("utils"),
        **{file: pulumi.FileAsset(file) for file in base_files if os.path.exists(file)},
        f"{update_file}.py": pulumi.FileAsset(f"{update_file}.py"),
    }
    return pulumi.AssetArchive(files)


update_cars_function = create_lambda_function(
    "cars",
    "update_cars.handler",
    code=create_asset_archive("update_cars"),
)

update_coe_function = create_lambda_function(
    "coe",
    "update_coe.handler",
    code=create_asset_archive("update_coe"),
)


def create_event_rule(name, scheduled_expression, target_lambda_function):
    rule = aws.cloudwatch.EventRule(
        f"{PROJECT_NAME}-{name}-rule", schedule_expression=scheduled_expression
    )

    aws.cloudwatch.EventTarget(
        f"{PROJECT_NAME}-{name}-target",
        rule=rule.name,
        arn=target_lambda_function.arn,
    )

    aws.lambda_.Permission(
        f"{PROJECT_NAME}-{name}-permission",
        action="lambda:InvokeFunction",
        function=target_lambda_function.name,
        principal="events.amazonaws.com",
        source_arn=rule.arn,
    )

    return rule


cron_schedulers = {
    "cars": {"cron": "cron(0/60 0-10 ? * MON-FRI *)", "function": update_cars_function},
    "coe": {"cron": "cron(0/60 0-10 ? * MON-FRI *)", "function": update_coe_function},
    "coe-1st-bidding": {
        "cron": "cron(0/10 8-10 ? * 4#1 *)",
        "function": update_coe_function,
    },
    "coe-2nd-bidding": {
        "cron": "cron(0/10 8-10 ? * 4#3 *)",
        "function": update_coe_function,
    },
}

for name, scheduler in cron_schedulers.items():
    create_event_rule(name, scheduler["cron"], scheduler["function"])

pulumi.export("update_cars_function", update_cars_function.name)
pulumi.export("update_coe_function", update_coe_function.name)
pulumi.export("packages_layer", package_layer.source_code_size)
