Ink2Impress
===========

Ink2Impress is a converter-like script that enables using [Inkscape](http://inkscape.org/)
as a GUI for generating [Impress.js](https://github.com/bartaz/impress.js) presentations.

# Demo

[Basic Ink2Impress demo](http://tmr232.github.com/Ink2Impress) (result only)

Your demos are welcome!

# Usage

1. Create a new Inkscape document
	* Set the size of the page to the actual pixel-size you want
	for your presentation.
2. Make sure you have 2 layers (create if necessary)
	* Bottom layer will hold the graphics
	* Top layer will hold the layout
3. Create your graphics
	* Remember to keep all the graphical elements inside the page.
	Graphics outside the page will not show.
4. Create your layout
	* Each `<rect>` element in the layout layer will ve a step in the
	presentation
	* `<rect>` elements may be contained in groups (`<g>` elements).
	You can add other (non-`<rect>`) elements to the group as annotations.
	They will not show in the final presentation.
	* Z-Order dictates presentation order (bottom to top)
	* If you add an overview-step, set its `id` to `overview`
5. Save your presentation as plain-svg (not Inkscape SVG)
6. Run the convertion script
	* python ink2impress.py <source-svg> <target-html>
	* Make sure `js/impress.js` is in the same folder as the result
7. Enjoy!

# Dependencies

### Code
[lxml](http://lxml.de/) - XML processing - Use [this](http://www.lfd.uci.edu/~gohlke/pythonlibs/) for precompiled binaries.
[impress.js](https://github.com/bartaz/impress.js) - For the animations in the presentation.

### Software
[Python2.7](http://python.org/) - For running the script. Not tested for other versions.
[Inkscape](http://inkscape.org/) - For presentation creation
