import aws_cdk as core
import aws_cdk.assertions as assertions

from pipeline_project_stack import PipelineProjectStackV2

# example tests. To run these tests, uncomment this file along with the example
# resource in pipeline_project/pipeline_project_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = PipelineProjectStackV2(app, "pipeline-project")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
