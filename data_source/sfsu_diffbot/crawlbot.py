"""
File:         crawlbot.py
Package:      sfsu_diffbot
Author:       Jose Ortiz Costa <jortizco@mail.sfsu.edu>
Date:         09-29-2017
Modified:     09-29-2017
Description:  Represents the response from a crawlbot extraction api
"""
class CrawlBot(object):
    """
    Class containing usefull crawlbot extraction api properties
    """
    def __init__(self, response):
        self._response = response


    def field(self, key):
        if key in self._response:
             return self._response[key]


    def jobs(self):
        return self.field("jobs")


    def job(self, name_or_index):
        is_index = isinstance(name_or_index, int)
        jobs = self.jobs()
        count = 1
        for job in jobs:
            if is_index:
                if count == name_or_index:
                    return job
                count = count+1
            else:
                if job['name'] == name_or_index:
                    return job

    def type(self, job_name_or_index):
        job = self.job(job_name_or_index)
        return job['type']

    def jobCreationTimeUTC(self, job_name_or_index):
        job = self.job(job_name_or_index)
        return job['jobCreationTimeUTC']

    def jobCompletionTimeUTC(self, job_name_or_index):
        job = self.job(job_name_or_index)
        return job['jobCompletionTimeUTC']

    def jobStatus(self, job_name_or_index):
        job = self.job(job_name_or_index)
        return job['jobStatus']['status']

    def jobStatusMessage(self, job_name_or_index):
        job = self.job(job_name_or_index)
        return job['jobStatus']['message']

    def status(self):
        return self.field('response')

    def to_string(self):
        return self._response





