import os

from PySide6.QtCore import Signal
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QFileDialog, QHeaderView, QAbstractItemView

from component.dialog.base_mask_dialog import BaseMaskDialog
from component.label.gif_label import GifLabel
from config import config
from config.setting import Setting
from interface.ui_download_dir import Ui_DownloadDir
from interface.ui_nas_add import Ui_NasAdd
from qt_owner import QtOwner
from task.qt_task import QtTaskBase
from task.task_upload import QtUpTask
from tools.str import Str
from view.nas.nas_item import NasInfoItem


class NasAddView(BaseMaskDialog, Ui_NasAdd, QtTaskBase):
    SaveLogin = Signal(NasInfoItem)

    def __init__(self, parent=None, nextID=1):
        BaseMaskDialog.__init__(self, parent)
        Ui_NasAdd.__init__(self)
        QtTaskBase.__init__(self)
        self.widget.adjustSize()
        self.setupUi(self.widget)
        self.closeButton.clicked.connect(self.close)
        self.testButton.clicked.connect(self.TestLink)
        self.saveButton.clicked.connect(self.Save)
        self.nextId = nextID
        self.buttonGroup.setId(self.dir1Radio, 0)
        self.buttonGroup.setId(self.dir2Radio, 1)
        self.buttonGroup.setId(self.dir3Radio, 2)
        self.compressGroup.setId(self.compress1Radio, 0)
        self.compressGroup.setId(self.compress2Radio, 1)

        self.loadingDialog = GifLabel(self)
        self.loadingDialog.Init(QtOwner().GetFileData(":/png/icon/loading.gif"), 256)
        self.loadingDialog.setAlignment(Qt.AlignCenter)
        self.loadingDialog.close()
        self.dirButton.clicked.connect(self.SelectSavePath)
        self.comboBox.currentIndexChanged.connect(self.SwitchTips)
        self.nasInfo = None
        self.SwitchTips()

    def SelectSavePath(self):
        url = QFileDialog.getExistingDirectory(self, Str.GetStr(Str.SelectFold))
        if url:
            self.pathEdit.setText(url)

    def SwitchTips(self):

        self.userEdit.setVisible(True)
        self.passEdit.setVisible(True)
        self.addressEdit.setVisible(True)
        self.portEdit.setVisible(True)
        self.dirButton.setVisible(False)
        self.label_select.setVisible(False)

        if self.comboBox.currentIndex() == 0:
            self.addressEdit.setText("http://192.168.31.28")
            self.portEdit.setText("5005")

        elif self.comboBox.currentIndex() == 1:
            self.addressEdit.setText("192.168.31.28")
            self.portEdit.setText("0")
        else:
            self.addressEdit.setText("")
            self.portEdit.setText("")

            self.userEdit.setVisible(False)
            self.passEdit.setVisible(False)
            self.addressEdit.setVisible(False)
            self.portEdit.setVisible(False)
            self.dirButton.setVisible(True)
            self.label_select.setVisible(True)
        if self.nasInfo:
            self.UpdateText(self.nasInfo)

    def Init(self, nasInfo):
        self.nasInfo = nasInfo
        assert isinstance(nasInfo, NasInfoItem)
        self.addressEdit.setText(nasInfo.address)
        self.titleEdit.setText(nasInfo.title)
        self.pathEdit.setText(nasInfo.path)
        self.passEdit.setText(nasInfo.passwd)
        self.userEdit.setText(nasInfo.user)
        self.isWaifu2x.setChecked(bool(nasInfo.is_waifu2x))
        self.comboBox.setCurrentIndex(nasInfo.type)
        self.portEdit.setText(str(nasInfo.port))

        getattr(self, "compress{}Radio".format(nasInfo.compress_index+1)).setChecked(True)
        getattr(self, "dir{}Radio".format(nasInfo.dir_index+1)).setChecked(True)
        return

    def UpdateText(self, nasInfo):
        if not nasInfo:
            nasInfo = NasInfoItem()
        assert isinstance(nasInfo, NasInfoItem)
        self.addressEdit.setText(nasInfo.address)
        self.titleEdit.setText(nasInfo.title)
        self.pathEdit.setText(nasInfo.path)
        self.passEdit.setText(nasInfo.passwd)
        self.userEdit.setText(nasInfo.user)
        self.isWaifu2x.setChecked(bool(nasInfo.is_waifu2x))
        self.portEdit.setText(str(nasInfo.port))
        getattr(self, "compress{}Radio".format(nasInfo.compress_index+1)).setChecked(True)
        getattr(self, "dir{}Radio".format(nasInfo.dir_index+1)).setChecked(True)
        return

    def GetNasInfo(self):
        nasInfo = NasInfoItem()
        nasInfo.nasId = self.nextId
        address = self.addressEdit.text()
        title = self.titleEdit.text()
        path = self.pathEdit.text()
        user = self.userEdit.text()
        password = self.passEdit.text()
        isWaifu2x = self.isWaifu2x.isChecked()
        index = self.buttonGroup.checkedId()
        compressId = self.compressGroup.checkedId()
        type = int(self.comboBox.currentIndex())
        if type != 2:
            if not address or not title or not path or not user or not password :
                return None
        else:
            if not title or not path:
                return None
        nasInfo.address = address
        nasInfo.title = title
        nasInfo.passwd = password
        nasInfo.user = user
        nasInfo.path = path
        nasInfo.is_waifu2x = isWaifu2x
        nasInfo.dir_index = index
        nasInfo.compress_index = compressId
        nasInfo.type = int(self.comboBox.currentIndex())
        if self.portEdit.text():
            nasInfo.port = int(self.portEdit.text())
        return nasInfo

    def Save(self):
        nasInfo = self.GetNasInfo()
        if not nasInfo:
            QtOwner().ShowError(Str.GetStr(Str.NotSpace))
            return
        self.SaveLogin.emit(nasInfo)
        self.close()
        return

    def TestLink(self):
        nasInfo = self.GetNasInfo()
        if not nasInfo:
            QtOwner().ShowError(Str.GetStr(Str.NotSpace))
            return
        self.loadingDialog.show()
        self.AddUploadTask(nasInfo, QtUpTask.Check, "", "", "","","", backParam=self.nextId, callBack=self.TestLinkCallBack)
        return

    def TestLinkCallBack(self, st, back):
        self.loadingDialog.close()
        QtOwner().ShowError(Str.GetStr(st))
        return