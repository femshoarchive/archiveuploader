# FemSho Archive Uploader
Simple Discord bot for uploading images to [FemSho Archive](https://femshoarchive.github.io)

# Instalation
## Manual (development)
Copy `.env.example` to `.env` and fill it out.

## Docker Compose
```yaml
services:
    uploader:
        image: ghcr.io/femshoarchive/archiveuploader:main
        restart: unless-stopped
        environment:
            GIT_URL: <Optional, URL to the Git repository>
            GIT_USER: <Git user>
            GIT_PASS: <Git password>
            DISCORD_TOKEN: <Discord bot>
            DISCORD_ALLOWED: <Comma-separated list of allowed user IDs>
```
