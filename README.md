<div align="center">
  <img src="https://raw.githubusercontent.com/kubernetes/kubernetes/master/logo/logo.png" alt="K8sh Logo" width="150">
  <h1>K8sh</h1>
  <p><strong>A Filesystem-like Shell for Kubernetes</strong></p>
  <p>
    <a href="#features">Features</a> •
    <a href="#commands">Commands</a> •
    <a href="#navigation">Navigation</a> •
    <a href="#virtual-filesystem">Virtual Filesystem</a>
  </p>
</div>

## 🚀 Overview

**K8sh** is a powerful interactive shell for Kubernetes that provides a filesystem-like navigation experience. Navigate through your Kubernetes resources as if they were directories and files, making cluster management intuitive and efficient.

Say goodbye to lengthy `kubectl` commands and hello to a more natural way of interacting with your Kubernetes clusters.

## ✨ Features

- 📁 **Filesystem-like Navigation** - Browse Kubernetes resources using familiar concepts like directories and files
- 💻 **Familiar Shell Commands** - Use intuitive commands like `ls`, `cd`, `pwd`, and `cat`
- ⌨️ **Tab Completion** - Enjoy smart autocompletion for commands and resource paths
- 📜 **Command History** - Access previous commands with up/down arrow keys
- 🔍 **Fuzzy Path Matching** - Find resources even with typos in resource names

## 🛠️ Commands

| Command | Description | Example |
|---------|-------------|---------|
| `ls [path]` | List resources at current or specified path | `ls /default/pods` |
| `cd [path]` | Change current path | `cd deployments/nginx` |
| `cd -` | Return to previous directory | `cd -` |
| `pwd` | Print current path | `pwd` |
| `cat [resource]` | Display YAML definition with syntax highlighting | `cat configmap-name` |
| `edit [resource]` | Edit resource using your preferred editor | `edit deployment-name` |
| `exec [pod]` | Execute a command in a pod | `exec nginx-pod` |
| `logs [pod]` | View logs from a pod | `logs nginx-pod` |
| `help [command]` | Show help for all commands or specific command | `help cat` |
| `exit` | Exit the shell | `exit` |

## 🧭 Navigation

K8sh makes navigating your Kubernetes cluster as intuitive as browsing files on your computer:

```bash
# List all namespaces
$ ls /
default
kube-system
kube-public

# Change to the default namespace
$ cd default

# List resource types in the namespace
$ ls
configmaps
deployments
pods
services
...

# Navigate to deployments
$ cd deployments

# List all deployments
$ ls
frontend
backend
database

# View details of a specific deployment
$ cat frontend

# Navigate to pods of a deployment
$ cd frontend
$ ls
frontend-7f5569bb7f-bcgjs
frontend-7f5569bb7f-xdp2w

# View logs of a pod
$ logs frontend-7f5569bb7f-bcgjs

# Execute a command in a pod
$ exec frontend-7f5569bb7f-bcgjs
```

## 🗂️ Virtual Filesystem

K8sh organizes Kubernetes resources in a hierarchical structure:

- **Level 0**: Namespaces (directories)
- **Level 1**: Resource types (directories)
- **Level 2**: Resources (directories for workload controllers and pods, files for other resources)
- **Level 3**: Pods for workload controllers or containers for pods (directories for pods, files for containers)
- **Level 4**: Containers (files)

This structure provides a consistent mental model for navigating your cluster resources.

## 🔄 Resource Types

K8sh supports a wide range of Kubernetes resource types:

- ✅ Services
- ✅ Deployments
- ✅ DaemonSets
- ✅ StatefulSets
- ✅ ReplicaSets
- ✅ ConfigMaps
- ✅ Secrets
- ✅ Ingresses
- ✅ Pods
- 🤔 Custom Resources

---

<div align="center">
  <p>Made with ❤️ for Kubernetes users</p>
</div>
