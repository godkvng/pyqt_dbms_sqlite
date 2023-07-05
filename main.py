from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication, QLabel, QGridLayout, QLineEdit, QPushButton, QMainWindow, \
	QTableWidget, QTableWidgetItem, QDialog, QVBoxLayout, QComboBox, QToolBar, QStatusBar, QMessageBox
import sys
import sqlite3


class MainWindow(QMainWindow):

	def __init__(self):
		super(MainWindow, self).__init__()
		self.setWindowTitle("Student Management System")
		self.setMinimumSize(800, 600)

		file_menu_item = self.menuBar().addMenu("&File")
		help_menu_item = self.menuBar().addMenu("&Help")

		add_student_action = QAction(QIcon("icons/add.png"), "Add Student", self)
		add_student_action.triggered.connect(self.insert)
		file_menu_item.addAction(add_student_action)

		about_action = QAction("About", self)
		help_menu_item.addAction(about_action)
		about_action.setMenuRole(QAction.MenuRole.NoRole)
		about_action.triggered.connect(self.about)

		self.table = QTableWidget()
		self.table.setColumnCount(4)
		self.table.setHorizontalHeaderLabels(("ID", "Name", "Course", "Mobile"))
		self.table.verticalHeader().setVisible(False)

		self.setCentralWidget(self.table)
		self.load_data()

		# Create toolbar and add items to the toolbar
		toolbar = QToolBar()
		toolbar.setMovable(True)
		self.addToolBar(toolbar)
		toolbar.addAction(add_student_action)
		# toolbar.addAction(search_action)

		# Create statusbar and add statusbar elements
		self.statusbar = QStatusBar()
		self.setStatusBar(self.statusbar)

		# Detect cell click
		self.table.cellClicked.connect(self.cell_clicked)

	def cell_clicked(self):
		edit_button = QPushButton("Edit Record")
		edit_button.clicked.connect(self.edit)

		delete_button = QPushButton("Delete Record")
		delete_button.clicked.connect(self.delete)

		children = self.findChildren(QPushButton)
		if children:
			for child in children:
				self.statusbar.removeWidget(child)

		self.statusbar.addWidget(edit_button)
		self.statusbar.addWidget(delete_button)

	def load_data(self):
		connection = sqlite3.connect("database.db")
		result = connection.execute("SELECT * FROM students")
		self.table.setRowCount(0)
		for row_number, row_data in enumerate(result):
			self.table.insertRow(row_number)
			for column_number, data in enumerate(row_data):
				self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
		connection.close()

	def insert(self):
		dialog = InsertDialog()
		dialog.exec()

	def edit(self):
		dialog = EditDialog()
		dialog.exec()

	def delete(self):
		dialog = DeleteDialog()
		dialog.exec()

	def about(self):
		dialog = AboutDialog()
		dialog.exec()


class AboutDialog(QMessageBox):
	def __init__(self):
		super(AboutDialog, self).__init__()
		self.setWindowTitle("About")
		content = """
		This app was made be me. Heheheehh
		"""
		self.setText(content)


class EditDialog(QDialog):
	def __init__(self):
		super(EditDialog, self).__init__()
		self.setWindowTitle("Update Student Data")
		self.setFixedWidth(300)
		self.setFixedHeight(300)

		layout = QVBoxLayout()

		# Get student name from selected row
		index = app.table.currentRow()
		student_name = app.table.item(index, 1).text()

		# Get id from selected row
		self.student_id = app.table.item(index, 0).text()

		# Add student name widget
		self.student_name = QLineEdit(student_name)
		self.student_name.setPlaceholderText("Name")
		layout.addWidget(self.student_name)

		# Add combo box for courses
		course_name = app.table.item(index, 2).text()
		self.course_name = QComboBox()
		courses = ["Biology", "Math", "Astronomy", "Physics"]
		self.course_name.addItems(courses)
		self.course_name.setCurrentText(course_name)
		layout.addWidget(self.course_name)

		# Add student mobile widget
		mobile = app.table.item(index, 3).text()
		self.mobile = QLineEdit(mobile)
		self.mobile.setPlaceholderText("Name")
		layout.addWidget(self.mobile)

		# Add submit button widget
		button = QPushButton("Update Record")
		button.clicked.connect(self.update_student)
		layout.addWidget(button)

		self.setLayout(layout)

	def update_student(self):
		connection = sqlite3.connect("database.db")
		cursor = connection.cursor()
		cursor.execute("UPDATE students SET name = ?, course = ?, mobile = ? WHERE id = ?",
					   (self.student_name.text(),
						self.course_name.itemText(self.course_name.currentIndex()),
						self.mobile.text(),
						self.student_id))
		connection.commit()
		cursor.close()

		# Refresh the table
		app.load_data()


class DeleteDialog(QDialog):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("Delete Student Data")

		layout = QGridLayout()
		confirmation = QLabel("Are you sur you want to delete?")
		yes = QPushButton("Yes")
		no = QPushButton("No")

		layout.addWidget(confirmation, 0, 0, 1, 2)
		layout.addWidget(yes, 1, 0)
		layout.addWidget(no, 1, 1)

		self.setLayout(layout)

		yes.clicked.connect(self.delete_student)

	def delete_student(self):
		# Get selected row index and student id
		index = app.table.currentRow()
		student_id = app.table.item(index, 0).text()

		connection = sqlite3.connect("database.db")
		cursor = connection.cursor()
		cursor.execute("DELETE from students WHERE id = ?", (student_id,))
		connection.commit()
		cursor.close()
		connection.close()
		app.load_data()

		self.close()

		confirmation_widget = QMessageBox()
		confirmation_widget.setWindowTitle("Success")
		confirmation_widget.setText('The record was deleted successfully')
		confirmation_widget.exec()


class InsertDialog(QDialog):
	def __init__(self):
		super(InsertDialog, self).__init__()
		self.setWindowTitle("Insert Student Data")

		layout = QVBoxLayout()

		# Add student name widget
		self.student_name = QLineEdit()
		self.student_name.setPlaceholderText("Name")
		layout.addWidget(self.student_name)

		# Add combo box for courses
		self.course_name = QComboBox()
		courses = ["Biology", "Math", "Astronomy", "Physics"]
		self.course_name.addItems(courses)
		layout.addWidget(self.course_name)

		# Add student mobile widget
		self.mobile = QLineEdit()
		self.mobile.setPlaceholderText("Name")
		layout.addWidget(self.mobile)

		# Add submit button widget
		button = QPushButton("Register")
		button.clicked.connect(self.add_student)
		layout.addWidget(button)

		self.setLayout(layout)

	def add_student(self):
		name = self.student_name.text()
		course = self.course_name.itemText(self.course_name.currentIndex())
		mobile = self.mobile.text()
		connection = sqlite3.connect("database.db")
		cursor = connection.cursor()
		cursor.execute("INSERT INTO students (name, course, mobile) VALUES(?, ?, ?)", (name, course, mobile))
		connection.commit()
		cursor.close()
		connection.close()
		app.load_data()


main_app = QApplication(sys.argv)
app = MainWindow()
app.show()
sys.exit(main_app.exec())
