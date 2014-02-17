##git-vimdiff - git diffs in vim tabs with splits

### SYNOPSIS

`git vimdiff <args...>`

### DESCRIPTION

Use all the regular arguments to `git diff` that you already know and love, but
view the diffs in side-by-side vim splits with a tab for each changed file.

The script respects your `$EDITOR` variable, but it has to be a vim of some
kind.

### INSTALLATION

Place `git-vimdiff.py` in your `$PATH` somewhere. Personally, I symlink it to
`~/bin/git-vimdiff` and have `~/bin` in my `$PATH`.

This requires either of the latest versions of Python 2 or Python 3.

### LICENSE

Copyright (C) 2012 Masud Rahman

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

