"""
ADES WPS-T layer for HySDS
Author: Namrata Malarout
"""
import os
from subprocess import run
import json
from flask_ades_wpst.ades_abc import ADES_ABC
import otello
from otello import Mozart
import time

hysds_to_ogc_status = {
    "job-started" : "running",
    "job-queued" : "accepted",
    "job-failed" : "failed",
    "job-completed" : "succeeded"
    
    }

class ADES_HYSDS(ADES_ABC):

    def __init__(self, hysds_version='v4.0', mozart_url='https://[MOZART_IP]/mozart/api/v0.2',
                 default_queue='test-job_worker-large', lw_queue='system-jobs-queue',
                 lw_version='v0.0.5', grq_url='http://[GRQ_IP]/api/v0.1',
                 s3_code_bucket='s3://[S3_BUCKET_NAME]'):
        self._hysds_version = hysds_version
        self._mozart_url = mozart_url
        self._default_queue = default_queue
        self._lw_queue = lw_queue
        self._lw_version = lw_version
        self._grq_url = grq_url
        self.s3_code_bucket = s3_code_bucket
        m = Mozart()


    def _generate_job_id_stub(self, qsub_stdout):
        return '.'.join(qsub_stdout.strip().split('.')[:2])


    def _pbs_job_state_to_status_str(self, work_dir, job_state):
        pbs_job_state_to_status = {
            "Q": "accepted",
            "R": "running",
            "E": "running",
        }
        if job_state in pbs_job_state_to_status:
            status =  pbs_job_state_to_status[job_state]
        elif job_state == "F":
            # Job finished; need to check cwl-runner exit-code to determine
            # if the job succeeded or failed.  In the auto-generated, PBS job 
            # submission script, the exit code is saved to a file.
            exit_code_fname = os.path.join(work_dir, self._exit_code_fname)
            try:
                with open(exit_code_fname, "r") as f:
                    d = json.loads(f.read())
                    exit_code = d["exit_code"]
                    if exit_code == 0:
                        status = "successful"
                    else:
                        status = "failed"
            except:
                status = "unknown-not-qref"
        else:
            # Encountered a PBS job state that is not supported.
            status = "unknown-no-exit-code"
        return status

    def get_procs(self):
        """
        Get all job types in HySDS
        :return:
        """
        """
        Otello Implementation
        job_types = m.get_job_types()
        for proc_name in job_types:
        """
        # For prototype,
        m = Mozart()
        job_types = m.get_job_types()
        for proc_name in job_types:
            jt = m.get_job_type(proc_name)
            jt.initialize()
            jt.describe()

    def deploy_proc(self, proc_spec):
        container = proc_spec["executionUnit"][0]["href"]
        local_sif = self._construct_sif_name(container)
        print("local_sif={}".format(local_sif))
        print("Localizing container {} to {}".format(container, local_sif))
        run([self._module_cmd, "bash", "load", "singularity"])
        run([self._singularity_cmd, "pull", local_sif, container])
        return proc_spec

    def undeploy_proc(self, proc_spec):
        container = proc_spec["executionUnit"]
        local_sif = self._construct_sif_name(container)
        print("Removing local SIF {}".format(local_sif))
        os.remove(local_sif)
        return proc_spec

    def exec_job(self, job_spec):
        print(job_spec)
        # Make Otello call to submit job with job type and parameters
        m = otello.Mozart()
        proc_id = job_spec.get("proc_id")
        print(proc_id)
        print(job_spec.get("inputs").get("inputs"))
        job = m.get_job_type(proc_id)
        job.initialize() # retrieving the Job wiring and parameters
        # Create params dictionary
        params = dict()
        if len(job_spec.get("inputs").get("inputs")) != 0:
            for input in job_spec.get("inputs").get("inputs"):
                params[input["id"]] = input["data"]
        job.set_input_params(params=params)
        print("Submitting job of type {}\n Parameters: {}".format(proc_id, params))
        hysds_job = job.submit_job(queue='factotum-job_worker-large', priority=0, tag="test")
        print(f"Submitted job with id {hysds_job.job_id}")
        error = None
        time.sleep(2)
        return {'job_id': hysds_job.job_id, 'status': hysds_job.get_status(), 'error': error}

    def dismiss_job(self, proc_id, job_id):
        # We can only dismiss jobs that were last in accepted or running state.
        # initialize job
        job = otello.Job(job_id=job_id)
        status = job.get_status()
        print("dismiss_job got start status: ", status)
        if status in ("job-started", "job-queued"):
            # if status is started then revoke the job
            if status == "job-started":
                job.revoke()
            elif status == "job-queued":
                # if status is queued then purge (remove) the job
                job.remove()
        else:
            raise Exception(f"Can not dismiss a job in {hysds_to_ogc_status.get(status)}.")
        return

    def get_jobs(self, proc_id):
        jobs_result = list()
        m = otello.Mozart()
        job_set = m.get_jobs()
        print(f"filtering jobs for process {proc_id}")
        # {"jobID": job_id, "status": job_info["status"], "message": "Status of job {}".format(job_id)}
        for job in job_set:
            job_dets = dict()
            job_info = job.get_info()
            if job_info.get("type") == proc_id:
                job_dets["jobID"] = job_info.get("payload_id")
                job_dets["status"] = hysds_to_ogc_status.get(job.get_status())
                job_dets["inputs"] = job_info.get("job").get("params").get("job_specification").get("params")
                jobs_result.append(job_dets)
        return jobs_result

    def get_job(self, job_spec):
        # Get PBS job status.
        # 
        job_id = job_spec["jobID"]
        job = otello.Job(job_id=job_id)
        status = job.get_status()
        job_spec["status"] = hysds_to_ogc_status.get(status)
        print(f"Job status {status}")
        return job_spec

    def get_job_results(self, job_id):
        job = otello.Job(job_id=job_id)
        products = job.get_generated_products()
        print(f"Found products: {products}")
        return products
