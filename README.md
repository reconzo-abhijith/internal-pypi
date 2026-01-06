## What this package does

This package is expected to act on a local repository, which is just a folder
containing python packages. A repository has a root index html file that lists
all the packages that are available from this repository to install.

For each folder in the local repository, the package
will create an index html file that lists all the installable versions of the
package as per the [Simple API
spec](https://packaging.python.org/en/latest/specifications/simple-repository-api/#simple-repository-api)

## Who uses this package

This package is for use by package writers to upload to a Simple API repository.
Package creation is not the responsibility of this package.

Expectations -
1. A repository without folders in it should error
2. Folder names must get normalized - normalization is defined in the Spec
