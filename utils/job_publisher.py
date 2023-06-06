from abc import ABCMeta, abstractmethod
from utils.datatypes import Job, JobStatus
import boto3


class JobPublisher(metaclass=ABCMeta):
    @abstractmethod
    def publish_job_change(self, job: Job, status: JobStatus):
        raise NotImplementedError()


class SnsJobPublisher(JobPublisher):
    def __init__(self, topic_arn: str):
        self.topic_arn = topic_arn

    def publish_job_change(self, job: Job):
        client = boto3.client("sns", region_name="us-west-2")
        client.publish(
            TopicArn=self.topic_arn, Message=job.json(), MessageGroupId="jobstatus"
        )
