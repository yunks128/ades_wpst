from abc import ABCMeta, abstractmethod
from utils.datatypes import Job, JobStatus
import boto3

class JobPublisher(metaclass=ABCMeta):

    @abstractmethod
    def publish_job_change(self, job: Job, status: JobStatus):
        raise NotImplementedError()

class SnsJobPublisher(JobPublisher):
    def __init__(self, topic_name: str):
        self.topic_name = topic_name
        self.sts_client = boto3.client('sts', region_name='us-west-2')
        self.topic_arn = f"arn:aws:sns:{self.sts_client.meta.region_name}:{self.sts_client.get_caller_identity()['Account']}:{self.topic_name}"

    def publish_job_change(self, job: Job):
        client = boto3.client('sns', region_name='us-west-2')
        client.publish(
            TopicArn=self.topic_arn,
            Message=job.json(),
            MessageGroupId="jobstatus"
        )
