from aws_cdk import (
    aws_cognito as cognito,
    core
)


class TodoStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        cognito.UserPool(
            self,
            "ServerlessTodoUserPool",
            user_pool_name="ServerlessTodoUserPool",
            password_policy=cognito.PasswordPolicy(
                min_length=6,
                require_digits=True,
                require_lowercase=True,
                require_symbols=True,
                require_uppercase=True,
                temp_password_validity=core.Duration.days(7)
            ),
            auto_verify=cognito.AutoVerifiedAttrs(
                email=True
            ),
            standard_attributes=cognito.StandardAttributes(
                email=cognito.StandardAttribute(
                    mutable=True,
                    required=True
                ),
                family_name=cognito.StandardAttribute(
                    mutable=True,
                    required=True
                ),
                given_name=cognito.StandardAttribute(
                    mutable=True,
                    required=True
                )
            )
        )
