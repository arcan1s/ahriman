# OAuth

1. Create user from `AHRIMAN_OAUTH_USER` environment variable (same as GitHub user).
2. Configure OAuth to use GitHub provider with client ID and secret specified in variables `AHRIMAN_OAUTH_CLIENT_ID` and `AHRIMAN_OAUTH_CLIENT_SECRET` variables respectively.   
3. Setup repository named `ahriman-demo` with architecture `x86_64`.
4. Start web server at port `8080`.
5. Repository is available at `http://localhost:8080/repo`.

Before you start, you need to create an application. It can be done by:

1. Go to `https://github.com/settings/applications/new`
2. Set application name and its homepage.
3. Set callback url to `http://localhost:8080/api/v1/login`
4. Copy Client ID.
5. Generate new client secret and copy it.
