from PyQt5 import QtCore, QtGui, QtWidgets
import cv2
import os


class ImageViewerWidget(QtWidgets.QLabel, object):
    def __init__(self, parent=None):
        #calling base initializers
        super(ImageViewerWidget, self).__init__()

        #necessary and don't know why
        self.resize(parent.size())

        # QImage for the QtWidget
        self.qimage = None

        # numpy image array
        self.image_array = None

        # image name
        self.image_name = None

        # image path
        self.image_path = None

        self.border_pen = QtGui.QPen(QtGui.QColor.fromRgb(100, 100, 100))
        self.border_pen.setStyle(QtCore.Qt.DashLine)

        self.border_brush = QtCore.Qt.NoBrush

        self.context_menu = None

        #setting the context menu
        self.__setContextMenu()

    #----------------------------Properties------------------------------

    def getBorderPen(self):
        return self.border_pen

    def setBorderPen(self, value):
        self.border_pen = value

    def getImage(self):
        return self.qimage

    def getImageData(self):
        return self.image_array

    def setImageData(self, img_data):
        if img_data is None:
            return

        # grayscale image
        if len(img_data.shape) == 2:
            height, width = img_data.shape
            format = QtGui.QImage.Format_Indexed8

        # multichannel image
        elif len(img_data.shape) == 3:
            height, width, _ = img_data.shape
            format = QtGui.QImage.Format_RGB888

        # format nor supported
        else:
            return

        # setting the image data
        self.image_array = img_data

        # setting the new qimage
        self.qimage = QtGui.QImage(img_data.data, width, height, format)

        # resizing the image viewer widget
        self.setFixedSize(QtCore.QSize(self.qimage.width(), self.qimage.height()))

    def getImageName(self):
        return self.image_name

    def setImageName(self, value):
        if value is not None:
            self.image_name = value

    #------------------------------Methods-------------------------------

    def __setContextMenu(self):
        self.context_menu = QtWidgets.QMenu(self)

        # add a Save Image Action
        save_image_action = QtWidgets.QAction("Save &Image", self)
        save_image_action.triggered.connect(self.saveImage)
        self.context_menu.addAction(save_image_action)

    def loadImage(self):
        image_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Open Image",
            "./iris-images",
            "bmp files (*.bmp)\njpg files (*.jpg)\nAll files (*.*)",
            "All files (*.*)",
            options=QtWidgets.QFileDialog.DontUseNativeDialog
        )

        # if no image was selected
        if not image_path:
            return 0

        # loading image as numpy array in gray scale
        self.image_array = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)

        # if there was a problem loading the image
        if self.image_array is None:
            return 0

        # setting the qimage
        self.qimage = QtGui.QImage(image_path)

        # setting image path
        self.image_path = image_path

        # setting the image name
        _, file_name = os.path.split(image_path)
        image_name, _ = os.path.splitext(file_name)
        self.setImageName(image_name)

        # resizing the image viewer widget
        self.setFixedSize(QtCore.QSize(self.qimage.width(), self.qimage.height()))

        return 1

    def unloadImage(self):
        # reset image(s) and image path
        self.qimage = None
        self.image_array = None

        #resetting name
        self.image_name = ""

        #updating the widget
        self.update()

    def saveImage(self):
        image_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save Image",
            ".",
            "bmp files (*.bmp)\njpg files (*.jpg)\nAll files (*.*)",
            "All files (*.*)",
            options=QtWidgets.QFileDialog.DontUseNativeDialog
        )

        if not image_path:
            return False

        # save the image
        cv2.imwrite(image_path, self.image_array)
        return True

    #-------------------------Overrided methods--------------------------

    def paintEvent(self, QPaintEvent):
        #calling the paintEvent of parent
        super(ImageViewerWidget, self).paintEvent(QPaintEvent)

        qpainter = QtGui.QPainter(self)

        #drawing border rectangle
        border_rect = QtCore.QRect(0, 0, self.width() - 1, self.height() - 1)
        qpainter.setPen(self.border_pen)
        qpainter.setBrush(self.border_brush)
        qpainter.drawRect(border_rect)

        #image must be valid
        if self.qimage is not None:
            self.setPixmap(QtGui.QPixmap.fromImage(self.qimage))
        else:
            #setting an empty bitmap
            self.setPixmap(QtGui.QPixmap())

    def contextMenuEvent(self, QContextMenuEvent):
        #calling the contextMenuEvent of parent
        super(ImageViewerWidget, self).contextMenuEvent(QContextMenuEvent)

        #show menu if imaga is valid
        if self.qimage is not None:
            self.context_menu.exec_(self.mapToGlobal(QContextMenuEvent.pos()))
