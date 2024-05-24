import json
import os
import tempfile

import pulumi
import pulumi_aws as aws
from dotenv import load_dotenv

import create_package_zip

load_dotenv()

PROJECT_NAME = f"{pulumi.get_stack()}-{pulumi.get_project()}"

MEMORY_SIZE = 1024
TIMEOUT = 15
RUNTIME = aws.lambda_.Runtime.PYTHON3D12
TIMEZONE = "Asia/Singapore"

config = pulumi.Config()
MONGODB_URI = os.environ.get("MONGODB_URI")
MONGODB_DB_NAME = os.environ.get("MONGODB_DB_NAME")

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
zip_file = 'python.zip'

create_package_zip.main(temp_dir, zip_file)

package_layer = aws.lambda_.LayerVersion(f'{PROJECT_NAME}-layer',
                                         layer_name=f"{PROJECT_NAME}-layer",
                                         code=pulumi.AssetArchive({".": pulumi.FileArchive(f"{temp_dir}/{zip_file}")}),
                                         compatible_runtimes=[aws.lambda_.Runtime.PYTHON3D12]
                                         )


def create_lambda_function(name, handler, code):
    return aws.lambda_.Function(f"{PROJECT_NAME}-{name}-function",
                                code=code,
                                role=role.arn,
                                environment=aws.lambda_.FunctionEnvironmentArgs(
                                    variables={
                                        "TZ": "Asia/Singapore",
                                        "MONGODB_URI": MONGODB_URI,
                                        "MONGODB_DB_NAME": MONGODB_DB_NAME
                                    }
                                ), handler=handler, runtime=RUNTIME, memory_size=MEMORY_SIZE, timeout=TIMEOUT,
                                layers=[package_layer.arn])


def create_asset_archive(update_file):
    # TODO: Need a more recursive way to handle these file dependencies
    files = {"utils": pulumi.FileArchive("utils"),
             "db.py": pulumi.FileAsset("db.py"),
             "download_file.py": pulumi.FileAsset("download_file.py"),
             "updater.py": pulumi.FileAsset("updater.py"),
             f"{update_file}.py": pulumi.FileAsset(f"{update_file}.py")}
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
    rule = aws.cloudwatch.EventRule(f"{PROJECT_NAME}-{name}-rule", schedule_expression=scheduled_expression)

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
    "coe-1st-bidding": {"cron": "cron(0/10 8-10 ? * 4#1 *)", "function": update_coe_function},
    "coe-2nd-bidding": {"cron": "cron(0/10 8-10 ? * 4#3 *)", "function": update_coe_function},
}

for name, scheduler in cron_schedulers.items():
    create_event_rule(name, scheduler['cron'], scheduler['function'])

pulumi.export("update_cars_function", update_cars_function.name)
pulumi.export("update_coe_function", update_coe_function.name)
pulumi.export("packages_layer", package_layer.source_code_size)
