# podman-gitops

Apply GitOps concepts to Podman based container deployment use cases


## Goal

GitOps is well define for OpenShift and other K8S platforms. An introduction to GitOps with OpenShift can be found here:
https://blog.openshift.com/introduction-to-gitops-with-openshift/

However, there are use cases where container based workloads should run on bare Linux systems without Kubernetes. GitOps workflows should applicale for Podman based systems as well.

The goal of podman-gitops is to provid an example implemenation for applying GitOps to Podman based solutions.

## Key concepts

- All configurations are stored and managed in Git. A key maniest for this use case are the K8S pod yamls.
- Users define pods in K8S-like manifests, which are deployed to Podman.
- In the current, early implementation, a configuratin file per podman systems defines the Git repos, which contain pod yaml manifests that are deployed on the podman systems. This configuratin file is managed in git as well.
- Leverage Podman's pod functionality so that pods can be used for OpenShift and Podman deployments.
