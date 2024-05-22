import json

import pulumi
import pulumi_aws as aws

project_name = "lta-datasets-updater"

role = aws.iam.Role(
    f"{project_name}-role",
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
    f"{project_name}-policy",
    role=role.name,
    policy_arn=aws.iam.ManagedPolicy.AWS_LAMBDA_BASIC_EXECUTION_ROLE,
)

# lta_datasets_updater_bucket = aws.s3.Bucket(f"{project_name}-bucket")

# packages = aws.s3.BucketObjectv2(
#     f"{project_name}-packages",
#     bucket=lta_datasets_updater_bucket.id,
#     source=pulumi.FileAsset("package.zip"),
# )

packages_layer = aws.lambda_.LayerVersion(
    f"{project_name}-layer",
    layer_name=f"{project_name}-layer",
    code=pulumi.FileArchive("package.zip"),
    # s3_bucket=lta_datasets_updater_bucket.id,
    # s3_key=packages.key,
    compatible_runtimes=[aws.lambda_.Runtime.PYTHON3D12],
)

update_cars_function = aws.lambda_.Function(
    f"{project_name}-cars-function",
    code=pulumi.AssetArchive(
        {
            "utils": pulumi.FileArchive("utils"),
            "download_file.py": pulumi.FileAsset("download_file.py"),
            "update_cars.py": pulumi.FileAsset("update_cars.py"),
            "updater.py": pulumi.FileAsset("updater.py"),
        }
    ),
    role=role.arn,
    environment=aws.lambda_.FunctionEnvironmentArgs(
        variables={
            "TZ": "Asia/Singapore",
            "MONGODB_URI": pulumi.Config().require_secret("MONGODB_URI"),
            "MONGODB_DB_NAME": pulumi.Config().require("MONGODB_DB_NAME"),
        }
    ),
    handler="update_cars.handler",
    runtime=aws.lambda_.Runtime.PYTHON3D12,
    memory_size=1024,
    timeout=15,
    layers=[packages_layer.arn],
)

update_coe_function = aws.lambda_.Function(
    f"{project_name}-coe-function",
    code=pulumi.AssetArchive(
        {
            "utils": pulumi.FileArchive("utils"),
            "download_file.py": pulumi.FileAsset("download_file.py"),
            "update_coe.py": pulumi.FileAsset("update_coe.py"),
            "updater.py": pulumi.FileAsset("updater.py"),
        }
    ),
    role=role.arn,
    environment=aws.lambda_.FunctionEnvironmentArgs(
        variables={
            "TZ": "Asia/Singapore",
            "MONGODB_URI": pulumi.Config().require_secret("MONGODB_URI"),
            "MONGODB_DB_NAME": pulumi.Config().require("MONGODB_DB_NAME"),
        }
    ),
    handler="update_coe.handler",
    runtime=aws.lambda_.Runtime.PYTHON3D12,
    memory_size=1024,
    timeout=15,
    layers=[packages_layer.arn],
)

update_cars_rule = aws.cloudwatch.EventRule(
    f"{project_name}-cars-rule",
    schedule_expression="cron(0/60 0-10 ? * MON-FRI *)",
)

update_coe_rule = aws.cloudwatch.EventRule(
    f"{project_name}-coe-rule",
    schedule_expression="cron(0/60 0-10 ? * MON-FRI *)",
)

update_coe_first_bidding_rule = aws.cloudwatch.EventRule(
    f"{project_name}-coe-first-bidding-rule",
    schedule_expression="cron(0/10 8-10 ? * 4#1 *)",
)

update_coe_second_bidding_rule = aws.cloudwatch.EventRule(
    f"{project_name}-coe-second-bidding-rule",
    schedule_expression="cron(0/10 8-10 ? * 4#3 *)",
)

aws.lambda_.Permission(
    f"{project_name}-permission",
    action="lambda:InvokeFunction",
    function=update_cars_function.name,
    principal="events.amazonaws.com",
    source_arn=update_cars_rule.arn,
)

aws.lambda_.Permission(
    f"{project_name}-coe-permission",
    action="lambda:InvokeFunction",
    function=update_coe_function.name,
    principal="events.amazonaws.com",
    source_arn=update_coe_rule.arn,
)

update_cars_target = aws.cloudwatch.EventTarget(
    f"{project_name}-cars-target",
    rule=update_cars_rule.name,
    arn=update_cars_function.arn,
)

pulumi.export("update_cars_function", update_cars_function.name)
pulumi.export("update_cars_rule", update_cars_rule.schedule_expression)
update_coe_target = aws.cloudwatch.EventTarget(
    f"{project_name}-coe-target",
    rule=update_coe_rule.name,
    arn=update_coe_function.arn,
)

update_coe_first_bidding_target = aws.cloudwatch.EventTarget(
    f"{project_name}-coe-first-bidding-target",
    rule=update_coe_first_bidding_rule.name,
    arn=update_coe_function.arn,
)

update_coe_second_bidding_target = aws.cloudwatch.EventTarget(
    f"{project_name}-coe-second-bidding-target",
    rule=update_coe_second_bidding_rule.name,
    arn=update_coe_function.arn,
)

pulumi.export("packages_layer", packages_layer.source_code_size)
