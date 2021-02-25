#!/usr/bin/env python3

from aws_cdk import core

from serverless_todo_stack.serverless_todo_stack import TodoStack


app = core.App()
TodoStack(app, "serverless-todo")

app.synth()
