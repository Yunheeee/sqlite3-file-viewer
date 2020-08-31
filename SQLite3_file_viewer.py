# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SQLite3_file_viewer'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!

try:
    import os,platform,sys,traceback
    import PyQt5
    from tkinter import Tk
    from tkinter.messagebox import showwarning
    from PyQt5.QtGui import *
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtPrintSupport import *
    from untitled import Ui_MainWindow
    from QHexTextEdit import QCodeEditor
    import qrc_resources
    import struct
    from graphviz import Digraph
    #from QimageWidget import ImageWithMouseControl

    #import qrc_images
    #import newimagedlg
    #import helpform
    #import resizedlg
except Exception as _err:
    Tk().withdraw()
    warn=showwarning("WARNING","WARNING Info:\n%s"%_err)

__version__="0.0.1"

class dataType():
    PAGE_LEAF_TYPE = 0
    PAGE_TRUNK_TYPE = 1
    FILE_HEADER_TYPE = 2
    PAGE_INFO_TYPE = 3
    CELL_INFO_TYPE = 4

class AppWindow(QMainWindow):
    def __init__(self, parent=None):
        super(AppWindow, self).__init__(parent)
        self.filename = None  #数据库文件名
        self.pageNum = 0
        self.pageCount = 0
        self.pageData = None
        self.pageSize = 1024 #正常是要从文件头中读取的，这里直接取默认吧
        self.dot = None

        self.textWidget = QCodeEditor()
        minWidth = self.textWidget.number_bar.fontMetrics().width('ffffffff    1234567812345678')
        minWidth += self.textWidget.fontMetrics().width('FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF ff')
        self.textWidget.setMinimumSize(minWidth, 200)  # 设置一个最小大小以防其不占用空间
        self.textWidget.setReadOnly(True)  #设置文本框只读
        #self.textWidget.setAlignment(Qt.AlignCenter)  # 对Lable中的各图片保持水平和垂直居中
        self.textWidget.setContextMenuPolicy(Qt.ActionsContextMenu)
        # 添加上下文菜单的一个最简单的方法是对需要添加上下文的部件声明一个上下文菜单策略，然后向
        # 该窗口部件中添加一些动作。
        self.setCentralWidget(self.textWidget)  # imageLabel添加到MWindow中充当中心部件窗口
        # QLabel可以显示各种类型的文本、图片。中心部件窗口是复合窗口部件。
        # setCentralWidght可以设置什么部件为主窗口，同时也可以重新定义一个部件的父对象，让父窗口掌控它。

        logDockWidgetFileHeader = QDockWidget("文件头", self)
        logDockWidgetFileHeader.setObjectName("LogDockFileHeader")
        # 让PyQt能够保存和回复停靠窗口部件的尺寸大小和位置。因为一个地方可能有多个停靠窗口部件，通过变量名区分。
        logDockWidgetFileHeader.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.tableWidgetFileHeader = QTableWidget(23, 1)
        # 设置根据窗口大小调整单元格大小
        self.tableWidgetFileHeader.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 设置只读模式
        self.tableWidgetFileHeader.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidgetFileHeader.setHorizontalHeaderLabels(['值'])
        self.tableWidgetFileHeader.setVerticalHeaderLabels(['头字符串', '页大小', '写版本', '读版本',
                                                  '页尾部保留空间','内部页单元最大空间','内部页单元最小空间',
                                                  '叶子页单元最小空间','文件修改次数','总页数','空闲页链表头指针',
                                                  '空闲页数量','schema版本号','未定义','默认页缓存大小','b-tree最大根页号',
                                                  '编码方式','用户版本号','是否启用incremental-vacuum','用户应用程序ID','保留空间','有效版本','数据库版本号'])
        logDockWidgetFileHeader.setWidget(self.tableWidgetFileHeader)
        self.addDockWidget(Qt.RightDockWidgetArea, logDockWidgetFileHeader)

        # 声明一个Dock组件，然后设置其父对象和标题名称，这样的话，当mainwindow被删除后，它也会被删除
        logDockWidgetPageHeader = QDockWidget("页头", self)
        # 设置此组件的ObjName
        logDockWidgetPageHeader.setObjectName("LogDockWidgetPageHeader")
        # 让PyQt能够保存和回复停靠窗口部件的尺寸大小和位置。因为一个地方可能有多个停靠窗口部件，通过变量名区分。
        logDockWidgetPageHeader.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        # 设置dock在mianwindow的停靠区域。
        # 使用setFeatures()方法来控制Dock的移动、浮动和关闭属性。

        # tableWidget，然后把它赋给logdockwidget
        self.tableWidgetPageHeader = QTableWidget(7,1)
        self.tableWidgetPageHeader.setHorizontalHeaderLabels(['值'])
        self.tableWidgetPageHeader.setVerticalHeaderLabels(['页类型', '首自由块偏移', '单元数', '单元内容起始偏移',
                                                  '碎片总字节','最右子页号','单元指针数组'])
        #设置根据窗口大小调整单元格大小
        self.tableWidgetPageHeader.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        #设置只读模式
        self.tableWidgetPageHeader.setEditTriggers(QAbstractItemView.NoEditTriggers)
        logDockWidgetPageHeader.setWidget(self.tableWidgetPageHeader)

        self.addDockWidget(Qt.RightDockWidgetArea, logDockWidgetPageHeader)
        # 将dockwidght设置为默认呈现在mainwindow的右边。

        # 声明一个Dock组件，然后设置其父对象和标题名称，这样的话，当mainwindow被删除后，它也会被删除
        logDockWidgetCell = QDockWidget("单元", self)
        # 设置此组件的ObjName
        logDockWidgetCell.setObjectName("LogDockWidgetCell")
        # 让PyQt能够保存和回复停靠窗口部件的尺寸大小和位置。因为一个地方可能有多个停靠窗口部件，通过变量名区分。
        logDockWidgetCell.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        # tableWidget，然后把它赋给logdockwidget
        self.tableWidgetCell = QTableWidget(100, 6)
        self.tableWidgetCell.setHorizontalHeaderLabels(['单元偏移','数据长度', 'Key', '左子页', '溢出页', 'payloadOffset'])
        #self.tableWidgetCell.setVerticalHeaderLabels(['有效数据长度', 'key rowid', '左子页指针', '首溢出页页码'])
        # 设置根据窗口大小调整单元格大小
        self.tableWidgetCell.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 设置只读模式
        self.tableWidgetCell.setEditTriggers(QAbstractItemView.NoEditTriggers)
        logDockWidgetCell.setWidget(self.tableWidgetCell)
        #单元格双击事件，显示payload内容
        self.tableWidgetCell.cellDoubleClicked.connect(self.cellClicke)

        self.addDockWidget(Qt.RightDockWidgetArea, logDockWidgetCell)
        # 将dockwidght设置为默认呈现在mainwindow的右边。

        logDockWidgetTree = QDockWidget("树图", self)
        logDockWidgetTree.setObjectName("LogDockTree")
        # 让PyQt能够保存和回复停靠窗口部件的尺寸大小和位置。因为一个地方可能有多个停靠窗口部件，通过变量名区分。
        logDockWidgetTree.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.tableWidgetTree = QLabel()
        self.scrollWidget = QScrollArea()
        '''la = QVBoxLayout()
        la.addWidget(self.tableWidgetTree)
        self.scrollWidget.setLayout(la)'''
        self.scrollWidget.setWidget(self.tableWidgetTree)
        self.scrollWidget.setAlignment(Qt.AlignLeft)#// 对齐
        self.scrollWidget.setWidgetResizable(True)#// 自动调整大小

        logDockWidgetTree.setWidget(self.scrollWidget)
        self.addDockWidget(Qt.RightDockWidgetArea, logDockWidgetTree)

        # 框架类型的设置
        status = self.statusBar()
        status.setSizeGripEnabled(False)
        #status.addPermanentWidget(self.sizeLabel)
        status.showMessage("Ready Go!", 5000)

        # 状态栏的永久提示
        self.tip1 = QLabel("    ")
        self.tip1.setStyleSheet("background-color:rgb(119, 136, 153)")
        self.tip2 = QLabel("文件头  ")
        self.tip3 = QLabel("    ")
        self.tip3.setStyleSheet("background-color:rgb(238,130,238)")
        self.tip4 = QLabel("页头  ")
        self.tip5 = QLabel("    ")
        self.tip5.setStyleSheet("background-color:rgb(32,178,170)")
        self.tip6 = QLabel("单元指针  ")
        self.tip7 = QLabel("    ")
        self.tip7.setStyleSheet("background-color:rgb(124,252,0)")
        self.tip8 = QLabel("单元内容  ")
        self.tip9 = QLabel("    ")
        self.tip9.setStyleSheet("background-color:rgb(255, 160, 122)")
        self.tip10 = QLabel("自由块  ")

        status.addPermanentWidget(self.tip1, stretch=0)
        status.addPermanentWidget(self.tip2, stretch=0)
        status.addPermanentWidget(self.tip3, stretch=0)
        status.addPermanentWidget(self.tip4, stretch=0)
        status.addPermanentWidget(self.tip5, stretch=0)
        status.addPermanentWidget(self.tip6, stretch=0)
        status.addPermanentWidget(self.tip7, stretch=0)
        status.addPermanentWidget(self.tip8, stretch=0)
        status.addPermanentWidget(self.tip9, stretch=0)
        status.addPermanentWidget(self.tip10, stretch=0)

        fileOpenAction = self.createAction("&Open...", self.fileOpen, QKeySequence.Open, "fileopen",
                                           "Open an existing file")
        fileCloseAction = self.createAction("&Close...", self.fileClose, None, "delete",
                                           "Close the opening file")
        findPageAction = self.createAction("&findPage...", self.findPage, None, "find",
                                           "Find wanted num page")
        btreeShowAction = self.createAction("&BtreeShow...", self.btreeShow, None, "flow_chart",
                                           "Show db Btree")
        pagePrevAction = self.createAction("&PrevPage...", self.prevPage, None, "prev",
                                            "Prev page")
        pageNextAction = self.createAction("&NextPage...", self.nextPage, None, "next",
                                            "Next page")

        '''self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenuActions = (fileOpenAction)
        self.fileMenu.aboutToShow.connect(self.updateFileMenu)'''

        fileToolbar = self.addToolBar("File")
        fileToolbar.setObjectName("FileToolBar")
        #self.addActions(fileToolbar, (fileOpenAction))

        fileToolbar.addAction(fileOpenAction)
        fileToolbar.addAction(fileCloseAction)
        fileToolbar.addAction(btreeShowAction)

        pageToolbar = self.addToolBar("Page")
        self.pageLabel = QLabel()
        self.pageLabel.setText("Page")
        self.pageInput = QLineEdit()
        self.pageInput.setMaximumWidth(50)
        self.pageInput.returnPressed.connect(self.findPage)
        pageToolbar.addAction(pagePrevAction)
        pageToolbar.addWidget(self.pageLabel)
        pageToolbar.addWidget(self.pageInput)
        pageToolbar.addAction(findPageAction)
        pageToolbar.addAction(pageNextAction)

    def cellClicke(self,row,col):
        item = self.tableWidgetCell.item(row,1)
        if(item):
            len = int(item.text())
        else:
            return

        item = self.tableWidgetCell.item(row, 0)
        if (item):
            cellOff = int(item.text(), 16)
        else:
            return

        item = self.tableWidgetCell.item(row, 5)
        if (item):
            payloadOff = int(item.text(), 16)
        else:
            return

        with open(self.filename, 'rb') as f:
            f.seek((self.pageNum - 1) * self.pageSize + cellOff + payloadOff, 0)
            buf = f.read(len)

        strBuf = ""
        # 解析有效数据
        dataArr = self.payloadFormat(buf)
        for each in dataArr:
            strBuf += str(each)
            strBuf += ","

        QMessageBox.warning(self, "单元内容:", strBuf)

    def createAction(self,text,slot=None,shortcut=None,icon=None,tip=None,
                    checkable=False,signal="triggered"):
            action=QAction(text,self)
            if icon is not None:
                    action.setIcon(QIcon(":/%s.png"%icon))
            if shortcut is not None:
                    action.setShortcut(shortcut)
            if tip is not None:
                    action.setToolTip(tip)
                    action.setStatusTip(tip)
            if slot is not None:
                    getattr(action,signal).connect(slot)
            # self.connect(action,SIGNAL(signal),slot) qt4中的信号方法
            if checkable:
                    action.setCheckable(True)
            return action

    def addActions(self,target,actions):
            for action in actions:
                    if action is None:
                            target.addSeparator()
                    else:
                            target.addAction(action)

    def updateFileMenu(self):
            self.fileMenu.clear()
            self.addActions(self.fileMenu,self.fileMenuActions[:-1])#不要quit
            current=(self.filename if self.filename is not None else None)
            recentFiles=[]
            for fname in self.recentFiles:
                    if fname != current and QFile.exists(fname):
                            recentFiles.append(fname)
            if recentFiles:
                    self.fileMenu.addSeparator()
                    for i,fname in enumerate(recentFiles):
                            action=QAction(QIcon(":/icon.png)"),"&%s %s"%(i+1,QFileInfo(fname).fileName()),self)
                            action.setData(QVariant(fname))
                            # action.triggered.connect(self.loadFile)
                            self.fileMenu.addAction(action)
                            action.triggered.connect(self.loadFile)
                    self.fileMenu.addSeparator()
                    self.fileMenu.addAction(self.fileMenuActions[-1])

    def findPage(self):

        num_str = self.pageInput.text()
        if (num_str == ""):
            return

        num = int(num_str)
        if (num > self.pageCount):
            QMessageBox.warning(self, "Tip:", "没那么多页！")
        else:
            self.pageNum = num
            self.loadFile(self.filename)
            self.pageInput.setText("%d" % (self.pageNum))

    def treeHandleCell(self, buf, pageNum, type, dot):
        STRUCT = "!H"
        cellPtrArr = []
        if (pageNum == 1):
            fileHdrOff = 100
        else:
            fileHdrOff = 0
        cellNum = struct.unpack(STRUCT, buf[fileHdrOff + 3:fileHdrOff + 5])[0]

        dotHead = "page%d"%(pageNum)
        dotCell = "{{<n>  Page%d } |{ " % (pageNum)
        if (cellNum <= 0):
            dotCell += "}}"
            dot.node(dotHead, dotCell)
            return

        # 内部页偏移为12
        if (type == 0x05 or type == 0x02):
            for i in range(0, cellNum):
                offset = fileHdrOff + 12 + i * 2
                cellPtrArr.append(struct.unpack(STRUCT, buf[offset:offset+2])[0])
                #print (i, cellPtrArr[i])
        elif  (type == 0x0d or type == 0x0a):
            for i in range(0, cellNum):
                offset = fileHdrOff + 8 + i * 2
                cellPtrArr.append(struct.unpack(STRUCT, buf[offset:offset+2])[0])
                #print (i, cellPtrArr[i])
        else:
            pass

        if (type == 0x0d):#b+tree叶子页
            dotCell = "{{<n>  Page%d B+ } |{ " % (pageNum)
            for i in range(0, cellNum):
                len, off1 = self.varintTrans(buf[cellPtrArr[i]:])
                offset = off1
                key, off1 = self.varintTrans(buf[cellPtrArr[i] + offset:])
                offset += off1
                if(i == 0):
                    dotCell += "<c%d> %d"%(i,key)
                else:
                    dotCell += "|<c%d> %d"%(i,key)
            dotCell += "}}"
            dot.node(dotHead, dotCell)


        elif(type == 0x05):#b+tree内部页
            dotCell = "{{<n>  Page%d B+ } |{ " % (pageNum)
            for i in range(0, cellNum):
                tmp = buf[cellPtrArr[i]:cellPtrArr[i] + 4]
                left = struct.unpack("!1I", tmp)[0]
                key, off = self.varintTrans(buf[cellPtrArr[i] + 4:])
                dot.edge("page%d:c%d"%(pageNum, i), "page%d:n"%(left))
                if (i == 0):
                    dotCell += "<c%d> %d" % (i, key)
                else:
                    dotCell += "|<c%d> %d" % (i, key)
            dotCell += "}}"
            dot.node(dotHead, dotCell)

        elif (type == 0x0a):#b-tree叶子页
            dotCell = "{{<n>  Page%d B } |{ " % (pageNum)
            for i in range(0, cellNum):
                len, off = self.varintTrans(buf[cellPtrArr[i]:])

            dotCell += "}}"
            dot.node(dotHead, dotCell)

        elif (type == 0x02):#b-tree内部页
            dotCell = "{{<n>  Page%d B } |{ " % (pageNum)
            for i in range(0, cellNum):
                left = struct.unpack("!I", buf[cellPtrArr[i]:cellPtrArr[i] + 4])[0]
                len, off = self.varintTrans(buf[cellPtrArr[i] + 4:])
                dot.edge("page%d:c%d" % (pageNum, i), "page%d:n" % (left))

            dotCell += "}}"
            dot.node(dotHead, dotCell)

        else:
            pass

    def treeOverViewPage(self, pageNum, dot):
        buf = ""
        PAGE_HEADER = '!1B3H1B1I'
        with open(self.filename, 'rb') as f:
            f.seek((pageNum - 1) * self.pageSize, 0)
            buf = f.read(self.pageSize)

        if (pageNum == 1):
            off = 100
            arr = struct.unpack('!16s1H6B19I', buf[:100])
            freePageHeader = arr[10]
            freePageCount = arr[11]
        else:
            off = 0

        pageType = struct.unpack(PAGE_HEADER, buf[off:off+12])[0]

        self.treeHandleCell(buf, pageNum, pageType, dot)


    def btreeShow(self):
        if(self.filename == None):
            return

        dot = Digraph('test', node_attr={"shape": "record"}, format='png')
        #
        #dot.attr(autosize = false, radio = 1.25)
        '''
        dot.node("page1", "{{<n> Page 1} | {<c1> 3  |<c2> 5 |<c3> 8}}")
        dot.node("page6", "{{<num> Page 6} | {<c1> 1  |<c2> 2 |<c3> 3}}")
        dot.node("page7", "{{<num> Page 7} | {<c1> 4  |<c2> 5 }}")
        dot.node("page10", "{{<num> Page 10} | {<c1> 6  |<c2> 7 |<c3> 8}}}")
        dot.edge('page1:c1', 'page6:n')
        dot.edge('page1:c2', 'page7:n')
        dot.edge('page1:c3', 'page10:n')
        '''

        for i in range(1, self.pageCount + 1):
            self.treeOverViewPage(i, dot)

        #print (dot.source)
        img = QImage.fromData(dot.pipe())
        #self.tableWidgetTree.setScaledContents(True)
        #scale_img = img.scaled(self.tableWidgetTree.size(), Qt.KeepAspectRatio)
        self.tableWidgetTree.setPixmap(QPixmap.fromImage(img))

        """
        for i in range(0, self.pageCount):
            with open(self.filename, 'rb') as f:
                f.seek(i * self.pageSize, 0)
                buf = f.read(self.pageSize)
            
            if(buf == None):
                self.showbug()
                return"""



    def nextPage(self):
        if(self.pageNum < self.pageCount):
            self.pageNum += 1
            self.loadFile(self.filename)
            self.pageInput.setText("%d" % (self.pageNum))
        else:
            QMessageBox.warning(self, "Tip:", "已到达最后页！")

    def prevPage(self):
        if(self.pageNum <= 1):
            QMessageBox.warning(self,"Tip:","已到达最前页！")
        else:
            self.pageNum -= 1
            self.loadFile(self.filename)
            self.pageInput.setText("%d" % (self.pageNum))

    def transOffset(self, off, len):
        line = off // 16
        remain = off % 16
        start = line * 49 + remain * 3

        line = (off + len) // 16
        remain = (off + len)  % 16
        end = line * 49 + remain * 3

        #print (start,end)
        return start,end

    def addTableItem(self, type, row, col, value):
        try:
            newItem = QTableWidgetItem(value)
        except:
            self.showbug()
        if(type == dataType.FILE_HEADER_TYPE):
            self.tableWidgetFileHeader.setItem(row, col, newItem)
        elif(type == dataType.PAGE_INFO_TYPE):
            self.tableWidgetPageHeader.setItem(row, col, newItem)
        elif(type == dataType.CELL_INFO_TYPE):
            self.tableWidgetCell.setItem(row, col, newItem)
        else:
            pass

    def handleFileHeader(self):
        # 清空
        self.tableWidgetFileHeader.clearContents()

        FILE_HEADER_STRUCT = '!16s1H6B19I'  # !代表网络字节序，二进制读取文件需注意
        with open(self.filename, 'rb') as f:
            f.seek(0, 0)
            buf = f.read(100)
            if (buf != None):
                arr = struct.unpack(FILE_HEADER_STRUCT, buf)
                self.pageSize = arr[1]
                self.pageCount = arr[9]
                self.addTableItem(dataType.FILE_HEADER_TYPE, 0, 0, arr[0].decode('utf-8'))
                self.addTableItem(dataType.FILE_HEADER_TYPE, 1, 0, "%d"%(arr[1]))
                self.addTableItem(dataType.FILE_HEADER_TYPE, 2, 0, "%d (大于1代表只读)" % (arr[2]))
                self.addTableItem(dataType.FILE_HEADER_TYPE, 3, 0, "%d (大于1代表文件格式错)" % (arr[3]))
                self.addTableItem(dataType.FILE_HEADER_TYPE, 4, 0, "%d" % (arr[4]))
                if(arr[5] == 0x40):
                    self.addTableItem(dataType.FILE_HEADER_TYPE, 5, 0, "25%")
                else:
                    self.addTableItem(dataType.FILE_HEADER_TYPE, 5, 0, "%d" % (arr[5]))

                if (arr[6] == 0x20):
                    self.addTableItem(dataType.FILE_HEADER_TYPE, 6, 0, "12.5%")
                else:
                    self.addTableItem(dataType.FILE_HEADER_TYPE, 6, 0, "%d" % (arr[6]))

                if (arr[7] == 0x20):
                    self.addTableItem(dataType.FILE_HEADER_TYPE, 7, 0, "12.5%")
                else:
                    self.addTableItem(dataType.FILE_HEADER_TYPE, 7, 0, "%d" % (arr[7]))

                self.addTableItem(dataType.FILE_HEADER_TYPE, 8, 0, "%d" % (arr[8]))
                self.addTableItem(dataType.FILE_HEADER_TYPE, 9, 0, "%d" % (arr[9]))
                self.pageCount = arr[9]
                self.addTableItem(dataType.FILE_HEADER_TYPE, 10, 0, "%d" % (arr[10]))
                self.addTableItem(dataType.FILE_HEADER_TYPE, 11, 0, "%d" % (arr[11]))
                self.addTableItem(dataType.FILE_HEADER_TYPE, 12, 0, "%d" % (arr[12]))
                self.addTableItem(dataType.FILE_HEADER_TYPE, 13, 0, "%d" % (arr[13]))
                self.addTableItem(dataType.FILE_HEADER_TYPE, 14, 0, "%d" % (arr[14]))
                self.addTableItem(dataType.FILE_HEADER_TYPE, 15, 0, "%d" % (arr[15]))
                if(arr[16] == 1):
                    self.addTableItem(dataType.FILE_HEADER_TYPE, 16, 0, "utf-8")
                elif(arr[16] == 2):
                    self.addTableItem(dataType.FILE_HEADER_TYPE, 16, 0, "utf-16le")
                elif (arr[16] == 3):
                    self.addTableItem(dataType.FILE_HEADER_TYPE, 16, 0, "utf-16be")

                self.addTableItem(dataType.FILE_HEADER_TYPE, 17, 0, "%d" % (arr[17]))
                self.addTableItem(dataType.FILE_HEADER_TYPE, 18, 0, "%d" % (arr[18]))
                self.addTableItem(dataType.FILE_HEADER_TYPE, 19, 0, "%d" % (arr[19]))
                self.addTableItem(dataType.FILE_HEADER_TYPE, 20, 0, "%d" % (arr[20]))
                self.addTableItem(dataType.FILE_HEADER_TYPE, 21, 0,"%d" % (arr[21]))
                self.addTableItem(dataType.FILE_HEADER_TYPE, 22, 0, "%d" % (arr[22]))
            else:
                self.showbug()

    def nByteNum(self, buf, bytes):
        a = 0
        for i in range(0,bytes):
            a = a << 8 + buf[i]
        return a

    def varintTrans(self, buf):
        a = 0
        for i in range(1, 10):
            b = buf[i - 1]
            if(0x80 & b == 0):
                a = (a << 7) + b
                break
            else:
                b &= ~0x80
                a = (a << 7) + b

        return a, i

    def payloadFormat(self, payload):
        #先取出header_size，表示标头总字节
        header_size, off1 = self.varintTrans(payload)
        offset = off1
        typeArr = []
        dataArr = []

        #填充类型列表
        while (offset < header_size):
            type, off1 = self.varintTrans(payload[offset:])
            typeArr.append(type)
            offset += off1

        for type in typeArr:
            if(type == 0):
                dataArr.append('NULL')
            elif(type >= 1 and type <= 4):
                dataArr.append(self.nByteNum(payload[offset:], type))
                offset += type
            elif(type == 5):
                dataArr.append(self.nByteNum(payload[offset:], 6))
                offset += 6
            elif(type == 6):
                dataArr.append(self.nByteNum(payload[offset:], 8))
                offset += 8
            elif(type == 7):
                STRUCT = "!1d"
                dataArr.append(struct.unpack(STRUCT, payload[offset:offset+8])[0])
                offset += 8
            elif (type == 8):
                dataArr.append(0)
            elif (type == 9):
                dataArr.append(1)
            elif((type % 2 == 0) and type > 12):
                dataArr.append(payload[offset:offset+((type-12)//2)])
                offset += (type-12)//2
            elif((type % 2 == 1) and type > 13):
                textLen = ((type - 13) // 2)
                str_buf = payload[offset:offset + textLen]
                str_buf.decode('utf-8')
                dataArr.append(str_buf.decode('utf-8'))
                offset += textLen
                #print(str_buf.decode('utf-8'))
            else:
                pass

        return dataArr

    def handleCellHeader(self, buf, type):
        STRUCT = "!H"
        cellPtrArr = []
        if (self.pageNum == 1):
            fileHdrOff = 100
        else:
            fileHdrOff = 0
        cellNum = struct.unpack(STRUCT, buf[fileHdrOff + 3:fileHdrOff + 5])[0]

        if (cellNum <= 0):
            return

        # 内部页偏移为12
        if (type == 0x05 or type == 0x02):
            for i in range(0, cellNum):
                offset = fileHdrOff + 12 + i * 2
                cellPtrArr.append(struct.unpack(STRUCT, buf[offset:offset+2])[0])
                #print (i, cellPtrArr[i])
        elif  (type == 0x0d or type == 0x0a):
            for i in range(0, cellNum):
                offset = fileHdrOff + 8 + i * 2
                cellPtrArr.append(struct.unpack(STRUCT, buf[offset:offset+2])[0])
                #print (i, cellPtrArr[i])
        else:
            pass

        #清空
        self.tableWidgetCell.clearContents()

        if (type == 0x0d):#b+tree叶子页
            for i in range(0, cellNum):
                len, off1 = self.varintTrans(buf[cellPtrArr[i]:])
                offset = off1
                key, off1 = self.varintTrans(buf[cellPtrArr[i] + offset:])
                offset += off1
                self.addTableItem(dataType.CELL_INFO_TYPE, i, 0, "0x%X" % (cellPtrArr[i]))
                self.addTableItem(dataType.CELL_INFO_TYPE, i, 1, "%d" % (len))
                self.addTableItem(dataType.CELL_INFO_TYPE, i, 2, "%d" % (key))
                self.addTableItem(dataType.CELL_INFO_TYPE, i, 5, "0x%X" % (offset))


        elif(type == 0x05):#b+tree内部页
            for i in range(0, cellNum):
                tmp = buf[cellPtrArr[i]:cellPtrArr[i] + 4]
                left = struct.unpack("!1I", tmp)[0]
                key, off = self.varintTrans(buf[cellPtrArr[i] + 4:])
                self.addTableItem(dataType.CELL_INFO_TYPE, i, 0, "0x%X" % (cellPtrArr[i]))
                #self.addTableItem(dataType.CELL_INFO_TYPE, i, 1, "%d" % (len))
                self.addTableItem(dataType.CELL_INFO_TYPE, i, 2, "%d" % (key))
                self.addTableItem(dataType.CELL_INFO_TYPE, i, 3, "%d" % (left))
                self.addTableItem(dataType.CELL_INFO_TYPE, i, 5, "0x%X" % (off + 4))
        elif (type == 0x0a):#b-tree叶子页
            for i in range(0, cellNum):
                len, off = self.varintTrans(buf[cellPtrArr[i]:])
                self.addTableItem(dataType.CELL_INFO_TYPE, i, 0, "0x%X" % (cellPtrArr[i]))
                self.addTableItem(dataType.CELL_INFO_TYPE, i, 1, "%d" % (len))
                self.addTableItem(dataType.CELL_INFO_TYPE, i, 5, "0x%X" % (off))
        elif (type == 0x02):#b-tree内部页
            for i in range(0, cellNum):
                left = struct.unpack("!I", buf[cellPtrArr[i]:cellPtrArr[i] + 4])[0]
                len, off = self.varintTrans(buf[cellPtrArr[i] + 4:])
                self.addTableItem(dataType.CELL_INFO_TYPE, i, 0, "0x%X" % (cellPtrArr[i]))
                self.addTableItem(dataType.CELL_INFO_TYPE, i, 1, "%d" % (len))
                self.addTableItem(dataType.CELL_INFO_TYPE, i, 3, "%d" % (left))
                self.addTableItem(dataType.CELL_INFO_TYPE, i, 5, "0x%X" % (off+4))
        else:
            pass

    def handlePage(self):

        pghdr = QColor(238,130,238)
        cellptr = QColor(32,178,170)
        unallocated = QColor(255,160,122)
        active = QColor(124,252,0)

        # 清空
        self.tableWidgetPageHeader.clearContents()

        if (self.pageNum == 1):
            off = 100
        else:
            off = 0

        buf = ""
        PAGE_HEADER = '!1B3H1B1I'
        with open(self.filename, 'rb') as f:
            f.seek((self.pageNum - 1) * self.pageSize, 0)
            buf = f.read(self.pageSize)

        arr = struct.unpack(PAGE_HEADER, buf[off:off+12])
        if (arr[0] == 0x0d):
            self.addTableItem(dataType.PAGE_INFO_TYPE, 0, 0, "表b+tree叶子页")
        elif(arr[0] == 0x05):
            self.addTableItem(dataType.PAGE_INFO_TYPE, 0, 0, "表b+tree内部页")
        elif (arr[0] == 0x0a):
            self.addTableItem(dataType.PAGE_INFO_TYPE, 0, 0, "索引b-tree叶子页")
        elif (arr[0] == 0x02):
            self.addTableItem(dataType.PAGE_INFO_TYPE, 0, 0, "索引b-tree内部页")
        else: #这里暂不考虑指针图页，项目中未使用自收缩数据库配置，仍有可能为溢出页或空闲页
            '''
            self.addTableItem(dataType.PAGE_INFO_TYPE, 0, 0, "溢出页")
            OVERFLOW_HEADER = "!I"
            pagearr = struct.unpack(PAGE_HEADER, buf[0:4])
            self.addTableItem(dataType.PAGE_INFO_TYPE, 4, 0, "%d" % (pagearr[0]))
            self.textWidget.markDataArea(pghdr, self.transOffset(0, 4))
            '''
            self.addTableItem(dataType.PAGE_INFO_TYPE, 0, 0, "空闲页")
            HEADER = "!2I"
            pagearr = struct.unpack(HEADER, buf[0:8])
            #print ("nextTrunk:",pagearr[0], ", leafCount:",pagearr[1])
            QMessageBox.warning(self,"空闲页:","nextTrunk:%d, leafCount:%d"%(pagearr[0],pagearr[1]))
            self.textWidget.markDataArea(pghdr, self.transOffset(0, 8))
            self.textWidget.markDataArea(active, self.transOffset(8, pagearr[1] * 4 + 8))
            return

        self.addTableItem(dataType.PAGE_INFO_TYPE, 1, 0, "0x%X" % (arr[1]))
        self.addTableItem(dataType.PAGE_INFO_TYPE, 2, 0, "%d" % (arr[2]))
        self.addTableItem(dataType.PAGE_INFO_TYPE, 3, 0, "0x%X" % (arr[3]))
        self.addTableItem(dataType.PAGE_INFO_TYPE, 4, 0, "%d" % (arr[4]))
        if(arr[0] == 0x05 or arr[0] == 0x02):
            self.addTableItem(dataType.PAGE_INFO_TYPE, 5, 0, "%d" % (arr[5]))
            cellptrOff = 12
            self.pageType = dataType.PAGE_TRUNK_TYPE
            self.textWidget.markDataArea(pghdr, self.transOffset(off, 12))

        else:
            self.addTableItem(dataType.PAGE_INFO_TYPE, 5, 0, "")
            cellptrOff = 8
            self.pageType = dataType.PAGE_LEAF_TYPE
            self.textWidget.markDataArea(pghdr, self.transOffset(off, 8))

        cellnum = arr[2]
        self.textWidget.markDataArea(cellptr, self.transOffset(off + cellptrOff, cellnum * 2))
        self.textWidget.markDataArea(active, self.transOffset(arr[3], self.pageSize - arr[3]))

        #有自由块
        if (arr[1] != 0):
            freeOff = arr[1]
            while (freeOff != 0):
                FREE_HEADER = '!2H'
                freeArr = struct.unpack(FREE_HEADER, buf[freeOff:freeOff+4])
                len = freeArr[1]
                if(len != 0):
                    self.textWidget.markDataArea(unallocated, self.transOffset(freeOff, len))
                freeOff = freeArr[0]

        self.handleCellHeader(buf, arr[0])

    def handleData(self):
        filehdr = QColor(119,136,153)

        if(self.pageNum == 1):
            #第一页需要标记文件头
            self.textWidget.markDataArea(filehdr, self.transOffset(0, 100))
            off = 100
        else:
            off = 0
        '''
        buf = ""
        off += (self.pageNum - 1) * self.pageSize
        with open(self.filename, 'rb') as f:
            f.seek(off, 0)
            buf = f.read(1)

        STRUCT = "!B"
        #print(type(page))
        arr = struct.unpack(STRUCT, buf)
        #如果页类型是叶子页
        if(arr[0] == 0x0D or arr[0] == 0x0A):
            self.pageType = dataType.PAGE_LEAF_TYPE
            self.textWidget.markDataArea(pghdr, self.transOffset(off,8))
        else:
            self.pageType = dataType.PAGE_TRUNK_TYPE
            self.textWidget.markDataArea(pghdr, self.transOffset(off,12))
        '''
        self.handlePage()

    def loadFile(self, fname):
        if(self.pageNum == 1):
            self.handleFileHeader()

        buf = ''
        offset = (self.pageNum - 1 ) * self.pageSize
        with open(fname, 'rb') as f:
            i = 0
            f.seek(offset,0)
            while i < self.pageSize:
                i += 1
                a = f.read(1)
                if not a :
                    break
                else:
                    pass
                buf += ("%.2x"%(ord(a))+' ').upper()
                if (i % 16 == 0):
                    buf += '\r\n'
                else :
                    pass

        #print (buf)
        self.textWidget.setPlainText(buf)
        self.handleData()

    def fileClose(self):
        self.pageNum = 1
        self.pageInput.setText("")
        self.filename = None
        self.textWidget.setPlainText("")
        self.filename = None  # 数据库文件名
        self.pageNum = 0
        self.pageCount = 0
        self.pageData = None
        self.dot = None
        self.tableWidgetTree.setPixmap(QPixmap(""))

        # 清空
        self.tableWidgetFileHeader.clearContents()
        self.tableWidgetPageHeader.clearContents()
        self.tableWidgetCell.clearContents()

    def showbug(self):
            _err=traceback.format_exc()
            QMessageBox.warning(self,"warning","%s"%_err,QMessageBox.Ok)

    def fileOpen(self):
        try:
            dir = (os.path.dirname(self.filename) if self.filename is not None else ".")
            formats = (
            ['*.%s' % (str(format, encoding="utf8").lower()) for format in QImageReader.supportedImageFormats()])
            fname = QFileDialog.getOpenFileName(self, "选取文件", dir,
                                                "所有文件 (*);;SQLite数据库文件 (*.db *.sqlite *.sqlite3 *.db3)")[0]
            # 最后面那一个是过滤参数，用于图片的过滤 最后的[0]表示我们仅仅需要返回第一个参数，也就是fname即可。
            if fname:
                self.pageNum = 1
                self.pageInput.setText("%d"%(self.pageNum))
                self.filename = fname
                self.loadFile(fname)
                #QMessageBox.warning(self,"Test","%s"%fname)
        except:
            self.showbug()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 一次性的传递这些参数，在QSetting中就可以直接使用，而在之后的QSetting调用中就不用再设置了。
    #app.setOrganizationName("Marvin Studio")
    #app.setOrganizationDomain("http://www.marvinstudio.cn")
    app.setApplicationName("SQLite3 File Viewer")
    app.setWindowIcon(QIcon(":/loudou.png"))

    qb = AppWindow()
    qb.show()
    sys.exit(app.exec_())