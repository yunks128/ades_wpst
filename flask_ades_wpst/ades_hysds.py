"""
ADES WPS-T layer for HySDS
Author: Namrata Malarout
"""
import os
from subprocess import run
import json
from flask_ades_wpst.ades_abc import ADES_ABC
# from otello import Mozart


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
        # m = Mozart()


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
        """
        algo_instance = m.get_job_type(proc_id)
        algo_instance.initialize() #retrieving the Job wiring and parameters
        algo_instance.set_input_params(job_spec.get("inputs")
        hysds_job = algo_instance.submit_job()
        """

        # Stub for prototype
        print("Submitting job of type {}\n Parameters: {}").format(job_spec.get("process"), job_spec.get("inputs"))

            
        return {'job_id': job_id, 'status': status, 'error': error}

    def dismiss_job(self, job_spec):
        # We can only dismiss jobs that were last in accepted or running state.
        status = self.get_job(job_spec)["status"]
        print("dismiss_job got start status: ", status)
        if status in ("running", "accepted"):
            # Delete the job from the queue if it is still queued or running.
            # The "-x" option enables deleting jobs and their history in any 
            # of the following states: running, queued, suspended, held, 
            # finished, or moved.
            pbs_job_id = job_spec["backend_info"]["pbs_job_id"]
            qdel_resp = run([self._pbs_qdel_cmd, "-x", "-W", "force", pbs_job_id],
                            capture_output=True, text=True)
            print("Deleting jobID:", job_spec["jobID"])
            print("Deleting pbs_job_id:", pbs_job_id)
            print("qdel_resp:", qdel_resp)
       
        # Remove the job's work directory.
        job_id = job_spec["jobID"]
        self._remove_workdir(job_id)
            
        return job_spec

    def get_job(self, job_spec):
        # Get PBS job status.
        # 
        job_id = job_spec["jobID"]
        work_dir = self._construct_workdir(job_id)
        pbs_job_id = job_spec["backend_info"]["pbs_job_id"]
        qstat_resp = run([self._pbs_qstat_cmd, "-x", "-F", "json", pbs_job_id],
                         capture_output=True, text=True)
        print("qstat_resp:", qstat_resp)
        job_spec["status"] = \
            self._get_status_from_qstat_stdout(work_dir, qstat_resp.stdout)
        
        return job_spec

    def get_job_results(self, job_spec):
        res =  {"links": [{"href": "https://mypath",
                           "rel": "result",
                           "type": "application/json",
                           "title": "mytitle"}]}
        return {**job_spec, **res}
