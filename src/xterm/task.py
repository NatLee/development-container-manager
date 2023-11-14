import docker
from django_rq import job

@job
def run_image_task(image_name, ports, volumes, environment, name, privileged=False, nvdocker=False):
    client = docker.from_env()
    device_requests = []
    network = client.networks.get('d-gui-network')

    if nvdocker:
        # Define device requests for NVIDIA GPUs
        device_requests += [
            docker.types.DeviceRequest(
                count=-1,  # -1 specifies all available GPUs
                capabilities=[['gpu']],  # This is the equivalent of `--gpus all`
                driver='nvidia'
            )
        ]

    traefik_labels = {
        "traefik.enable": "true",
        f"traefik.http.routers.d-gui-{name}.rule": f"PathPrefix(`/novnc/{name}/`)",
        f"traefik.http.services.d-gui-{name}.loadbalancer.server.port": "6901",
        f"traefik.http.middlewares.d-gui-{name}-strip-prefix.stripprefix.prefixes": f"/novnc/{name}/",
        f"traefik.http.routers.d-gui-{name}.middlewares": f'd-gui-{name}-strip-prefix',
    }

    container = client.containers.run(
        image_name,
        stdin_open=True,
        detach=True,
        tty=True,
        ports=ports,
        volumes=volumes,
        environment=environment,
        name=name,
        privileged=privileged,
        device_requests=device_requests,
        network=network.id,  # Attach the container to the network
        labels=traefik_labels
    )

    image_name = "none"
    if container.image.tags:
        image_name = container.image.tags[0]
    container_name = container.attrs['Name'][1:]
    msg = f"Container {container_name} ({image_name}) has been created"
    return msg

@job
def run_container_task(id):
    client = docker.from_env()
    container = client.containers.get(id)
    container.start()
    container_name = container.name
    msg = f"Container {container_name} has been started"
    return msg

@job
def stop_container_task(id):
    client = docker.from_env()
    container = client.containers.get(id)
    container.stop()
    container_name = container.name
    msg = f"Container {container_name} has been stopped"
    return msg

@job
def remove_container_task(id):
    client = docker.from_env()
    container = client.containers.get(id)
    container.remove()
    container_name = container.name
    msg = f"Container {container_name} has been removed"
    return msg

@job
def restart_container_task(id):
    client = docker.from_env()
    container = client.containers.get(id)
    container.restart()
    container_name = container.name
    msg = f"Container {container_name} has been restarted"
    return msg
