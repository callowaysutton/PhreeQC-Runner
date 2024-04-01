# PhreeqcRunner
PhreeqcRunner lets you queue Phreeqc simulation jobs through an HTTP/HTTPS REST API

# TODO
- [x] Queue job
	- [x] Run multiple jobs in parallel
	- [x] Only run enough jobs per total CPU threads
- [x] Dequeue Job
- [x] List all jobs
	- [x] Save previous results from completed jobs
	- [x] Save log file from failed jobs
	- [x] Gracefully show cancelled/errored out jobs
