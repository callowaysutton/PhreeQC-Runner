# PhreeqcRunner
PhreeqcRunner lets you queue Phreeqc simulation jobs through an HTTP/HTTPS REST API

# TODO
- [x] Queue job
	- [ ] Run multiple jobs in parallel (Not Necessary yet...)
	- [ ] Only run enough jobs per total CPU threads
- [x] Dequeue Job
- [x] List all jobs
	- [ ] Save previous results from completed jobs
	- [ ] Save log file from failed jobs
	- [x] Gracefully show cancelled/errored out jobs
