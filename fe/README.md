# Frontend

## Setup

- for usage only
  - `dist` directory is included in the repo
  - modify index.html such that "src" or "href" tags start with `./` instead of `/` (assuming no directory changes)
  - open index.html
  - notably, the backend API still has to be running
- for development
  - download and install [NodeJS](https://nodejs.org/en), preferably through [nvm](https://github.com/nvm-sh/nvm)
  - install dependenencides
  ```shell
  # /your/local/path/fe
  npm install
  ```
  - run the dev server
  ```shell
  # /your/local/path/fe
  npm run dev
  ```
