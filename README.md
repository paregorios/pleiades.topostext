# Extract ToposText:Pleiades matches for upload to Pleiades

[_ToposText_](https://topostext.org/) is an excellent resource and every corresponding [_Pleiades_](https://pleiades.stoa.org) place resource should cite it with a link. Since _ToposText_ was created from a dump of _Pleiades_ data, and since [the _ToposText_ team](https://topostext.org/who-we-are) has taken care to keep track of the backlinks to _Pleiades_, it should be straightforward to extract the _Pleiades_:_ToposText_ pairs from [the _ToposText_ RDF dump](https://topostext.org/TT-downloads) and programmatically construct _Pleiades_ references to point at those pages.

This package is intended to accomplish that task.

At the moment, we only have test functionality (with nose):

```
nosetests
```

 [See the issue tracker](https://github.com/paregorios/pleiades.topostext/issues) for next steps.
