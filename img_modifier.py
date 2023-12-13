import os
import imageio
import numpy as np


def _yn_prompt(prompt, default=None):
    """
    A short function to give the user a prompt and ask yes-or-no. It is pos-\\
    sible to choose a default answer, which is then indicated automatically.

    Parameters:
    -----------
    `prompt` : string
        A user prompt, typically a question, which has a yes-or-no answer.
    `default` : [`'y'`, `'yes'`] / [`'n'`, `'no'`]
        If one of the options is given the respective default setting is in-
        dicated. Otherwise default is set to `None` and no answer is indicated.

    Returns:
    --------
    Depending on the user's choice returns a boolean value (`True` for yes and
    `False` for no).

    Dependencies:
    =============
    `---`
    """
    if default is None:
        deflt, opt = " [y/n] ", -1
    else:
        if not isinstance(default, str):
            raise Exception("Invalid `default` parameter setting.")
        if default.lower() in ['y', 'yes']:
            deflt, opt = " [Y/n] ", 1
        elif default.lower() in ['n', 'no']:
            deflt, opt = " [y/N] ", 0
        else:
            deflt, opt = " [y/n] ", -1

    while True:
        inp = input(prompt + deflt)
        if (not inp and opt==1) or inp.lower().startswith('y'):
            re = True
            break
        elif (not inp and opt==0) or inp.lower().startswith('n'):
            re = False
            break
        else:
            continue
    return re

def _g_filedialog(initialdir=None, title=None, filetypes=None):
    """
    Open a graphical filedialog to choose a file.

    Parameters:
    -----------
    `initialdir` (optional) : string (path)
        Path of the initial directory the filedialog should open. If not
        specified will open current directory.
    `title` (optional) : string
        Title of the filedialog window.
    `filetypes` (optional) : tuple of tuples describing selectable file types
        Example if only py-files should be shown in the filedialog:
        filetypes = (("Python files", "*.py"), ("all files", "*.*"))
        My testing so far indicated that the "all files" tuple is always
        necessary, in case `filetypes` is specified. Thus, I added a detection

    Returns:
    --------
    `fullpath` : string (path to the file)
        Full path to the selected file, e.g.
        /home/username/Python_codes/test.1.py
    `filename` : string (filename)
        Full filename, e.g.
        test.1.py
    `dir_path` : string (path to parent directory)
        Path to the file parent directory, e.g. `/home/username/Python_codes`.
    `file_ext` : string (file extension)
        File extension without the leading separator, e.g., no leading dot such
        as `py`.
    `extstrip` : string (filename without extension)
        Filename without its file extension. May still contain dots, e.g.
        `test.1`.

    Dependencies:
    =============
    Outer:
    ------
    `_yn_prompt` from this module
    Inner:
    ------
    `tkinter`, `tkinter.filedialog`
    """

    ## imports necessary for a tkinter filedialog
    import tkinter
    from tkinter import filedialog
    root = tkinter.Tk().withdraw() # standard code snippet when using tkinter

    ## test `filetypes` for correct input and adjust if necessary
    if "((" in str(filetypes).replace(" ", ""):
        if not ("all files", "*.*") in filetypes:
            filetypes = (*filetypes, ("all files", "*.*"))
    else:
        filetypes = (filetypes, ("all files", "*.*"))

    ## open filedialog with specified settings; None refers to default setting
    while True:
        filepath = filedialog.askopenfilename(
            initialdir=initialdir,
            title=title,
            filetypes=filetypes
            )
        if not filepath:
            if _yn_prompt("No file chosen. Do you want to continue?", "y"):
                continue
            else:
                # sys.exit("Exit")
                raise SystemExit("Exit")
        else:
            break

    ## assign values to return variables
    fullpath = filepath
    filename = os.path.basename(fullpath)
    dir_path = os.path.dirname(fullpath)
    file_ext = os.path.splitext(filename)[1][1:]
    extstrip = os.path.splitext(filename)[0]

    return fullpath, filename, dir_path, file_ext, extstrip

class InvalidParameterException(Exception):
    """ Exception for invalid parameter settings. """
    pass

class InvalidImageException(Exception):
    """ Exception for invalid image input. """
    pass

class Img:
    """
    A script for image manipulations (currently in a proof-of-concept status).

    This project is based on two pillars:
     - use OO-Python code
     - test the concept of creating partially transparent images from
       full-color images

    This script is currently at a proof-of-concept stage. While it does work,
    there are still multiple issues (see below). It might also be extended by
    more functionalities, e.g., applying a multiplication of the result from
    the `grayscale_to_transp` function with the input image, in order to get
    a color image that is combined with the transparency.

    Issues:
    =======
     - Results from JPEG/JPG images are likely to not meet expectations,
       especially concerning the handling of their colors. This might be
       related to their format (chroma subsampling YUV420/422/444). For PNGs it
       appears to work just as expected (test images use RGBA).
     - The current performance is poor, i.e., the script is very slow to be
       executed on images that have more than just a few pixels. A likely large
       contribution to this fact is that the handling of numpy.arrays could be
       improved at multiple points.
     - Initially this script relied on forward slashes (`/`) in paths, such as
       in Linux systems. This should be fixed by now, but it is not tested yet.
    
    User Methods:
    =============
    Each method's docstring contains more information about its usage.
     - `save`: save the current image
     - `grayscale`: convert the current image to grayscale
     - `grayscale_to_tranp`: convert a grayscale image into tranparency based
       on each pixel's brightness

    Dependencies:
    =============
    `os`, `imageio`, `numpy` as `np`, `_yn_prompt`, `_g_filedialog` \\
    (`_g_filedialog`'s dependencies: `tkinter`, `tkinter.filedialog`)
    """

    def __init__(self, filename=None):
        """
        Image object which gets all necessary attributes for later usage.

        If no filename is given a graphical filedialog is opened.

        Parameters:
        -----------
        `filename` : string (filename/-path)
            Effectively all inputs for imageio.imread() should work, but I only
            wrote and tested parts of this code for filenames/-paths in Linux-
            style. If `filename` is not specified a filedialog will be opened.

        Attributes:
        -----------
        `path` : Path to the file's parent directory (no trailing separator).\\
        `name` : Filename without extension, e.g. `testfile` or `test.file`. \\
        `ext` : File extension without a leading dot, e.g. `png`. \\
        `data` : Image data via `imageio.imread`, also containing meta data. \\
        `meta` : Image meta data via `imageio.imread` using its `meta` method.

        Information:
        ------------
        uint8 format: \\
        Due to the usage of `imageio.imwrite` all data will be converted to
        `uint8` before being saved to an image file. Thus, the data will be
        formatted respectively before saving. Without formatting `imageio`
        automatically detects the minimum and maximum value in the array and
        linearly adjusts all values accordingly from range `[min, max]` to
        range `[0, 255]`. \\
        Conversion of `x` to `uint8` via `numpy` works as follows:
            x in ]-inf, -1.0]    becomes    255
            x in ]-1.0,  0.0[    becomes      0
            x in [   0,  256[    becomes int(x), i.e. strips decimals
            x in [ 256,  inf]    becomes      0
        """
        if filename is None:
            filename = _g_filedialog()[0]

        ## catch some cases the code cannot handle (yet?)
        if filename[0] == '~': ## as I do not use pathlib.Path (yet) avoid `~`
            raise InvalidParameterException(
                "Using `~` for home is currently not supported."
            )
        if not os.path.isfile(filename):
            raise FileNotFoundError("No such file: '{}'".format(filename))

        self.path, file = os.path.split(os.path.abspath(filename))
        # self.name, self.ext = file.rsplit('.', 1)
        self.name, self.ext = os.path.splitext(file)
        self.ext = self.ext[1:]

        ## data and meta data
        self.data = imageio.imread(filename)
        self.meta = self.data.meta

    def _uint8(self):
        """ Ensure that current format is numpy.uint8. """
        ## one could pick one or all pixel and check: type(pixel) == np.uint8
        ## but it is bad practice to check for types, thus check values only
        if np.amin(self.data) >= 0 and np.amax(self.data) < 256:
            self.data = np.array(self.data).astype(np.uint8)
        else:
            self.data = np.interp(self.data,
                    (np.amin(self.data), np.amax(self.data)),
                    (0, 255)
                ).astype(np.uint8)
        return self

    def _rgba(self):
        """ Convert image data to RGBA shape in numpy.uint8 format. """
        dim = len(self.data.shape)
        # assert dim==2 or dim==3, "Only grayscale(a), RGB, or RGBA supported."
        if not (dim==2 or dim==3):
            raise InvalidImageException(
                "Invalid input image. Only grayscale[a] or RGBA supported."
            )
        self._uint8() ## ensure uint8 format
        if dim == 2: ## grayscale, i.e. row x column
            grayscale_to_rgba = np.array([ ## create RGB and A for RGBA
                    [[col, col, col, 255] for col in row] for row in self.data
                ]).astype(np.uint8)
            self.data = grayscale_to_rgba
        elif dim == 3: ## row x column x pixel with pixel: RGB(A)/grayA
            if self.data.shape[-1] == 3: ## RGB case
                rgb_to_rgba = np.array([ ## create A for RGBA
                        [[col[0], col[1], col[2], 255] for col in row
                        ] for row in self.data
                    ]).astype(np.uint8)
                self.data = rgb_to_rgba
            elif self.data.shape[-1] == 4: ## RGBA case
                pass ## just for readability/understanding purpose
            elif self.data.shape[-1] == 2: ## grayscale with alpha channel case
                grayscale_alpha_to_rgba = np.array([
                        [[col[0], col[0], col[0], col[1]] for col in row
                        ] for row in self.data
                    ]).astype(np.uint8)
                self.data = grayscale_alpha_to_rgba
            else: ## should not be met, due to previous check
                raise InvalidImageException(
                    "Image does not conform to supported standards. Only "
                    "grayscale[a] or RGB[A] supported."
                )
        return self

    def _strip_a(self, warn=False):
        """
        Strip an existing alpha channel if it has one.

        Warnings about losing transparency can be switched on setting `warn` to
        `True`.
        """
        dim = len(self.data.shape)

        assert dim==2 or dim==3, "Only grayscale(a), RGB, or RGBA supported."

        if dim == 2: ## grayscale, i.e. dim = row x column, i.e. no alpha!
            return self
        elif dim == 3: ## dim = row x column x pixel with pixel: RGB(A)/grayA
            if self.data.shape[-1] == 3: ## RGB case, i.e. no alpha channel
                return self
            elif self.data.shape[-1] == 4: ## RGBA case, i.e. alpha here
                if warn and any(alpha != 255 for alpha in
                        [col_a for row in self.data[:,:,3] for col_a in row]):
                    if not _yn_prompt("Warning!\nLoss of transparency when "
                            "stripping alpha channel. Continue?", 'n'):
                        return self
                    else: ## user chose to lose transparency
                        rgb_only = np.array([
                                [[col[0], col[1], col[2]] for col in row
                                ] for row in self.data
                            ]).astype(np.uint8)
                        self.data = rgb_only
                else: ## all alpha 255 and/or warning is off
                    rgb_only = np.array([
                            [[col[0], col[1], col[2]] for col in row
                            ] for row in self.data
                        ]).astype(np.uint8)
                    self.data = rgb_only
            elif self.data.shape[-1] == 2: ## grayscale with alpha channel case
                if warn and any(alpha != 255 for alpha in
                        [col_a for row in self.data[:,:,1] for col_a in row]):
                    if not _yn_prompt("Warning!\nLoss of transparency when "
                            "stripping alpha channel. Continue?", 'n'):
                        return self
                    else: ## user chose to lose transparency
                        grayscale_only = np.array([
                                [col[0] for col in row] for row in self.data
                            ]).astype(np.uint8)
                        self.data = grayscale_only
                else: ## all alpha 255 and/or warning is off
                    grayscale_only = np.array([
                            [col[0] for col in row] for row in self.data
                        ]).astype(np.uint8)
                    self.data = grayscale_only
            else:
                raise Exception("Only grayscale(a), RGB, or RGBA supported.")
        return self

    def save(self, extension=None, savepath=None, savename=None,
            auto_rename=True):
        """
        Save current image as a file.

        Parameters:
        -----------
        `extension` (optional) : string (file extension/format)
            Format to be saved to, given as the file extension. If not speci-
            fied the source file format is used. In case the source format does
            not support (new) properties, such as alpha, invokes a warning.
        `savepath` (optional) : string (path for saving)
            Path of directory where the file should be saved. If not specified
            or specified path is invalid the source file's parent directory is
            used.
        `savename` (optional) : string (filename)
            Filename of the file to be saved. If not specified uses the source
            file's name. If this file exists already invokes a warning.
        `auto_rename` (optional) : boolean
            Choose whether the filename for saving should automatically be
            changed if the file exists already. By default set to True. If
            set set to False and the filename exists invokes a warning.

        Returns:
        --------
        Writes current image object as a file with the specified parameters to
        the disk.
        """
        ## supported file formats/extensions using transparency
        transp_ext = ['png', ]

        ## checks concerning the new image format
        if extension is None:
            extension = self.ext
        removed_leading_dot = False
        if extension[0] == '.':
            removed_leading_dot = True
            extension = extension[1:]
        if (len(self.data.shape)==3 and self.data.shape[-1]==4
            and extension not in transp_ext
            ):
            ## RGBA but extension would not support transparency
            if any(alpha != 255 for alpha in
                    [col_a for row in self.data[:,:,3] for col_a in row]):
                ## above conditions + at least one alpha value is not 255
                if _yn_prompt("Warning!\nThe image contains transparency "
                        "properties which are not compatible with the "
                        "current format '{}'.\nDo you want to change the "
                        "format to 'png'?".format(extension), 'y'):
                    extension = 'png'
                else:
                    ## user chose non-transp. format, thus strip alpha
                    self._strip_a(warn=False)
            else:
                ## above conditions, but all alpha 255, thus strip alpha
                self._strip_a(warn=True) ## warning should never occur
        elif (len(self.data.shape)==3 and self.data.shape[-1]==2
              and extension not in transp_ext
              ):
            ## grayscale with alpha but extension would not support alpha
            if any(alpha != 255 for alpha in
                    [val_a for row in self.data[:,:,1] for val_a in row]):
                ## above conditions + at least one alpha value is not 255
                if _yn_prompt("Warning!\nThe image contains transparency "
                        "properties which are not compatible with the "
                        "current format '{}'.\nDo you want to change the "
                        "format to 'png'?".format(extension), 'y'):
                    extension = 'png'
                else:
                    ## user chose non-transp. format, thus strip alpha
                    self._strip_a(warn=False)
            else:
                ## above conditions, but all alpha 255, thus strip alpha
                self._strip_a(warn=True) ## warning should never occur
        else:
            ## not a known transparency format, so hopefully no problem
            pass
        ## append leading dot (was removed above if existing earlier)
        if removed_leading_dot:
            extension = "." + extension

        ## checks concerning the savepath
        sp_flag = True ## assume `savepath` is set
        if savepath is None:
            savepath = self.path
            sp_flag = False ## `savepath` is not set by the user
        if not os.path.isdir(savepath):
            if sp_flag:
                print("Warning!\nThe specified path for saving does not "
                    "exist.\nUsing the path of the source file instead.")
                savepath = self.path
            else: ## path of the source file does not exist anymore
                raise IOError("Path for saving does not exist anymore!")
        ## adjust path, in case it is a relative path
        savepath = os.path.abspath(savepath)

        def quick_renamer(savepath, savename, extension):
            """ Find a filename for a non-existing file. """
            nc = 1 ## name counter
            while True:
                temp_name = savename + "_{}".format(nc)
                if os.path.isfile(os.path.join(savepath, temp_name+extension)):
                    nc += 1
                    continue
                else:
                    return temp_name

        ## checks concerning the filename
        if savename is None:
            savename = self.name
        if savename.rsplit('.', 1)[-1] == extension[1:]:
            savename = savename.rsplit('.', 1)[0]
        if os.path.isfile(os.path.join(savepath, savename+extension)):
            if not auto_rename and not _yn_prompt("Warning!\nFile '{}' "
                    "exists already.\nDo you want to overwrite it?"
                    .format(savename+extension), 'n'):
                savename = quick_renamer(savepath, savename, extension)
            else:
                savename = quick_renamer(savepath, savename, extension)
                print("File exists already. Using filename '{}' instead."
                    .format(savename + extension))

        ## saving the data as an image file
        fullsave = os.path.join(savepath, savename+extension)
        imageio.imwrite(fullsave, self.data)
        print("Success. Wrote '{}' to disk.".format(fullsave))
        return self

    def grayscale(self, factor=1.0, method='luminosity'):
        """
        Convert input image data to grayscale.

        Possibility to choose a grayscaling factor and whether luminosity
        should be preserved or not.

        Parameters:
        -----------
        `factor` (optional) : float (must be in range `[0, 1]`)
            A factor corresponding to the amount of grayscaling, i.e. 1. trans-
            lates to full grayscale while 0. does not change anything. By de-
            fault the image is completely grayscaled.
        `method` (optional) : `'luminosity'` or `'average'`
            'luminosity' (default) preserves the luminosity of the image, while
            'average' neglects different color contributions and simply takes
            the average, usually distorting the perceived brightness.
        """
        ## initial checks and definitions to prepare calculations
        if factor == 0.:
            return self
        if factor<0. or factor>1.:
            raise InvalidParameterException(
                "Factor for grayscaling out of range [0, 1]"
                )
        if not (method=='luminosity' or method=='average'):
            raise InvalidParameterException(
                "Method for grayscaling must be 'luminosity' or 'average'."
            )

        if method == 'luminosity':
            def _meth(r, g, b):
                return 0.299*r + 0.587*g + 0.114*b
        else:
            def _meth(r, g, b):
                return (1./3.)*r + (1./3.)*g + (1./3.)*b
        def _graysc_r(r, g, b):
            return (1.-factor)*r + factor*_meth(r, g, b)
        def _graysc_g(r, g, b):
            return (1.-factor)*g + factor*_meth(r, g, b)
        def _graysc_b(r, g, b):
            return (1.-factor)*b + factor*_meth(r, g, b)
        self._uint8()._rgba()

        ## adjust grayscale according to parameters
        self.data = np.array([
                [   [
                    _graysc_r(col[0], col[1], col[2]),
                    _graysc_g(col[0], col[1], col[2]),
                    _graysc_b(col[0], col[1], col[2]),
                    col[3]
                    ] for col in row
                ] for row in self.data
            ]).astype(np.uint8)

        return self

    def grayscale_to_transp(self, color='white', check_grayscale=True,
            leave_alpha=False, c=None, cgs=None, la=None):
        """
        Adjust a grayscale image's alpha channel to its brightness' proportion.

        Use either the amount of white or black in a grayscale image to adjust
        its alpha channel accordingly. It is possible to leave existing trans-
        parency values as they are.

        Parameters:
        -----------
        `color`/`c` (optional) : [`'w'`, `'white'`] / [`'b'`, `'black'`]
            Choose the color being used as a reference for the conversion of
            the transparency. Default is 'white'/'w'. The other possibility is
            'black'/'b'.
        `check_grayscale`/`cgs` (optional) : boolean
            By default it is checked whether the image is already grayscale or
            not. For performance reasons it is possible to switch this function
            off. However, then it is assumed that the image is grayscale and
            only the red channel is used furthermore.
        `leave_alpha`/`la` (optional) : boolean
            Choose whether to leave the alpha value of a pixel untouched in
            case it is not fully opaque. By default, i.e. False, the alpha
            value will still be changed, regardless of previous transparency.
        """
        ## check input data validity
        dim = len(self.data.shape)
        assert dim==2 or dim==3, "Only grayscale(a), RGB, or RGBA supported."

        ## tend to alternative argument names
        if c is None:
            c = color
        if cgs is None:
            cgs = check_grayscale
        if la is None:
            la = leave_alpha

        ## check argument validity
        if not c in ['w', 'white', 'b', 'black']:
            raise InvalidParameterException("Invalid color parameter.")
        if c == 'white':
            c = 'w'
        elif c == 'black':
            c = 'b'

        ## ensure uint8 format
        self._uint8()

        ## check_grayscale
        if check_grayscale and dim == 3: ## dim == 2 is by definition grayscale
            px_dim = self.data.shape[-1] ## each pixel's structure
            if px_dim == 4 or px_dim == 3: ## RGBA or RGB
                ## px_dim == 2 is grayscale with alpha, i.e. no need to check
                dim_row, dim_col = len(self.data), len(self.data[0])
                found_color = False
                i = 0
                while i < dim_row:
                    j = 0
                    while j < dim_col:
                        if not (self.data[i,j,0] == self.data[i,j,1]
                                == self.data[i,j,2]):
                            found_color = True
                            break
                        else:
                            j += 1
                    if found_color:
                        break
                    else:
                        i += 1
                if found_color and not _yn_prompt("Warning!\nThe image data "
                        "do not correspond to a grayscale image.\nResults "
                        "will be grayscaled and transparent based on the "
                        "red channel only.\nDo you still want to continue?",
                        'n'):
                    return self

        ## use RGBA format (did not do this before as check_grayscale might be
        ## faster for other formats)
        self._rgba()

        ## define method based on specified parameters (cf. comment below)
        if c == 'w':
            if la:
                def _newpix(pix):
                    if pix[3] != 255:
                        return [pix[0], pix[0], pix[0], pix[3]]
                    else:
                        return [pix[0], pix[0], pix[0], 255-pix[0]]
            else: ## la == False
                def _newpix(pix):
                    if int(pix[3])-int(pix[0]) < 0:
                        return [pix[0], pix[0], pix[0], 0]
                    else:
                        return [pix[0], pix[0], pix[0], pix[3]-pix[0]]
        else: ## c == 'b'
            if la:
                def _newpix(pix):
                    if pix[3] != 255:
                        return [pix[0], pix[0], pix[0], pix[3]]
                    else:
                        return [pix[0], pix[0], pix[0], pix[0]]
            else: ## la == False
                def _newpix(pix):
                            if int(pix[3])-255+int(pix[0]) < 0:
                                return [pix[0], pix[0], pix[0], 0]
                            else:
                                return [pix[0], pix[0], pix[0],
                                        pix[3]-255+pix[0]]

        ## a more comprehensive version of the code above, but this here always
        ## checks the specified parameters, i.e., the upper definition should
        ## be more favorable
        #def _new_pix(pix, c, la):
        #    if c == 'w':
        #        if la:
        #            if pix[3] != 255:
        #                return [pix[0], pix[0], pix[0], pix[3]]
        #            else: ## pix[3] == 255
        #                ## 255-pix[0] is the same as pix[3]-pix[0]
        #                return [pix[0], pix[0], pix[0], 255-pix[0]]
        #        else: ## la == False
        #            new_alpha = pix[3] - pix[0]
        #            if new_alpha < 0:
        #                return [pix[0], pix[0], pix[0], 0]
        #            else: ## pix[3]-pix[0] >= 0
        #                return [pix[0], pix[0], pix[0], new_alpha]
        #    else: # c == 'b'
        #        if la:
        #            if pix[3] != 255:
        #                return [pix[0], pix[0], pix[0], pix[3]]
        #            else: ## pix[3] == 255
        #                return [pix[0], pix[0], pix[0], pix[0]]
        #        else: ## la == False
        #            new_alpha = pix[3] - 255 + pix[0]
        #            if new_alpha < 0:
        #                return [pix[0], pix[0], pix[0], 0]
        #            else: ## pix[3]-(255-pix[0]) >= 0
        #                return [pix[0], pix[0], pix[0], new_alpha]

        ## convert grayscale to transparent
        self.data = np.array([
                [_newpix(col) for col in row] for row in self.data
            ]).astype(np.uint8)

        return self


if __name__ == "__main__":
    pass

    ## NOTE - Known Issues with JPEG/JPG Images:
    '''
    ## Handling the colors of JPEG/JPG images does not work as expected. This
    ## might be related to the YUV420/422/444 format associated with these
    ## filetypes, instead of RGBA which is used for PNGs.
    '''

    ## NOTE - Regarding Performance Enhancements:
    '''
    ## More efficient handling of the data (i.e., making better use of numpy)
    ## can be done similar to this example from the imageio docs:
    ## <url>
    ##  https://imageio.readthedocs.io/en/stable/examples.html
    ##  #convert-a-short-movie-to-grayscale
    ## </url>
    ## This is not implemented (yet), due to the proof-of-concept status.
    '''

    ## input images for testing purposes
    # filename = './test_imgs/blackwhitetransp.png' # test `leave_alpha`
    # filename = './test_imgs/test.color.jpg' # colors as jpg
    # filename = './test_imgs/test.rgba.png' # colors as png
    filename = './test_imgs/flames_YUV420_90q.jpg' # actual test image

    testfile = Img(filename)

    ## some grayscaling tests
    # testfile.grayscale().save() # grayscaling with default parameters
    # testfile.grayscale(method='average').save() # average grayscaling
    # testfile.grayscale(factor=0.).save(extension='png') # no grayscaling
    # testfile.grayscale(factor=0.5).save() # 50% grayscaling
    # testfile.grayscale(factor=0.5).save(extension='png') # 50% grayscaling

    ## tests for the concept of turning grayscale brightness into transparency
    ## convert to transparent, but leave any previously transparent pixels
    # testfile.grayscale().grayscale_to_transp(leave_alpha=True).save()
    ## same as the line above, but use black as a reference for transparency
    # testfile.grayscale().grayscale_to_transp(c='b', leave_alpha=True).save()

    ## convert to transparent using default parameters
    # testfile.grayscale().grayscale_to_transp().save()
    ## same as above, but use black as a reference for transparency
    testfile.grayscale().grayscale_to_transp(c='b').save()
