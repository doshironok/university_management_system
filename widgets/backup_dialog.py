from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QListWidget, QListWidgetItem,
                             QMessageBox, QProgressDialog, QSplitter)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from services.backup_service import BackupService
from utils.helpers import get_file_size


class BackupThread(QThread):
    """Поток для создания резервной копии"""
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def run(self):
        try:
            backup_file = BackupService.create_backup()
            if backup_file:
                self.finished.emit(backup_file)
            else:
                self.error.emit("Не удалось создать резервную копию")
        except Exception as e:
            self.error.emit(str(e))


class BackupDialog(QDialog):
    """Диалог управления резервными копиями"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_backups()

    def setup_ui(self):
        self.setWindowTitle("Управление резервными копиями БД")
        self.setFixedSize(600, 400)

        layout = QVBoxLayout()

        # Заголовок
        title_label = QLabel("Резервные копии базы данных")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label)

        # Список бэкапов
        self.backup_list = QListWidget()
        self.backup_list.itemDoubleClicked.connect(self.on_backup_selected)
        layout.addWidget(self.backup_list)

        # Кнопки управления
        button_layout = QHBoxLayout()

        create_btn = QPushButton("Создать резервную копию")
        restore_btn = QPushButton("Восстановить из выбранной")
        delete_btn = QPushButton("Удалить выбранную")
        close_btn = QPushButton("Закрыть")

        create_btn.clicked.connect(self.create_backup)
        restore_btn.clicked.connect(self.restore_backup)
        delete_btn.clicked.connect(self.delete_backup)
        close_btn.clicked.connect(self.reject)

        button_layout.addWidget(create_btn)
        button_layout.addWidget(restore_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def load_backups(self):
        """Загрузка списка резервных копий"""
        self.backup_list.clear()
        backups = BackupService.get_backup_list()

        for backup in backups:
            item_text = f"{backup['filename']} - {backup['created']} - {get_file_size(backup['path'])}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, backup)
            self.backup_list.addItem(item)

    def create_backup(self):
        """Создание новой резервной копии"""
        progress = QProgressDialog("Создание резервной копии...", "Отмена", 0, 0, self)
        progress.setWindowTitle("Пожалуйста, подождите")
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.show()

        self.backup_thread = BackupThread()
        self.backup_thread.finished.connect(lambda path: self.on_backup_created(path, progress))
        self.backup_thread.error.connect(lambda error: self.on_backup_error(error, progress))
        self.backup_thread.start()

    def on_backup_created(self, file_path, progress):
        """Обработка успешного создания бэкапа"""
        progress.close()
        QMessageBox.information(self, "Успех", f"Резервная копия создана:\n{file_path}")
        self.load_backups()

    def on_backup_error(self, error, progress):
        """Обработка ошибки создания бэкапа"""
        progress.close()
        QMessageBox.critical(self, "Ошибка", f"Не удалось создать резервную копию:\n{error}")

    def on_backup_selected(self, item):
        """Обработка выбора бэкапа"""
        backup_data = item.data(Qt.ItemDataRole.UserRole)
        QMessageBox.information(
            self,
            "Информация о резервной копии",
            f"Файл: {backup_data['filename']}\n"
            f"Размер: {get_file_size(backup_data['path'])}\n"
            f"Создан: {backup_data['created']}"
        )

    def restore_backup(self):
        """Восстановление из резервной копии"""
        current_item = self.backup_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Ошибка", "Выберите резервную копию для восстановления")
            return

        backup_data = current_item.data(Qt.ItemDataRole.UserRole)

        reply = QMessageBox.question(
            self,
            "Подтверждение восстановления",
            f"Вы уверены, что хотите восстановить базу данных из резервной копии?\n"
            f"Файл: {backup_data['filename']}\n\n"
            f"ВНИМАНИЕ: Все текущие данные будут заменены!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            progress = QProgressDialog("Восстановление базы данных...", "Отмена", 0, 0, self)
            progress.setWindowTitle("Пожалуйста, подождите")
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.show()

            success = BackupService.restore_backup(backup_data['path'])
            progress.close()

            if success:
                QMessageBox.information(self, "Успех", "База данных успешно восстановлена")
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось восстановить базу данных")

    def delete_backup(self):
        """Удаление резервной копии"""
        current_item = self.backup_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Ошибка", "Выберите резервную копию для удаления")
            return

        backup_data = current_item.data(Qt.ItemDataRole.UserRole)

        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить резервную копию?\n{backup_data['filename']}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            import os
            try:
                os.remove(backup_data['path'])
                QMessageBox.information(self, "Успех", "Резервная копия удалена")
                self.load_backups()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить файл:\n{str(e)}")