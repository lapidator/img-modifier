From the docstring of the main class:

> A script for image manipulations (currently in a proof-of-concept status).
>
> This project is based on two pillars:
>  - use OO-Python code
>  - test the concept of creating partially transparent images from
>    full-color images
>
> This script is currently at a proof-of-concept stage. While it does work,
> there are still multiple issues (see below). It might also be extended by
> more functionalities, e.g., applying a multiplication of the result from
> the `grayscale_to_transp` function with the input image, in order to get
> a color image that is combined with the transparency.
>
> Issues:
> =======
>  - Results from JPEG/JPG images are likely to not meet expectations,
>    especially concerning the handling of their colors. This might be
>    related to their format (chroma subsampling YUV420/422/444). For PNGs it
>    appears to work just as expected, as the test images use RGBA instead.
>  - The current performance is poor, i.e., the script is very slow to be
>    executed on images that have more than just a few pixels. A likely large
>    contribution to this fact is that the handling of numpy.arrays could be
>    improved at multiple points.
>  - Initially this script relied on forward slashes (`/`) in paths, such as
>    in Linux systems. This should be fixed by now, but it is not tested yet.

## Usage

Refer to the document's main (`if __name__ == '__main__'`) at the bottom of the file to find further notes and examples. Some test cases are commented out. In case the different comment formats for notes and for commented code are not obvious, actual comment lines start with a double hash mark (`##`), while lines of commented code start with a single hash mark (`#`).

Furthermore, from the docstring of the main class:

> User Methods:
> =============
> Each method's docstring contains more information about its usage.
>  - `save`: save the current image
>  - `grayscale`: convert the current image to grayscale
>  - `grayscale_to_tranp`: convert a grayscale image into tranparency based
>    on each pixel's brightness
