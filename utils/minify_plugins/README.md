# Minify plugins

This utility allows you to automatically minify css and js files for each plugin on UNCode.  

## How to use

All the code and logic is in the script `minify_plugins.js`. This uses [terser][terser_url] to minify JavaScript files,
and for CSS files, [Clean CSS][clean_css_url] is used.

### Minify new plugins

In case a new plugin is added, you have to update the `minify_plugins.js` script, For that, a separate function is
 created for each plugin, please see how this is done for the other plugins.

### Run minifier 

Before you start, you must install `node 8.x` or a greater version and `npm`.

Install dependencies:

```bash
npm install
```

Update/create minified files for all plugins:

```bash
npm run minify
```

## Plugins

The plugins being minified are:
- UNCode.
- UN template.
- Statistics.
- Register students.
- Multilang.
- Grader generator.
- Custom input.
- Code preview
- Analytics
- Plagiarism

Some of this plugins, generate more than one minified file, for example, multilang.

[terser_url]: https://github.com/terser/terser
[clean_css_url]: https://www.cleancss.com/