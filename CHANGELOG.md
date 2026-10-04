# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Entries for releases before this file existed were generated from commit subjects.

## [1.2.0] - 2026-10-04

- Add QImageWidget for raw images, share stretch/cuts controls with QFitsWidget

## [1.1.3] - 2026-09-15

- Responsive Cuts/Stretch/Colormap toolbar: hide labels, then overflow checkboxes

## [1.1.2] - 2026-09-07

- Catch any WCS-formatting failure, not just NaN

## [1.1.1] - 2026-09-07

- Guard hover overlay against NaN WCS coordinates

## [1.1.0] - 2026-09-03

- Remove upper bound on Python version

## [1.0.0] - 2026-06-08

- updated deps

## [0.13.2] - 2026-06-08

- added from __future__ import annotations
- removed from __future__ import annotations everywhere

## [0.13.1] - 2025-12-01

- fixed bug

## [0.13.0] - 2025-12-01

- added missing files
- signals, type hints
- fixed uic errors
- scale rgb images to [0..1]
- qtpy
- cleaning up
- cleaning up for pyside6
- initial conversion

## [0.12.2] - 2025-07-29

- type hints
- versions

## [0.12.1] - 2025-07-07

- migrated to uv

## [0.12.0] - 2025-06-20

- Maintenance release (dependency and metadata updates only).

## [0.11.0] - 2025-06-20

- bumped astropy

## [0.10.1] - 2025-01-07

- python 3.13

## [0.10.0] - 2024-09-24

- right-click menus
- callback methods for menu entries, formatted via jinja2
- configurable menu
- showing a menu works
- updated devs to latest version
- tests

## [0.9.12] - 2024-07-08

- python 3.12

## [0.9.11] - 2023-12-07

- fixed bugs when no WCS is present

## [0.9.10] - 2023-12-07

- Maintenance release (dependency and metadata updates only).

## [0.9.9] - 2023-09-12

- updating deps

## [0.9.8] - 2023-09-06

- Maintenance release (dependency and metadata updates only).

## [0.9.7] - 2023-09-06

- HPLN coordinates

## [0.9.6] - 2023-07-18

- update

## [0.9.5] - 2023-07-18

- changed opencv-python to -headless
- new position angle

## [0.9.4] - 2023-05-05

- added OpenCV dep

## [0.9.3] - 2023-05-05

- GH workflow
- Py3.11 compat and upgraded deps

## [0.9.2] - 2023-05-05

- check for AttributeError

## [0.9.1] - 2022-07-28

- work with poetry

## [0.9.0] - 2022-07-28

- use center of image if CRPIX1/2 is not available
- print rgb values
- enable zoom
- zoom
- zoom options
- working on disabling zoom
- fixed bug with disabling elements
- .
- fixed bug with not plottings caled image
- settings for overlay text
- removed widgets
- zoom image
- making everything faster with blitting
- overlay text tests
- fixed bug
- clim for zoom
- removed debug output
- button to hide overlays
- more settings
- dependencies
- use poetry
- settings
- restructuring
- customizing toolbar
- fixed some bugs
- better compass
- cleaning up
- fixed N/E cross
- draw centre with half cross
- N/E directions arrow
- zoom works
- mouse hover in thread pool
- testing qimage
- changed sorting to stable
- fixed y coord
- testing
- added opencv-python
- rgb works (?)
- mouse events
- toolbar
- working on matplotlib version

## [0.8.2] - 2021-10-15

- reduced size of cut inputs
- check colormap before setting
- added try/except block around call to _trim_image, in case images come in too fast. Need to fix this!
- flip y for RA/Dec calculation

## [0.8.1] - 2021-07-01

- fixed bug with cuts
- handling colour images with axes aligned as (x, y, 3) instead of (3, x, y)
- explicitly cast float to int
- don't scale with cuts if image is uniform
- v0.8
- process new images in a thread
- support for images with Bayer pattern
- added comment

## [0.7.1] - 2021-02-06

- correct cut for RGB images
- moved RGB axis from 2 to 0
- v0.7
- added support for RGB images, if they come as uint8 in a cube with 3 layers
- renamed qfitsview to qfitswidget
- fixed bug when mouse cursor is outside image
- v0.5
- removed debug output
- update zoomed image on new image even without mouse moving
- changed origin of image from upper left to lower left to be consistent with DS9 etc
- disable image controls until first image is displayed
- GitHub workflow for publishing to PyPI
- v0.4
- added mean/max in area
- new mode
- add credit to FA
- cursors
- working on GUI
- created GUI
- renamed QFitsView to qfitsview
- disttools -> setuptoold
- v0.2
- option for using trimsec in scaling of image
- changed default values for cuts and stretch
- fixed current value of pixel
- color of NE cross
- fixed changing cuts after every image
- only draw coordinate system, if wcs is present
- coordinate system
- flip image before displaying it
- fixed world coordinate calcualtion
- more normalization functions
- added log normalization
- added custom cuts
- added colorba
- move cursor with arrow keys, if image has focus
- accept mouse events
- added requirements
- Create .gitignore
- Create LICENSE
- initial commit
