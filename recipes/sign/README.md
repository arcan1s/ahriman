# Sign

This example uses generated key. It can be generated as:

```shell
gpg --full-generate-key
gpg --export-secret-keys -a <...> > repository-sign.gpg
```

1. Setup repository named `ahriman-demo` with architecture `x86_64`.
2. Sing repository database with the distributed key.
3. Start service in daemon mode with periodic (once per day) repository update.
4. Repository is available at `http://localhost:8080/repo`.
