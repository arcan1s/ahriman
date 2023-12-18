# Distributed

1. Create user `demo` with password from `AHRIMAN_PASSWORD` environment variable.
2. Setup repository named `ahriman-demo` with architecture `x86_64`.
3. Start web server at port `8080`.
4. Start two workers.
5. All updates triggered by the web server will be passed to workers.
6. All updates from worker instances are uploaded to the web service.
7. Repository is available at `http://localhost:8080/repo`.

Note, in this configuration, workers are spawned in replicated mode, thus the backend accesses them in round-robin-like manner.
