# [0.2.0](https://github.com/robcxyz/tackle-box/compare/v0.1.1...v0.2.0) (2022-07-29)


### Features

* rm PartialModelMetaclass which simplifies model creation / tmp rm jinja filters ([21b4417](https://github.com/robcxyz/tackle-box/commit/21b441774e0c1fc9038d3583555dbf30e3e3c428))



## [0.1.1](https://github.com/robcxyz/tackle-box/compare/v0.1.0...v0.1.1) (2022-07-21)


### Bug Fixes

* issue with unquoted string cleanup function on empty dicts: ([b1e8b3f](https://github.com/robcxyz/tackle-box/commit/b1e8b3faf60c018f143b019f85732b13abe639d2))



# [0.1.0](https://github.com/robcxyz/tackle-box/compare/f173ef6818d179ed4f21ef899cad49bcb080b9f3...v0.1.0) (2022-07-21)


### Bug Fixes

* add exception for unknown variables the same as hook_types closes [#55](https://github.com/robcxyz/tackle-box/issues/55) ([b0b47ea](https://github.com/robcxyz/tackle-box/commit/b0b47ea85ae9be3ceeb96149126f15261b1cbc2c))
* add field for functions ([1a56f74](https://github.com/robcxyz/tackle-box/commit/1a56f74c81136394b29d041e49c9ae9d23d735aa))
* add smart_union to fix mangling of list inputs ([971ca88](https://github.com/robcxyz/tackle-box/commit/971ca882371f7079fc5f3f7a893bf6116b0d90f4))
* args refactor in docs hook ([0163d99](https://github.com/robcxyz/tackle-box/commit/0163d993a31ae65237ae76f1d2e4b565ba4c682c))
* checkbox hook with new API ([6e0b532](https://github.com/robcxyz/tackle-box/commit/6e0b532e54a08de49468979971013d177ce363f3))
* compact expression macro reindex based on key_path_block correctly ([a53942a](https://github.com/robcxyz/tackle-box/commit/a53942ab1fccccba52e93d4d550c0733bc145ee5))
* compact key macro to preserve order ([7ecf467](https://github.com/robcxyz/tackle-box/commit/7ecf467f0507bb91869a2846abdfb8eb210ce73c))
* declarative hooks using base object types and validations ([a3aa32d](https://github.com/robcxyz/tackle-box/commit/a3aa32db5bd2da67b2e2afe06977b50768f783c7))
* distinguish types with merge ([6c3bbed](https://github.com/robcxyz/tackle-box/commit/6c3bbedebd574cbafc26b2a058d175c6193c75b1))
* docs gen problem hooks copy over ([ff2a7f8](https://github.com/robcxyz/tackle-box/commit/ff2a7f8f32ff7f8122462e2dd3263747447649e1))
* drop used hooks from globals to fix second use of hook bug which didn't reinitialize and catch errors better ([f836229](https://github.com/robcxyz/tackle-box/commit/f836229e1e813e00c97e8501f62fe5ad93d9f090))
* else condition with bools, ints, and floats ([c2ce7b4](https://github.com/robcxyz/tackle-box/commit/c2ce7b42fe4c0f868f6ddae30963ef52e6a80968))
* embedded blocks issue with copying over key_path ([00f7ce8](https://github.com/robcxyz/tackle-box/commit/00f7ce8fdb356e8350d2c81cc75ee7b5c236b3cf))
* extends in declarative hooks ([8b33e6c](https://github.com/robcxyz/tackle-box/commit/8b33e6c1f9eff7d5b81c661eacc5af2c0681c72b))
* fixture that had invalid validator ([8dbf575](https://github.com/robcxyz/tackle-box/commit/8dbf57573be7eac2a483cfb7056e3f7420150f2b))
* for checkbox hook return all when checked and no_input ([a659901](https://github.com/robcxyz/tackle-box/commit/a6599014ad499085c18db5eb8504d8a3bec6457a))
* for temporary contexts which in edge cases can have unusable single values written them ([003563e](https://github.com/robcxyz/tackle-box/commit/003563ecd29c4ee8c4d8a01bf1b99c85ae886094))
* function return ref ([8265151](https://github.com/robcxyz/tackle-box/commit/8265151491728e78ae3aaf5e53ce43a583fad655))
* keyboard interrupt handling in prompts ([fe112d0](https://github.com/robcxyz/tackle-box/commit/fe112d0c90bd4ee3c1a3921604d22d4e4e3c15c3))
* load context on tackle hook with right precedence ([760cb61](https://github.com/robcxyz/tackle-box/commit/760cb61a27c0ffa523dd9e2eb7815a3881507bdd))
* match hook block macro not indenting block matches properly ([12cfc55](https://github.com/robcxyz/tackle-box/commit/12cfc554f2367147f895ce01df5126cc04274187))
* merge dict in block ([ec8d3d9](https://github.com/robcxyz/tackle-box/commit/ec8d3d9d39738e102195ba707da5098bc4575c1c))
* move try back into parser so it doesn't automatically write None to output - only on except ([797c776](https://github.com/robcxyz/tackle-box/commit/797c7768b83b5babe917ba23054415cdd0c9ed3b))
* parsing error from ruamel fix macro on empty items ([1e460b9](https://github.com/robcxyz/tackle-box/commit/1e460b98f1b794ed25221fd4f76fce264fa2913f))
* print in the case of non list / dict outputs ([11ea041](https://github.com/robcxyz/tackle-box/commit/11ea041e5e5c3c8b49e4d0ff8553e8c1dca06033))
* readable key path for prompt messages ([9bfaa7f](https://github.com/robcxyz/tackle-box/commit/9bfaa7f5419651a3170574a5059153ac36175e99))
* readable key path for string ([6ee040e](https://github.com/robcxyz/tackle-box/commit/6ee040ebcc9233210be9c2ea414283be6928851f))
* rebuild block hook indexing so that writes happen directly to output_dict ([874a046](https://github.com/robcxyz/tackle-box/commit/874a0469b91db94d07f0f86344f27beaf89b57b6))
* remove choices and default args from prompt hooks - only message now ([ca135dd](https://github.com/robcxyz/tackle-box/commit/ca135dd40a0a82cdbe92ef9012f5791af042fb70))
* ruamel parsing error macro that messed up empty keys ([c6bc582](https://github.com/robcxyz/tackle-box/commit/c6bc58202e2fde7bddf62587c1362944f80573ba))
* ruamel parsing error with un-quoted braces that returns ambiguous ordered dict and jams parser ([bd6922f](https://github.com/robcxyz/tackle-box/commit/bd6922fe24564f461eac87c4d7a7d30a4738dc88))
* update hook to actually update the values instead of overwriting them ([6a767bc](https://github.com/robcxyz/tackle-box/commit/6a767bc46211727ec55e476101bc862beeef8346))
* warning about invalid escape of \, in command lexer ([6849824](https://github.com/robcxyz/tackle-box/commit/684982491e194b96d4e00a97bafb5594813a8a08))
* yaml hook - force output to be string with extra json [#56](https://github.com/robcxyz/tackle-box/issues/56) ([80a956f](https://github.com/robcxyz/tackle-box/commit/80a956fd6a6f5564dfe7433515fd587503cbf20e))


### Features

* add ability for declarative hooks to be run as jinja extensions and filters ([d6e3dea](https://github.com/robcxyz/tackle-box/commit/d6e3dea3fbc1957db7ffc942490b21232ce50a3e))
* add ability to default render context when no hook provided ([0e89c0e](https://github.com/robcxyz/tackle-box/commit/0e89c0eaedb19b7535ec6bf28079fea0f5f18d00))
* add auth handler for web requests pprovider ([b635dc3](https://github.com/robcxyz/tackle-box/commit/b635dc3416c2e40b16a3c24f4069179059d43c0d))
* add basic function parser without exec ([4161410](https://github.com/robcxyz/tackle-box/commit/416141006dc6b84759954f55f18d6b66bd62011d))
* add better exception handling that returns context with the error ([fb0f466](https://github.com/robcxyz/tackle-box/commit/fb0f466c4273d43a3ecbceca0b458c61d799f86e))
* add cleanup function for when we have unquoted strings in hook args which can lead to frustrating errors that are hard to debug ([47871b3](https://github.com/robcxyz/tackle-box/commit/47871b37af14269b305f15d3a00d04eec1d4ac69))
* add datetime provider ([b8b0cfd](https://github.com/robcxyz/tackle-box/commit/b8b0cfd037ea04c8c607de76f059f47df1af2503))
* add find-in-parent cli flag and in tackle to search for tackle file in parent ([daee9d2](https://github.com/robcxyz/tackle-box/commit/daee9d2b24bc591ed73eebfca129477563af1af9))
* add fzf to select hook ([3a295c8](https://github.com/robcxyz/tackle-box/commit/3a295c851268b807f2afff6a92364f28f3c41b0b))
* add implicit value for an empty tackle call - searching for nearest tackle ([c5dd034](https://github.com/robcxyz/tackle-box/commit/c5dd0343f98b981852ea56f6c5861b29989b0f97))
* add latest flag to pull latest version ([8c3b687](https://github.com/robcxyz/tackle-box/commit/8c3b6874805a4cf08af5cab169fbc9a50f617aaf))
* add mkdocs and first pass on documentation ([be92f89](https://github.com/robcxyz/tackle-box/commit/be92f8902a038b16dd7d8d5b11c17e76a0878384))
* add override key to cli and main to override input key ([248dbb0](https://github.com/robcxyz/tackle-box/commit/248dbb0f17d4070a2c191f16030a1bd57e0a1384))
* add provider docs hook and docs code generator ([2befdc5](https://github.com/robcxyz/tackle-box/commit/2befdc5542d4fe6ecdadd601d3b269e734413cbd))
* add toml support ([d4698df](https://github.com/robcxyz/tackle-box/commit/d4698dfdfd5999c1cc94a48f314dba3457b0d5a5))
* add try method without any except ([6c33dbc](https://github.com/robcxyz/tackle-box/commit/6c33dbcf5a8f93abb97dd59b06be626230498fd2))
* add xdg and comply with spec to change location of takle directory and add tests for importing ([dd0cccb](https://github.com/robcxyz/tackle-box/commit/dd0cccb078b4a84517338c17340430526e8771ec))
* get else and except working and fix out of order macros ([9f018e2](https://github.com/robcxyz/tackle-box/commit/9f018e2ffc85872c6f95e7bfaf57bc359a73fe7f))
* implement initial hook methods ([67cf309](https://github.com/robcxyz/tackle-box/commit/67cf30946a2e6f3f7b024a28c1753245e43a939f))
* implement memory maangement with public private temp and existing contexts ([b37392e](https://github.com/robcxyz/tackle-box/commit/b37392eeb1d0153809b00adbcf8ee7a89d322e6a))
* implement methods on declarative hooks ([60f620f](https://github.com/robcxyz/tackle-box/commit/60f620f3486b98a9eb7b319e78cdd9bec7c39426))
* initial collections provider ([ffcd272](https://github.com/robcxyz/tackle-box/commit/ffcd2726b11fe7481f16e6db9dfd549bb55ebb42))
* make parser generic - mid overhaul ([6fbda6a](https://github.com/robcxyz/tackle-box/commit/6fbda6aa1b930f9ec10db7805543a174202f45c5))
* new parsing order logic and hook syntax ([91e37cd](https://github.com/robcxyz/tackle-box/commit/91e37cd91d4a6c3c81c615a44d9ac387344684dd))
* provider overhaul for 0.3.0 release ([070caaa](https://github.com/robcxyz/tackle-box/commit/070caaab3989e674202fa0102e804fe7029b5281))
* **README:** added cookiecutter-django-rest ([f173ef6](https://github.com/robcxyz/tackle-box/commit/f173ef6818d179ed4f21ef899cad49bcb080b9f3))
* **README:** added cookiecutter-es6-boilerplate ([dc533d4](https://github.com/robcxyz/tackle-box/commit/dc533d4db6c7f2ff54f0b8549bc982659d83e075))
* redo rendering to include special vars lazy lookup and remove slugify extension ([8ebf200](https://github.com/robcxyz/tackle-box/commit/8ebf200b7edfbbf4f983d0490b439aea78d3f99b))
* remove pre hook init object (hook_dict) and get loops working ([1fab36c](https://github.com/robcxyz/tackle-box/commit/1fab36c197ed71997d1f743b206b5f15215147e9))
* rm click dependency and use argparse ([60b98e6](https://github.com/robcxyz/tackle-box/commit/60b98e6f4f00de706f42c798b22d295a1fc3abf7))
* update all system hooks with descriptions and arguments ([ac56486](https://github.com/robcxyz/tackle-box/commit/ac5648638775a90e010ae18013ff8d47eacfd091))
* update parser to render variables more selectively and before they are used to initialize a hook ([1b160ca](https://github.com/robcxyz/tackle-box/commit/1b160ca852644e1118071eafbadac0ac9f6174b1))
* upgrade PyInquirer to InquirerPy ([62b68e4](https://github.com/robcxyz/tackle-box/commit/62b68e43562163aa2715c6e03b40ea973af0313e))


### Reverts

* Revert "Mark test_cookiecutters jquery with xfail due to undefined variable" ([24c108d](https://github.com/robcxyz/tackle-box/commit/24c108df4b6f8e25238908212eea3810cf714c2e))
* Revert "Run py35 on travis" ([b311b10](https://github.com/robcxyz/tackle-box/commit/b311b101bfbaf0a6d3463a628db73f40d8056665))


