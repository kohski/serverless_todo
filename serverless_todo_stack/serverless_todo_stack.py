from aws_cdk import (
    aws_cognito as cognito,
    aws_dynamodb as dynamodb,
    aws_lambda as lambda_,
    aws_logs as logs,
    aws_iam as iam,
    aws_apigateway as apigw,
    core
)


class TodoStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # -----------------------------------
        #           Cognito User Pool
        # -----------------------------------
        userpool = cognito.UserPool(
            self,
            "ServerlessTodoUserPool",
            user_pool_name="ServerlessTodoUserPool",
            sign_in_aliases=cognito.SignInAliases(
                username=True,
                email=True
            ),
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
        userpool.add_client(
            "UserPoolClient",
            auth_flows=cognito.AuthFlow(
                admin_user_password=True
            )
        )

        # -----------------------------------
        #           dynamodb
        # -----------------------------------
        dynamodbTable = dynamodb.Table(self, "TaskTable",
                                       partition_key=dynamodb.Attribute(
                                           name="id", type=dynamodb.AttributeType.STRING),
                                       sort_key=dynamodb.Attribute(
                                           name="meta", type=dynamodb.AttributeType.STRING),
                                       billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
                                       point_in_time_recovery=True,
                                       server_side_encryption=True
                                       )
        dynamodbTable.add_global_secondary_index(
            partition_key=dynamodb.Attribute(
                name="meta", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(
                name="id", type=dynamodb.AttributeType.STRING),
            index_name="meta-id-index"
        )
        dynamodbTable.add_global_secondary_index(
            partition_key=dynamodb.Attribute(
                name="owner", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(
                name="meta", type=dynamodb.AttributeType.STRING),
            index_name="owner-meta-index"
        )

        # -----------------------------------
        #             apigateway
        # -----------------------------------
        api_policy = iam.PolicyDocument(statements=iam.PolicyStatement(
            actions=[
                "lambda:InvokeFunction"
            ],
        ).add_resources("arn:aws:lambda:{}:{}:function:*".format(self.region, self.account)))

        api = apigw.RestApi(self, 'API',
                            deploy_options=apigw.StageOptions(
                                metrics_enabled=True
                            ),
                            policy=api_policy,
                            rest_api_name="Serverless TODO API",
                            endpoint_types=[apigw.EndpointType.REGIONAL],
                            default_cors_preflight_options=apigw.CorsOptions(
                                allow_origins=apigw.Cors.ALL_ORIGINS,  # TODO: Temporary for development
                                allow_headers=["Content-Type", "X-Amz-Date", "Authorization", "X-Api-Key",
                                               "X-Amz-Security-Token", "X-Tracing-Id", "x-jeffy-correlation-id", "x-amzn-trace-id"],
                                allow_methods=apigw.Cors.ALL_METHODS,
                                allow_credentials=True
                            )
                            )

        cognito_authorizer = apigw.CognitoUserPoolsAuthorizer(
            self,
            "CognitoAuthorizer",
            cognito_user_pools=[
                userpool
            ],
            authorizer_name='todo_cognito_authorizer',
            identity_source='method.request.header.Authorization',
            results_cache_ttl=core.Duration.minutes(60)
        )

        api_role = iam.Role(
            self, "ApiRole",
            assumed_by=iam.ServicePrincipal(
                service="apigateway.amazonaws.com"
            )
        )
        api_statement = iam.PolicyStatement(
            actions=[
                "lambda:InvokeFunction"
            ],
            resources=[
                "arn:aws:lambda:{}:{}:function:*".format(
                    self.region, self.account)
            ]
        )
        api_role.add_to_policy(api_statement)

        # -----------------------------------
        #      lambda common configure
        # -----------------------------------
        env = {
            "TABLE_NAME": dynamodbTable.table_name
        }

        # -----------------------------------
        #           get handler
        # -----------------------------------
        get_resource_base_name = "getTaskFunction"
        get_task_func = lambda_.Function(self, get_resource_base_name,
                                         code=lambda_.Code.from_asset('function/src/task',
                                                                      bundling=core.BundlingOptions(
                                                                          image=lambda_.Runtime.PYTHON_3_8.bundling_docker_image,
                                                                          command=[
                                                                              'bash', '-c', 'pip install -r requirements.txt -t /asset-output && cp -a . /asset-output'],
                                                                      )),
                                         handler="get.lambda_handler",
                                         runtime=lambda_.Runtime.PYTHON_3_8,
                                         environment=env,
                                         tracing=lambda_.Tracing.ACTIVE,
                                         timeout=core.Duration.seconds(
                                             29),
                                         memory_size=512
                                         )

        get_task_func.add_to_role_policy(statement=iam.PolicyStatement(
            actions=['dynamodb:*'], resources=[dynamodbTable.table_arn, dynamodbTable.table_arn + '/*']))
        logs.LogGroup(self, get_resource_base_name + 'LogGroup',
                      log_group_name='/aws/lambda/' + get_task_func.function_name,
                      retention=logs.RetentionDays.TWO_WEEKS
                      )

        task_path = api.root.add_resource("task")
        task_id_path = task_path.add_resource("{task_id}")
        get_task_integration = apigw.LambdaIntegration(
            get_task_func,
            credentials_role=api_role
        )
        task_id_path.add_method(
            "GET", integration=get_task_integration,
            authorization_type=apigw.AuthorizationType.COGNITO,
            authorizer=cognito_authorizer,
        )

        # -----------------------------------
        #           create handler
        # -----------------------------------
        create_resource_base_name = "craeteTaskFunction"
        create_task_func = lambda_.Function(self, create_resource_base_name,
                                            code=lambda_.Code.from_asset('function/src/task',
                                                                         bundling=core.BundlingOptions(
                                                                             image=lambda_.Runtime.PYTHON_3_8.bundling_docker_image,
                                                                             command=[
                                                                                 'bash', '-c', 'pip install -r requirements.txt -t /asset-output && cp -a . /asset-output'],
                                                                         )),
                                            handler="create.lambda_handler",
                                            runtime=lambda_.Runtime.PYTHON_3_8,
                                            environment=env,
                                            tracing=lambda_.Tracing.ACTIVE,
                                            timeout=core.Duration.seconds(
                                                29),
                                            memory_size=512
                                            )

        create_task_func.add_to_role_policy(statement=iam.PolicyStatement(
            actions=['dynamodb:*'], resources=[dynamodbTable.table_arn, dynamodbTable.table_arn + '/*']))
        logs.LogGroup(self, create_resource_base_name + 'LogGroup',
                      log_group_name='/aws/lambda/' + create_task_func.function_name,
                      retention=logs.RetentionDays.TWO_WEEKS
                      )

        create_task_integration = apigw.LambdaIntegration(
            create_task_func,
            credentials_role=api_role
        )
        task_path.add_method(
            "POST", integration=create_task_integration,
            authorization_type=apigw.AuthorizationType.COGNITO,
            authorizer=cognito_authorizer,
        )
