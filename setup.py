import setuptools


with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="serverless_todo_stack",
    version="0.0.1",

    description="An empty CDK Python app",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="author",

    package_dir={"": "serverless_todo_stack"},
    packages=setuptools.find_packages(where="serverless_todo_stack"),

    install_requires=[
        "aws-cdk.core==1.88.0",
        "aws-cdk.aws_cognito==1.88.0",
        "aws-cdk.aws_dynamodb==1.88.0",
        "aws-cdk.aws_logs==1.88.0",
        "aws-cdk.aws_codedeploy==1.88.0",
        "aws-cdk.aws_iam==1.88.0",
        "aws-cdk.aws_apigateway==1.88.0",
        "aws-cdk.aws_route53==1.88.0",
        "aws-cdk.aws_certificatemanager==1.88.0"
    ],

    python_requires=">=3.6",

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",

        "License :: OSI Approved :: Apache Software License",

        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",

        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",

        "Typing :: Typed",
    ],
)
