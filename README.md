# ebay-scraper

## Development

1. Frontend

- cd frontend
- npm install
- npm start

2. Backend

- cd backend
- python -m venv venv
- source venv/bin/activate
- uvicorn main:app --reload

3. Database

- Default username 'postgres'
- Adminer: a db management tool with UI

## Docker

- `docker-compose.yml` file that defines two services: frontend and backend.
- The frontend service is for React application and the backend service is for FastAPI application.
  When you run the `docker-compose up` command, Docker Compose will read the docker-compose.yml file and start both services in separate containers.
- The two services can interact with each other using their service names as hostnames.
  - For example, from the frontend service, you can send requests to the backend service using the URL http://backend:8000. This is because Docker Compose creates a default network for your application and automatically assigns each service a hostname that matches its service name.
- If any changes are made, `docker-compose down` and then `docker-compose up` again inside directory where yml file is present.

## Modular Backend Structure (future)

```
backend/
    __init__.py
    main.py
    email/
        __init__.py
        sender.py
    scraping/
        __init__.py
        scraper.py
    schedule/
        __init__.py
        runner.py
```

- Note to self : right now running backend locally and the rest on docker for better debugging experience.

### Dev Notes

Use Node Version Manager (NVM) to manage multiple active Node.js versions. It allows you to install and switch between different versions of Node.js as needed. Here's how you can install NVM and use it to install Node.js:

1. **Install NVM** by downloading the install script via cURL:

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.38.0/install.sh | bash
```

2. **Close and reopen your terminal** to start using NVM or run the following to use it immediately:

```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion
```

3. **Verify installation** by checking the version of NVM:

```bash
nvm --version
```

4. **Install Node.js** using NVM:

```bash
nvm install node # "node" is an alias for the latest version
```

5. If you want to install a specific version of Node.js, you can list all available versions and then install a specific one:

```bash
nvm ls-remote # List all versions available on the server
nvm install v16.14.0 # Install a specific version
```

6. **Switch between installed Node.js versions**:

```bash
nvm use v16.14.0 # Use a specific version
nvm use node # Use the latest version
nvm use --lts # Use the latest LTS version
```

Remember, every new shell session will use the default Node.js version you've set with `nvm alias default`. If you want to change the default version, use `nvm alias default <version>`.

In a typical CI/CD (Continuous Integration/Continuous Deployment) setup, you would use both branches, but for different purposes:

1. **Develop Branch**: This is where active development happens. Developers create feature branches off of this branch, and once their work is complete and tested, they merge their feature branches back into the develop branch. The CI process runs on every push to the develop branch (and possibly on feature branches as well), building the project and running any tests to ensure that new changes haven't broken anything.

2. **Main Branch**: This branch represents the stable version of your project and is what gets deployed to production. When you're ready to make a new release, you merge the develop branch into main. The CD process then deploys the main branch to production.

After publishing a release (i.e., merging develop into main and deploying it), you don't necessarily need to merge main back into develop, because all the changes in main originated from develop. However, if you made any hotfixes directly on the main branch, those would need to be merged back into develop.

Remember, this is just a typical setup and might not fit every project's needs. The key is to find a workflow that works best for your team and your project.

Try to do this once more,
https://www.patrickkoch.dev/posts/post_20/
https://learn.microsoft.com/en-us/azure/container-instances/container-instances-multi-container-yaml

else do the vm and then install docker and then docker compose.

or

azure kubernetes cluster/ service

Deployment
i am using the azure portal to deploy.
I created a VM and have the username - mushtaq96
I am using cent OS and it does not have docker capabilities.

Yes, you need to have Docker Compose installed on your Azure Virtual Machine to use it. Docker Compose is a tool for defining and running multi-container Docker applications. With Compose, you use a YAML file to configure your application's services, which allows you to manage your application as a single entity rather than dealing with individual containers.

If Docker Compose is not already installed on your VM, you can install it by following these steps:

1. **Download the Docker Compose binary**:

```bash
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```

2. **Apply executable permissions to the binary**:

```bash
sudo chmod +x /usr/local/bin/docker-compose
```

3. **Verify the installation**:

```bash
docker-compose --version
```

Whether you should use Docker or Podman depends on your specific needs and constraints. Here are some points to consider:

**Docker**:

- Docker is widely used and has a large community, which means it's easy to find help and resources online.
- Docker uses a client-server model. The Docker client communicates with the Docker daemon, which does the heavy lifting of building, running, and managing Docker containers.
- Docker Compose is a tool for defining and running multi-container Docker applications. It uses a YAML file to configure your application's services.

**Podman**:

- Podman is a newer, daemonless container engine developed by Red Hat.
- It's designed to be a drop-in replacement for Docker, offering similar functionality but without a daemon, making it more secure and lightweight.
- Podman is the default on Red Hat Enterprise Linux (RHEL), Fedora, and CentOS Stream.
- Podman has rootless support, which allows you to run containers as a non-root user.
- If you want to use Docker Compose with Podman, you can use `podman-compose`, a script that translates Docker Compose files to Podman-compatible files.

To monitor your Podman deployment on CentOS, you can use the following commands:

1. **List running containers**: Use the `podman ps` command to list all running containers¹³.

2. **Inspect a container**: Use the `podman inspect <container_id>` command to display detailed information about a container¹³.

3. **View container logs**: Use the `podman logs <container_id>` command to view the logs of a container¹³.

4. **Check container stats**: Use the `podman stats` command to display a live stream of container resource usage statistics¹³.

To access the ports from a browser, you can simply navigate to `http://<your_server_ip>:<port_number>`. Replace `<your_server_ip>` with the IP address of your CentOS server and `<port_number>` with the port number you want to access⁸.

For Adminer GUI ports, if you have specified a port in your `docker-compose.yml` file for the Adminer service (for example, `8080:8080`), you can access Adminer at `http://<your_server_ip>:8080`.

Here are some important Podman commands for terminal use¹³:

- **podman run**: Run a command in a new container.
- **podman ps**: List containers.
- **podman stop**: Stop one or more containers.
- **podman rm**: Remove one or more containers.
- **podman images**: List images in local storage.
- **podman pull**: Pull an image from a registry.
- **podman push**: Push an image to a specified destination.

Remember, these are general suggestions and might need adjustments based on your specific setup and requirements.

Let me know if you need more help! 😊

Source: Conversation with Bing, 21/10/2023
(1) Commands — Podman documentation. https://docs.podman.io/en/latest/Commands.html.
(2) Getting Started with Podman | Podman. https://podman.io/docs.
(3) Podman Tutorial: How to Work with Images, Containers and Pods - phoenixNAP. https://phoenixnap.com/kb/podman-tutorial.
(4) Deploy a Pod on CentOS with Podman | Podman. https://podman.io/blogs/2020/02/06/deploy-pod-on-centos.
(5) How To Install and use Podman on CentOS 8 / RHEL 8. https://www.osradar.com/how-to-install-and-use-podman-on-centos-8-rhel-8/.
(6) Deploy a Pod on CentOS with Podman | Podman. https://podman.io/blogs/2020/02/06/new.
(7) How To Install Podman on Centos 7 - Step by Step - OrcaCore. https://orcacore.com/install-podman-centos-7/.
(8) networking - Can't expose port with podman - Stack Overflow. https://stackoverflow.com/questions/69859279/cant-expose-port-with-podman.
(9) networking - How to: Podman rootless expose containers ports to the .... https://stackoverflow.com/questions/75427655/how-to-podman-rootless-expose-containers-ports-to-the-outside-and-see-real-clie.
(10) podman - Accessing host from inside container - Stack Overflow. https://stackoverflow.com/questions/58678983/accessing-host-from-inside-container.
(11) Is it possible to list which ports in a Podman pod is bound to which .... https://stackoverflow.com/questions/67885988/is-it-possible-to-list-which-ports-in-a-podman-pod-is-bound-to-which-container.
(12) Podman: add ports to expose to running pod - Stack Overflow. https://stackoverflow.com/questions/59920413/podman-add-ports-to-expose-to-running-pod.
(13) Podman. https://podman.io/get-started.
(14) Podman Cheat Sheet | Red Hat Developer. https://developers.redhat.com/cheat-sheets/podman-cheat-sheet.
(15) Podman Cheat Sheet - GitHub: Let’s build from here. https://github.com/redhat-developer/cheat-sheets/blob/master/podman.adoc.
(16) undefined. https://podman.io/getting-started/network.

Log into the VM using local shell.
ssh -i ebay-scraper_key.pem mushtaq96@98.67.160.228

python -m pytest backend/tests/test_db.py

### several potential improvements we could discuss:

Database Operations:
The current implementation uses separate database connections for each operation
We could optimize this by using a single connection per request
This would improve performance and reduce database load
Error Handling:
While you have basic error handling, we could add more specific error types
This would help with debugging and user feedback
We could also add logging for better monitoring
Scraping Logic:
The current implementation fetches all listings at once
We could add pagination support
This would be more efficient for large result sets
Email Notifications:
The email template is static
We could make it more dynamic
Add support for different notification types
