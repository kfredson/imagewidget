from PyQt4.QtGui import *
from PyQt4.QtCore import *
import os
from PIL import Image


class CustomWidget(QLabel):

    def __init__(self, window, directory, targetImageArea):
        QLabel.__init__(self,window)
        self.buttonDown = False
        self.initialPoint = None
        self.currentPoint = None
        self.directory = directory
        self.targetImageArea = targetImageArea

        dirList = os.listdir(directory)
        self.fileList = []
        for x in sorted(dirList):
            if x[-3:].lower()=='jpg':
                self.fileList.append(x)
        if len(self.fileList)==0:
            exit()

        self.currentFile = 0
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
            self.display()

    def previous(self):
        if self.currentFile > 0:
            self.currentFile -= 1
            self.display()

    def save(self):
        img = Image.open(self.directory+'/'+self.fileList[self.currentFile])

    def cropandsave(self):

    def display(self):
        self.basePixmap = QPixmap(self.directory+'/'+self.fileList[self.currentFile])
        w = self.basePixmap.width()
        h = self.basePixmap.height()
        targetHeight = min(800,h)
        targetWidth = min(1500,w)
        self.basePixmap = self.basePixmap.scaled(targetWidth,targetHeight,Qt.KeepAspectRatio)
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
        
        self.graphicsWidget = CustomWidget(self, directory)
        
        b1 = QPushButton("&Next")
        b1.clicked.connect(self.graphicsWidget.advance)
        b2 = QPushButton("&Previous")
        b2.clicked.connect(self.graphicsWidget.previous)
        b3 = QPushButton("&Save")
        b3.clicked.connect(self.graphicsWidget.save)
        b4 = QPushButton("&Crop and Save")
        b3.clicked.connect(self.graphicsWidget.cropandsave)
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
    win = Window('/home/karl')
    win.show()
    sys.exit(app.exec_())
