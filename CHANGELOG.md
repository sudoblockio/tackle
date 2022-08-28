# Changelog

## [0.3.0](https://github.com/robcxyz/tackle-box/compare/0.3.0-beta.5...v0.3.0) (2022-08-28)


### Features

* add ability to call declarative hook nested methods ([a44165b](https://github.com/robcxyz/tackle-box/commit/a44165b40b2b1b09ef1d78f1bf3ca1b998a12a0c))
* add auth handler for web requests pprovider ([b635dc3](https://github.com/robcxyz/tackle-box/commit/b635dc3416c2e40b16a3c24f4069179059d43c0d))
* add cleanup function for when we have unquoted strings in hook args which can lead to frustrating errors that are hard to debug ([47871b3](https://github.com/robcxyz/tackle-box/commit/47871b37af14269b305f15d3a00d04eec1d4ac69))
* add datetime provider ([b8b0cfd](https://github.com/robcxyz/tackle-box/commit/b8b0cfd037ea04c8c607de76f059f47df1af2503))
* add default kwargs mapper field so that by default, extra fields can be mapped to another attribute ([94fc9e9](https://github.com/robcxyz/tackle-box/commit/94fc9e952ab511e25af5a25d3281417af852f187))
* add fzf to select hook ([3a295c8](https://github.com/robcxyz/tackle-box/commit/3a295c851268b807f2afff6a92364f28f3c41b0b))
* add override key to cli and main to override input key ([248dbb0](https://github.com/robcxyz/tackle-box/commit/248dbb0f17d4070a2c191f16030a1bd57e0a1384))
* add toml support ([d4698df](https://github.com/robcxyz/tackle-box/commit/d4698dfdfd5999c1cc94a48f314dba3457b0d5a5))
* add xdg and comply with spec to change location of takle directory and add tests for importing ([dd0cccb](https://github.com/robcxyz/tackle-box/commit/dd0cccb078b4a84517338c17340430526e8771ec))
* rm PartialModelMetaclass which simplifies model creation / tmp rm jinja filters ([21b4417](https://github.com/robcxyz/tackle-box/commit/21b441774e0c1fc9038d3583555dbf30e3e3c428))


### Bug Fixes

* drop used hooks from globals to fix second use of hook bug which didn't reinitialize and catch errors better ([f836229](https://github.com/robcxyz/tackle-box/commit/f836229e1e813e00c97e8501f62fe5ad93d9f090))
* error passing context to jinja hook calls ([cfdda49](https://github.com/robcxyz/tackle-box/commit/cfdda495684129623129bc5b8f16cb9d40b43dd9))
* fixture that had invalid validator ([8dbf575](https://github.com/robcxyz/tackle-box/commit/8dbf57573be7eac2a483cfb7056e3f7420150f2b))
* issue with non-defaulted base parameters when calling declarative hook methods ([da315d9](https://github.com/robcxyz/tackle-box/commit/da315d957b7f2ec127395ec87d8ea91d49c6202b))
* issue with unquoted string cleanup function on empty dicts: ([b1e8b3f](https://github.com/robcxyz/tackle-box/commit/b1e8b3faf60c018f143b019f85732b13abe639d2))
* nested declarative hook nested method call ([d9cbf11](https://github.com/robcxyz/tackle-box/commit/d9cbf11b8d0f16dbd115d39f1a798194ca288c2d))
* print in the case of non list / dict outputs ([11ea041](https://github.com/robcxyz/tackle-box/commit/11ea041e5e5c3c8b49e4d0ff8553e8c1dca06033))
* update hook to actually update the values instead of overwriting them ([6a767bc](https://github.com/robcxyz/tackle-box/commit/6a767bc46211727ec55e476101bc862beeef8346))
