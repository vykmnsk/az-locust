# Perf test environment architecture

## Overview

To generate enough load we should be able to run the performance tests on a powerful server (VM) or be able to distribute the load on multiple machines.

Probably the simplest Azure solution would be to utilize __Azure Container Instances__ with __Storage Share__  orchestrated with __Bash scripts__ and __ARM templates__ and __Dockerfile__ stored in a Bitbucket repo.


## Details

### with ARM template
* declare 1 master Container 
* declare n slave Containers (workers)
* configure workers to communicate with the master over a public IP & DNS name

### via Azure CLI (script):
* create Resource Group
* create Storage Account
* create Storage Share
* upload files with performance tests code
* configure/deploy Containers via ARM template
* read back _master URL_

### in Browser
* open URL, (re)start and monitor perf tests via GUI


