from qtpy.QtWidgets import QGraphicsRectItem, QGraphicsEllipseItem, QMenu
from qtpy.QtGui import QBrush, QPen
from qtpy.QtCore import Qt

class CustomShapeItem(QGraphicsRectItem):
    def __init__(self, rect, color, app_reference):
        super().__init__(rect)
        self.setBrush(QBrush(color))
        self.setPen(QPen(Qt.black, 2))
        self.setFlags(QGraphicsRectItem.ItemIsMovable | QGraphicsRectItem.ItemIsSelectable)
        self.color = color
        self.app_reference = app_reference

    def contextMenuEvent(self, event):
        # Right-click context menu
        menu = QMenu()
        rectangle_action = menu.addAction("Circular Sector")
        delete_action = menu.addAction("Delete")

        action = menu.exec_(event.screenPos())

        if action == rectangle_action:
            self.app_reference.convert_to_kruhova(self)
        elif action == delete_action:
            self.app_reference.delete_shape(self)


class CustomEllipseItem(QGraphicsEllipseItem):
    def __init__(self, rect, color, app_reference):
        super().__init__(rect)
        self.setBrush(QBrush(color))
        self.setPen(QPen(Qt.black, 2))
        self.setFlags(QGraphicsEllipseItem.ItemIsMovable | QGraphicsEllipseItem.ItemIsSelectable)
        self.color = color
        self.app_reference = app_reference

    def contextMenuEvent(self, event):
        menu = QMenu()
        kruhova_action = menu.addAction("Rectangle")
        delete_action = menu.addAction("Delete")

        action = menu.exec_(event.screenPos())

        if action == kruhova_action:
            self.app_reference.convert_to_rectangle(self)
        elif action == delete_action:
            self.app_reference.delete_shape(self)
