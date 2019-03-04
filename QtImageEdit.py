from PyQt4.QtGui import *
from PyQt4.QtCore import *
import os, math
from PIL import Image, ExifTags


#get image orientation from exif metadata
def getRotationFromImage(filepath):
    try:
        image=Image.open(filepath)
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation]=='Orientation':
                break
        exif=dict(image._getexif().items())
        image.close()

        print exif[orientation]

        if exif[orientation] == 3:
            return 180
        elif exif[orientation] == 6:
            return 270
        elif exif[orientation] == 8:
            return -90
        else:
            return 0

    except (AttributeError, KeyError, IndexError):
        # cases: image don't have getexif
        return 0

class CustomWidget(QLabel):

    def __init__(self, window, directory, targetImageArea):
        QLabel.__init__(self,window)
        self.buttonDown = False
        self.initialPoint = None
        self.currentPoint = None
        self.directory = directory
        self.targetImageArea = targetImageArea
        self.currentRotation = 0
        self.parentWindow = window

        dirList = os.listdir(directory)
        self.fileList = []
        for x in sorted(dirList):
            if x[-3:].lower()=='jpg':
                self.fileList.append(x)
        if len(self.fileList)==0:
            print "No .JPG files found in directory"
            exit()

        self.currentFile = 0
        self.parentWindow.setWindowTitle(self.fileList[self.currentFile])
        self.display()

    #def paintEvent(self, qPaintEvent):
    #    print "calling super paint"
    #    QLabel.paintEvent(self,qPaintEvent)
    #    print "done super paint"
    #    if self.buttonDown:
    #        print "painting"
    #        painter = QPainter(self.pixmap())
    #        painter.setPen(QColor(Qt.black))
    #        painter.drawRect(self.initialPoint[0],self.initialPoint[1],self.currentPoint[0]-self.initialPoint[0],
    #                                      self.currentPoint[1]-self.initialPoint[1])
        

    def advance(self):
        if self.currentFile < len(self.fileList)-1:
            self.currentFile += 1
            self.parentWindow.setWindowTitle(self.fileList[self.currentFile])
            self.display()

    def previous(self):
        if self.currentFile > 0:
            self.currentFile -= 1
            self.parentWindow.setWindowTitle(self.fileList[self.currentFile])
            self.display()

    #Create 'imagewidget' directory in current directory if it doesn't exist, then save image
    def writeImageToDir(self,img,exif):
        print ("Saving to: "+self.directory+'/imagewidget/'+self.fileList[self.currentFile])
        if not os.path.exists(self.directory+'/imagewidget'):
                os.makedirs(self.directory+'/imagewidget')
        img.save(self.directory+'/imagewidget/'+self.fileList[self.currentFile],exif=exif)

    def save(self):
        img = Image.open(self.directory+'/'+self.fileList[self.currentFile])
        exif = img.info['exif']

        scaleFactor = max(1,math.sqrt(img.size[0]*img.size[1]/self.targetImageArea))
        if scaleFactor > 1:
            newImg = img.resize([img.size[0]/scaleFactor,img.size[1]/scaleFactor],
                            resample=Image.BICUBIC)
            self.writeImageToDir(newImg,exif)
        else:
            self.writeImageToDir(img,exif)

        img.close()

    def cropandsave(self):
        if self.initialPoint==None or self.currentPoint==None:
            print "No bounding box specified for crop!"
            return
        img_raw = Image.open(self.directory+'/'+self.fileList[self.currentFile])
        exif = img_raw.info['exif']
        img = img_raw.rotate(-1*self.currentRotation, expand=True)
        
        cScaleFactor = float(img.size[0])/float(self.width())
        cropBox = [cScaleFactor*self.initialPoint[0],cScaleFactor*self.initialPoint[1],cScaleFactor*self.currentPoint[0],
                   cScaleFactor*self.currentPoint[1]]
        newImg1 = img.crop(box=cropBox)
        scaleFactor = max(1,math.sqrt(newImg1.size[0]*newImg1.size[1]/self.targetImageArea))
        if scaleFactor > 1:
            newImg2 = newImg1.resize([newImg1.size[0]/scaleFactor,newImg1.size[1]/scaleFactor],
                            resample=Image.BICUBIC)
            self.writeImageToDir(newImg2.rotate(self.currentRotation),exif)
        else:
            self.writeImageToDir(newImg1.rotate(self.currentRotation),exif)

        img_raw.close()


    def display(self):
        self.currentRotation = getRotationFromImage(self.directory+'/'+self.fileList[self.currentFile])
        self.basePixmap = QPixmap(self.directory+'/'+self.fileList[self.currentFile])
        w = self.basePixmap.width()
        h = self.basePixmap.height()
        targetHeight = min(800,h)
        targetWidth = min(1500,w)
        self.basePixmap = self.basePixmap.transformed(QTransform().rotate(self.currentRotation)).scaled(
            targetWidth,targetHeight,Qt.KeepAspectRatio)
        self.setPixmap(self.basePixmap)


    def mousePressEvent(self, event):
        #print "mousepress"
        self.buttonDown = True
        self.initialPoint = [event.pos().x(), event.pos().y()]
        self.currentPoint = [event.pos().x(), event.pos().y()]

    def mouseReleaseEvent(self, event):
        #print "mouserelease" 
        self.buttonDown = False

    def mouseMoveEvent(self, event):
        self.currentPoint = [event.pos().x(), event.pos().y()]
        #print self.initialPoint
        #print self.currentPoint
        self.setPixmap(self.basePixmap)
        painter = QPainter(self.pixmap())
        painter.setCompositionMode(QPainter.CompositionMode_Difference)
        painter.setPen(QColor(Qt.white))
        painter.drawRect(self.initialPoint[0],self.initialPoint[1],self.currentPoint[0]-self.initialPoint[0],
                                          self.currentPoint[1]-self.initialPoint[1])
        self.repaint()

    
        
class Window(QMainWindow):

    def __init__(self, directory):
        QMainWindow.__init__(self)
        self.widget = QWidget(self)
        layout = QBoxLayout(QBoxLayout.TopToBottom)
        layout.setSizeConstraint(QLayout.SetFixedSize)
        self.widget.setLayout(layout)
        buttonWidget = QWidget(self)
        buttonLayout = QBoxLayout(QBoxLayout.LeftToRight)
        buttonWidget.setLayout(buttonLayout)
        
        self.graphicsWidget = CustomWidget(self, directory, 6000000)
        
        b1 = QPushButton("&Next")
        b1.clicked.connect(self.graphicsWidget.advance)
        b2 = QPushButton("&Previous")
        b2.clicked.connect(self.graphicsWidget.previous)
        b3 = QPushButton("&Save")
        b3.clicked.connect(self.graphicsWidget.save)
        b4 = QPushButton("&Crop and Save")
        b4.clicked.connect(self.graphicsWidget.cropandsave)
        buttonLayout.addWidget(b3)
        buttonLayout.addWidget(b4)
        buttonLayout.addWidget(b1)
        buttonLayout.addWidget(b2)
        layout.addWidget(buttonWidget)
        layout.addWidget(self.graphicsWidget)

        self.setCentralWidget(self.widget)
        self.layout().setSizeConstraint(QLayout.SetFixedSize)
        #self.resize(pixmap.width(),pixmap.height())

if __name__ == '__main__':

    import sys
    app = QApplication(sys.argv)
    win = Window('/home/karl/171___09')
    win.show()
    sys.exit(app.exec_())
