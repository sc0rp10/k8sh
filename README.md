<div align="center">
  <img src="https://raw.githubusercontent.com/kubernetes/kubernetes/master/logo/logo.png" alt="K8sh Logo" width="150">
  <h1>K8sh</h1>
  <p><strong>A Filesystem-like Shell for Kubernetes</strong></p>
  <p>
    <a href="#features">Features</a> •
    <a href="#installation">Installation</a> •
    <a href="#commands">Commands</a> •
    <a href="#navigation">Navigation</a> •
    <a href="#virtual-filesystem">Virtual Filesystem</a>
  </p>
</div>

## 🚀 Overview

**K8sh** is a powerful interactive shell for Kubernetes that provides a filesystem-like navigation experience. Navigate through your Kubernetes resources as if they were directories and files, making cluster management intuitive and efficient.

Say goodbye to lengthy `kubectl` commands and hello to a more natural way of interacting with your Kubernetes clusters.

## 📦 Installation

### Requirements

- A working Kubernetes cluster
- `kubectl` configured and working on your system
- Python 3.11 or higher

### Debian/Ubuntu Installation

1. Download the latest `.deb` package from the [Releases](https://github.com/sc0rp10/k8sh/releases) page

2. Install the package:
   ```bash
   sudo dpkg -i k8sh_1.0.2_all.deb
   ```

3. Start the shell:
   ```bash
   k8sh
   ```

### Verifying Installation

After installation, verify that K8sh can connect to your Kubernetes cluster:

```bash
# Start the shell
k8sh

# List available namespaces
ls /
```

If you see your Kubernetes namespaces listed, the installation was successful!

### Troubleshooting

- If K8sh can't connect to your cluster, verify that `kubectl` works correctly
- Check that your kubeconfig file is properly configured
- Ensure you have the necessary permissions to access your cluster

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

## 🔧 Configuration

K8sh uses your existing kubectl configuration, so no additional setup is required. It will connect to whatever cluster is currently active in your kubeconfig.

## 📋 Requirements

- **Kubernetes Cluster**: A working Kubernetes cluster (local or remote)
- **kubectl**: Properly configured kubectl with access to your cluster
- **Python 3.11+**: The package includes all necessary Python dependencies

---

<div align="center">
  <p>Made with ❤️ for Kubernetes users</p>
</div>
