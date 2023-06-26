from abc import ABCMeta, abstractmethod
from utils.datatypes import Job
import boto3

class JobPublisher(metaclass=ABCMeta):

    @abstractmethod
    def publish_job_change(self, job: Job):
        raise NotImplementedError()

class SnsJobPublisher(JobPublisher):
    def __init__(self, topic_arn: str):
        self.topic_arn = topic_arn
        self.sts_client = boto3.client('sts', region_name='us-west-2')

    def publish_job_change(self, job: Job):
        client = boto3.client('sns', region_name='us-west-2')
        try:
            client.publish(
                TopicArn=self.topic_arn,
                Message=job.json(),
                MessageGroupId=job.id
            )
        except Exception as e:
            print(f"Failed to publish job {job.id} to {self.topic_arn}:\n {e}")
