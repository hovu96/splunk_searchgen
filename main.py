import splunklib
import splunklib.client
import splunklib.results
import logging
import sys
import time
import datetime
import os

root = logging.getLogger()
root.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)


def main():
    splunk = splunklib.client.Service(
        port=8089,
        scheme="https",
        host=os.getenv("SEARCH_GEN_HOST"),
        username=os.getenv("SEARCH_GEN_USER"),
        password=os.getenv("SEARCH_GEN_PASSWORD"),
    )
    splunk.login()
    jobs = {}
    start_time = time.time()
    searches_executed = 0
    target_searches_per_second = 2.0
    spawn_counter = int(target_searches_per_second)

    while True:
        for _ in range(spawn_counter):
            searches_executed += 1
            job = splunk.search(
                "| search earliest=-1m latest=now index=_internal | stats count by sourcetype")
            jobs[job.name] = job
        logging.info("currently running %s searches" % len(jobs))
        for job_name in list(jobs.keys()):
            job = jobs[job_name]
            if job.is_ready():
                # results = job.results()
                result_count = 0
                # for result in splunklib.results.ResultsReader(results):
                #    logging.debug("result: %s" % result)
                #    result_count += 1
                # logging.info("job %s finished with %s results",
                # job_name, result_count)
                del jobs[job_name]
        time.sleep(1)
        seconds_elapsed = time.time()-start_time
        logging.info("seconds_elapsed: %s" % seconds_elapsed)
        searches_per_second_so_far = searches_executed / seconds_elapsed
        logging.info("searches_per_second_so_far: %s" %
                     searches_per_second_so_far)
        if searches_per_second_so_far > target_searches_per_second:
            if spawn_counter > 0:
                spawn_counter -= 1
                logging.info("decreased spawn counter to %s" % spawn_counter)
        else:
            spawn_counter += 1
            logging.info("increased spawn counter to %s" % spawn_counter)


if __name__ == "__main__":
    main()