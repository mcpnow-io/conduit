---
mode: agent
---
# Tips: How to run unittests
To run unittests, you need to install Docker on your environment to run [Phorge](https://we.phorge.it/) in the background.
```bash
cd tests
docker build -t phorge_debug .
docker run -d --rm -p 8080:80 --name phorge_debug phorge_debug
```
The `phorge_debug` container will automatically initialize the Phorge environment, enable username/password authorization, and generate a User API key for the default `admin` user. By default, you can access your locally running Phorge instance at http://127.0.0.1:8080/.

If you want to access Phorge from your browser, modify the `Dockerfile` to append the `--password` argument when calling `./bin/init_phabricator`.

You can retrieve the User API Key by entering the following command:
```bash
docker exec phorge_debug /usr/local/bin/get-api-token.sh
```
After that, you can run unittest locally by this command:
```bash
PHABRICATOR_TOKEN=<api-token> PHABRICATOR_URL=http://127.0.0.1:8080/api/ pytest
```
