# i686

This example uses hybrid setup from FAQ, because archlinux32 has outdated devtools package. So it distributes custom `makepkg.conf` and `pacman.conf` (which are copied from archlinux32 package) and builds custom image with archlinux32 keyring.

1. Create user `demo` with password from `AHRIMAN_PASSWORD` environment variable.
2. Build image from distributed `Dockerfile`.
3. Setup repository named `ahriman-demo` with architecture `i686`.
4. Start web server at port `8080`.
5. Repository is available at `http://localhost:8080/repo`.
