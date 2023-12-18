# Distributed manual

1. Create user `demo` with password from `AHRIMAN_PASSWORD` environment variable.
2. Setup repository named `ahriman-demo` with architecture `x86_64`.
3. Start web server at port `8080`.
4. Start service in daemon mode with periodic (once per day) repository update.
5. All updates from worker daemon instance are uploaded to the web service.
6. Repository is available at `http://localhost:8080/repo`.
