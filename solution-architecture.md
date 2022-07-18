# PLT solution architecture

## Overview

To generate enough load we should be able to run the performance tests on a
powerful server (VM) or be able to distribute the load on multiple machines.

Azure cloud would be the most suitable to scale as necessary plus at least some
of the PLT targets are already hosted on Azure (Pricing, Eventing).

Probably the simplest solution would be to utilize **Azure Container Instances**
with **Storage Share** orchestrated with **Bash scripts** and **ARM templates**
and **Dockerfile** stored in a Bitbucket repo.

For more complete container orchestrator, of course, Kubernetes could also be
used but it may be too complex for PLT team.

## Details

### with ARM template

- declare 1 master Container
- declare n slave Containers
- configure slaves to communicate with the master over a public IP & DNS name

### via Azure CLI (script)

- create Resource Group
- create Storage Account
- create Storage Share
- upload files with performance tests code
- configure/deploy Containers via ARM template
- read back _master URL_
- start Load tests via a REST API call

### in Browser

- monitor the tests run via _master URL_
