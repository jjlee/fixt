Make objects for use in tests, automatically making dependencies.

This is similar to the Test Data Builder pattern. It has some of the same
benefits.

Additional benefits compared to that pattern:

* "Make me an `x`, any `x` will do" is very easy

* That is because automatically creating dependencies is very easy, which is in
  turn because by default every object type has either zero or one instance

* Automatically creating dependencies is still easy when a dependency deep in a
  construction chain needs to be injected

Problems compared to that pattern:

* Creating multiple instances is clunkier (but still possible)

* Less strong at developing a "business language" directly supported by
  builders.


I think the problems may be fixable, but I think that would be a new project.


## Run the tests

A `tox.ini` file is provided to run the tests with different versions of
Python.

To run the tests:

1. Install tox
2. Run `tox` from the root folder of the repository


## See also

This project is closely based on my memory of a simpler but very similar tool
written by Mark Seaborn in maybe 2008. This adds namespaces, which makes this
not so elegant as Mark's version, but I've found them somewhat useful.

Inspired by this project: https://github.com/palankai/baluster

https://pypi.python.org/pypi/make-it-easy

https://pypi.python.org/pypi/factory_boy
