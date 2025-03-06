There are a two ways to install **hashreport** on your system. Choose the option that works best for you:

## **Install with Pip**

You can install **hashreport** using `pip` from the Python Package Index ([PyPI](https://pypi.org/project/hashreport/)):

```bash
pip install hashreport
```

## **Install from Source**

### Prerequisites

- [Python 3](https://www.python.org/downloads/) (tested with 3.10+)
- [Git](https://git-scm.com/downloads) (optional)

### 1. Download the Repository

Clone the repository to your local machine using Git and navigate to the project directory:

```bash
git clone https://github.com/madebyjake/hashreport.git && cd hashreport
```

Alternatively, you can download the repository as a ZIP file and extract it to a folder on your machine.

### 2. Install Dependencies

First we'll install Poetry, a Python packaging and dependency management tool. There are a few ways to do this, but the recommended method is to use the installer script:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Next, install the project dependencies using Poetry:

```bash
poetry install
```

### 3. Run the Application

You can now run the application using Poetry:

```bash
poetry run hashreport --version
```
