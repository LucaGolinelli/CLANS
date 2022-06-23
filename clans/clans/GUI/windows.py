from PyQt5.QtWidgets import *
import re
import clans.config as cfg


def error_occurred(method, method_name, exception_err, error_msg):

    if cfg.run_params['is_debug_mode']:
        print("\nError in " + method.__globals__['__file__'] + " (" + method_name + "):")
        print(exception_err)

    msg_box = QMessageBox()
    msg_box.setText(error_msg)
    if msg_box.exec_():
        return


class AboutWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.is_visible = 0

        self.layout = QVBoxLayout()

        self.setWindowTitle("About CLANS")
        self.setGeometry(400, 100, 300, 150)

        self.version_label = QLabel("Version: " + cfg.version)
        self.version_label.setStyleSheet("color: maroon")

        self.overview_label = QLabel("CLANS is a Python-based program for visualizing the relationship between "
                                     "proteins\nbased on their pairwise sequence similarities.\n"
                                     "The program implements a version of the Fruchterman-Reingold force directed\n"
                                     "graph layout algorithm to visualize the sequence similarities in a 2D or 3D "
                                     "space.")

        self.layout.addWidget(self.version_label)
        self.layout.addWidget(self.overview_label)

        self.setLayout(self.layout)

    def open_window(self):
        try:
            self.is_visible = 1
            self.show()
        except Exception as err:
            error_msg = "An error occurred: cannot open the 'About CLANS' window"
            error_occurred(self.open_window, 'open_window', err, error_msg)

    def close_window(self):
        try:
            self.is_visible = 0
            self.close()

        except Exception as err:
            error_msg = "An error occurred: cannot close the 'About CLANS' window"
            error_occurred(self.close_window, 'close_window', err, error_msg)


class SelectedSeqWindow(QWidget):

    def __init__(self, main_window, net_plot):
        super().__init__()

        self.main_window_object = main_window
        self.net_plot_object = net_plot

        self.sorted_seq_indices = []
        self.items = []

        self.is_visible = 0

        self.main_layout = QVBoxLayout()

        self.setWindowTitle("Selected Subset")
        self.setGeometry(600, 150, 600, 400)

        # Add a message for the number of selected sequences on top
        self.message = QLabel("")
        self.message.setStyleSheet("color: maroon;")

        self.main_layout.addWidget(self.message)

        # Add a list widget to display the sequences
        self.seq_list = QListWidget()
        self.seq_list.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.main_layout.addWidget(self.seq_list)

        # Add a layout for buttons
        self.buttons_layout = QHBoxLayout()

        self.highlight_button = QPushButton("Highlight in graph")
        self.highlight_button.setCheckable(True)
        self.highlight_button.released.connect(self.highlight_points)

        self.remove_button = QPushButton("Remove from subset")
        self.remove_button.released.connect(self.remove_from_selected)

        self.keep_selected_button = QPushButton("Set as selected subset")
        self.keep_selected_button.released.connect(self.keep_selected)

        self.find_button = QPushButton("Find in subset")
        self.find_button.released.connect(self.find_in_subset)

        self.close_button = QPushButton("Close")
        self.close_button.released.connect(self.close_window)

        self.buttons_layout.addWidget(self.highlight_button)
        self.buttons_layout.addWidget(self.keep_selected_button)
        self.buttons_layout.addWidget(self.remove_button)
        self.buttons_layout.addWidget(self.find_button)
        self.buttons_layout.addWidget(self.close_button)
        self.buttons_layout.addStretch()

        self.main_layout.addLayout(self.buttons_layout)

        self.setLayout(self.main_layout)

        self.seq_list.itemSelectionChanged.connect(self.highlight_points)

    def open_window(self):
        try:
            self.is_visible = 1
            self.show()
        except Exception as err:
            error_msg = "An error occurred: cannot open the selected sequences window"
            error_occurred(self.open_window, 'open_window', err, error_msg)

    def close_window(self):
        try:
            self.highlight_button.setChecked(False)

            try:
                self.highlight_points()
            except Exception as err:
                error_msg = "An error occurred: cannot turn off points highlighting"
                error_occurred(self.highlight_points, 'highlight_points', err, error_msg)

            self.is_visible = 0
            self.close()

        except Exception as err:
            error_msg = "An error occurred: cannot close the selected sequences window"
            error_occurred(self.close_window, 'close_window', err, error_msg)

    def update_window_title(self, file_name):

        self.setWindowTitle("Selected Subset from " + file_name)

    def update_sequences(self):

        self.highlight_button.setChecked(False)

        try:
            self.highlight_points()
        except Exception as err:
            error_msg = "An error occurred: cannot highlight data-points"
            error_occurred(self.highlight_points, 'highlight_points', err, error_msg)
            return

        self.seq_list.clear()
        self.items = []

        self.sorted_seq_indices = sorted(self.net_plot_object.selected_points)

        # There is at least one selected sequence
        if len(self.sorted_seq_indices) > 0:
            for i in range(len(self.sorted_seq_indices)):
                seq_index = self.sorted_seq_indices[i]
                seq_title = cfg.sequences_array[seq_index]['seq_title'][0:]

                # The sequence header is the same as the index -> display only once
                if str(seq_index) == seq_title:
                    line_str = str(seq_index)
                else:
                    line_str = str(seq_index) + "  " + seq_title

                self.items.append(QListWidgetItem(line_str))
                self.seq_list.insertItem(i, self.items[i])

                self.message.setText("Displaying " + str(len(self.sorted_seq_indices)) + " selected sequences")

        else:
            self.message.setText("No selected sequences")

    def clear_list(self):

        try:
            self.seq_list.clear()
            self.sorted_seq_indices = []
            self.items = []
            self.highlight_button.setChecked(False)
            self.message.setText("")

        except Exception as err:
            error_msg = "An error occurred: cannot clear the sequences list"
            error_occurred(self.clear_list, 'clear_list', err, error_msg)

    def highlight_points(self):

        try:
            selected_indices = {}
            not_selected_indices = {}

            for item in self.seq_list.selectedIndexes():
                row_index = item.row()
                selected_indices[self.sorted_seq_indices[row_index]] = 1

            for seq_index in self.sorted_seq_indices:
                if seq_index not in selected_indices:
                    not_selected_indices[seq_index] = 1

            if len(selected_indices) > 0:

                if self.main_window_object.view_in_dimensions_num == 2 or self.main_window_object.mode == "selection":
                    dim_num = 2
                else:
                    dim_num = 3

                # Highlight button is checked
                if self.highlight_button.isChecked():

                    # Highlight the selected points
                    try:
                        self.net_plot_object.highlight_selected_points(selected_indices, dim_num,
                                                                       self.main_window_object.z_indexing_mode,
                                                                       self.main_window_object.color_by,
                                                                       self.main_window_object.group_by)
                    except Exception as err:
                        error_msg = "An error occurred: cannot highlight the selected points"
                        error_occurred(self.net_plot_object.highlight_selected_points, 'highlight_selected_points', err,
                                       error_msg)
                        return

                    # Turn off all the rest (not selected)
                    try:
                        self.net_plot_object.unhighlight_selected_points(not_selected_indices, dim_num,
                                                                         self.main_window_object.z_indexing_mode,
                                                                         self.main_window_object.color_by,
                                                                         self.main_window_object.group_by)
                    except Exception as err:
                        error_msg = "An error occurred: cannot turn off highlighting"
                        error_occurred(self.net_plot_object.unhighlight_selected_points, 'unhighlight_selected_points', err,
                                       error_msg)

                # Turn off highlighting of all selected sequences (back to normal selected presentation)
                else:
                    try:
                        self.net_plot_object.unhighlight_selected_points(self.sorted_seq_indices, dim_num,
                                                                         self.main_window_object.z_indexing_mode,
                                                                         self.main_window_object.color_by,
                                                                         self.main_window_object.group_by)
                    except Exception as err:
                        error_msg = "An error occurred: cannot turn off highlighting"
                        error_occurred(self.net_plot_object.unhighlight_selected_points, 'unhighlight_selected_points',
                                       err, error_msg)

        except Exception as err:
            error_msg = "An error occurred: cannot turn highlight points"
            error_occurred(self.highlight_points, 'highlight_points', err, error_msg)

    def keep_selected(self):

        try:
            selected_indices = {}
            not_selected_indices = {}

            for item in self.seq_list.selectedIndexes():
                row_index = item.row()
                selected_indices[self.sorted_seq_indices[row_index]] = 1

            for seq_index in self.sorted_seq_indices:
                if seq_index not in selected_indices:
                    not_selected_indices[seq_index] = 1

            if len(not_selected_indices) > 0:

                if self.main_window_object.view_in_dimensions_num == 2 or self.main_window_object.mode == "selection":
                    dim_num = 2
                else:
                    dim_num = 3

                try:
                    self.net_plot_object.remove_from_selected(not_selected_indices, dim_num,
                                                            self.main_window_object.z_indexing_mode,
                                                            self.main_window_object.color_by,
                                                            self.main_window_object.group_by)
                except Exception as err:
                    error_msg = "An error occurred: cannot remove sequences from the selected-subset"
                    error_occurred(self.net_plot_object.remove_from_selected, 'remove_from_selected', err, error_msg)
                    return

                try:
                    self.update_sequences()
                except Exception as err:
                    error_msg = "An error occurred: cannot update the sequences list in the selected sequences window"
                    error_occurred(self.update_sequences, 'update_sequences', err, error_msg)

        except Exception as err:
            error_msg = "An error occurred: cannot keep the sequences as selected"
            error_occurred(self.keep_selected, 'keep_selected', err, error_msg)

    def remove_from_selected(self):

        try:
            # Turn off highlighting
            self.highlight_button.setChecked(False)

            try:
                self.highlight_points()
            except Exception as err:
                error_msg = "An error occurred: cannot highlight data-points"
                error_occurred(self.highlight_points, 'highlight_points', err, error_msg)
                return

            selected_rows = []
            selected_indices = {}

            for item in self.seq_list.selectedIndexes():
                row_index = item.row()
                selected_rows.append(row_index)
                selected_indices[self.sorted_seq_indices[row_index]] = 1

            if len(selected_indices) > 0:

                if self.main_window_object.view_in_dimensions_num == 2 or self.main_window_object.mode == "selection":
                    dim_num = 2
                else:
                    dim_num = 3

                try:
                    self.net_plot_object.remove_from_selected(selected_indices, dim_num,
                                                              self.main_window_object.z_indexing_mode,
                                                              self.main_window_object.color_by,
                                                              self.main_window_object.group_by)
                except Exception as err:
                    error_msg = "An error occurred: cannot remove sequences from the selected-subset"
                    error_occurred(self.net_plot_object.remove_from_selected, 'remove_from_selected', err, error_msg)
                    return

                # Delete the selected rows from the list (in reverse order, to prevent problems with the row-indices)
                for row_index in reversed(selected_rows):
                    self.seq_list.takeItem(row_index)
                    self.sorted_seq_indices.pop(row_index)

                # Update the selected sequences list
                self.sorted_seq_indices = sorted(self.net_plot_object.selected_points)

                # Update the number of sequences message
                if len(self.sorted_seq_indices) > 0:
                    self.message.setText("Displaying " + str(len(self.sorted_seq_indices)) + " selected sequences")
                else:
                    self.message.setText("No selected sequences")

        except Exception as err:
            error_msg = "An error occurred: cannot remove sequences from the selected-subset"
            error_occurred(self.remove_from_selected, 'remove_from_selected', err, error_msg)

    def find_in_subset(self):

        try:
            find_dlg = FindDialog("Find in subset")

            if find_dlg.exec_():
                text, is_case_sensitive = find_dlg.get_input()

                # The user entered some text
                if text != "":

                    self.seq_list.clearSelection()
                    # Turn off highlighting
                    self.highlight_button.setChecked(False)

                    try:
                        self.highlight_points()
                    except Exception as err:
                        error_msg = "An error occurred: cannot highlight data-points"
                        error_occurred(self.highlight_points, 'highlight_points', err, error_msg)
                        return

                    i = 0
                    for seq_index in self.sorted_seq_indices:
                        seq_title = cfg.sequences_array[seq_index]['seq_title']

                        if is_case_sensitive:
                            m = re.search(text, seq_title)
                        else:
                            m = re.search(text, seq_title, re.IGNORECASE)
                        # Search term was found in sequence title
                        if m:
                            self.items[i].setSelected(True)
                        i += 1

        except Exception as err:
            error_msg = "An error occurred while searching the subset"
            error_occurred(self.find_in_subset, 'find_in_subset', err, error_msg)


class FindDialog(QDialog):

    def __init__(self, win_title):
        super().__init__()

        self.setWindowTitle(win_title)
        self.setGeometry(650, 600, 300, 100)

        self.layout = QVBoxLayout()

        self.title = QLabel("Enter a search term:")
        self.find_area = QLineEdit()
        self.case_checkbox = QCheckBox("Case sensitive")

        self.text = ""
        self.is_case_sensitive = False

        # Add the OK/Cancel standard buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.layout.addWidget(self.title)
        self.layout.addWidget(self.find_area)
        self.layout.addWidget(self.case_checkbox)
        self.layout.addWidget(self.button_box)

        self.setLayout(self.layout)

    def get_input(self):

        self.text = self.find_area.text()
        self.is_case_sensitive = self.case_checkbox.isChecked()

        return self.text, self.is_case_sensitive


class SearchResultsWindow(QWidget):

    def __init__(self, main_window, net_plot):
        super().__init__()

        self.main_window_object = main_window
        self.net_plot_object = net_plot

        self.sorted_seq_indices = []
        self.items = []
        self.is_visible = 0

        self.setWindowTitle("Search results")
        self.setGeometry(650, 400, 600, 400)

        self.main_layout = QVBoxLayout()

        # Add a message on top
        self.message = QLabel("")
        self.message.setStyleSheet("color: maroon;")

        self.main_layout.addWidget(self.message)

        # Add a list widget to display the sequences
        self.seq_list = QListWidget()
        self.seq_list.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.main_layout.addWidget(self.seq_list)

        # Add a layout for buttons
        self.buttons_layout = QHBoxLayout()

        self.highlight_button = QPushButton("Highlight all")
        self.highlight_button.setCheckable(True)
        self.highlight_button.released.connect(self.highlight_all)

        self.add_to_selected_button = QPushButton("Add to selected subset")
        self.add_to_selected_button.released.connect(self.add_to_selected)

        self.set_as_selected_button = QPushButton("Set as selected subset")
        self.set_as_selected_button.released.connect(self.set_as_selected)

        self.new_search_button = QPushButton("New search")
        self.new_search_button.released.connect(self.new_search)

        self.close_button = QPushButton("Close")
        self.close_button.released.connect(self.close_window)

        self.buttons_layout.addWidget(self.highlight_button)
        self.buttons_layout.addWidget(self.add_to_selected_button)
        self.buttons_layout.addWidget(self.set_as_selected_button)
        self.buttons_layout.addWidget(self.new_search_button)
        self.buttons_layout.addWidget(self.close_button)
        self.buttons_layout.addStretch()

        self.main_layout.addLayout(self.buttons_layout)
        self.setLayout(self.main_layout)

    def open_window(self):

        try:
            self.is_visible = 1
            self.show()

            self.setGeometry(650, 400, 600, 400)

            # Open the 'find' dialog when this window opens
            self.open_find_dialog()

        except Exception as err:
            error_msg = "An error occurred: cannot open the Search Results Window"
            error_occurred(self.open_window, 'open_window', err, error_msg)

    def close_window(self):
        try:
            self.clear_seq_list()
            self.is_visible = 0
            self.close()

        except Exception as err:
            error_msg = "An error occurred: cannot close the Search Results Window"
            error_occurred(self.close_window, 'close_window', err, error_msg)

    def highlight_all(self):
        try:
            # Select all items
            if self.highlight_button.isChecked():
                for i in range(len(self.items)):
                    self.items[i].setSelected(True)

            # De-select all items
            else:
                for i in range(len(self.items)):
                    self.items[i].setSelected(False)

        except Exception as err:
            error_msg = "An error occurred: cannot mark all sequences as selected"
            error_occurred(self.highlight_all, 'highlight_all', err, error_msg)

    def open_find_dialog(self):

        find_dlg = FindDialog("Find in data")
        find_dlg.setGeometry(750, 500, 300, 100)

        if find_dlg.exec_():
            text, is_case_sensitive = find_dlg.get_input()

            try:
                self.clear_seq_list()
            except Exception as err:
                error_msg = "An error occurred: cannot clear the sequences list"
                error_occurred(self.clear_seq_list, 'clear_seq_list', err, error_msg)

            # The user entered some text
            if text != "":
                self.update_message("Searching data...")

                try:
                    self.find_in_data(text, is_case_sensitive)
                except Exception as err:
                    error_msg = "An error occurred while searching the data"
                    error_occurred(self.find_in_data, 'find_in_data', err, error_msg)

            else:
                self.update_message("No results found")

    def find_in_data(self, text, is_case_sensitive):

        i = 0
        for seq_index in range(cfg.run_params['total_sequences_num']):
            seq_title = cfg.sequences_array[seq_index]['seq_title']

            if is_case_sensitive:
                m = re.search(text, seq_title)
            else:
                m = re.search(text, seq_title, re.IGNORECASE)

            # Search term was found in sequence title - add this sequence to the list
            if m:
                self.sorted_seq_indices.append(seq_index)

                # The sequence header is the same as the index -> display only once
                if str(seq_index) == seq_title:
                    line_str = str(seq_index)
                else:
                    line_str = str(seq_index) + "  " + seq_title

                self.items.append(QListWidgetItem(line_str))
                self.seq_list.insertItem(i, self.items[i])

                i += 1

        # No results found
        if i == 0:
            self.update_message("No results found")
        else:
            self.update_message("Found " + str(i) + " matching sequences")

    def clear_seq_list(self):
        self.seq_list.clear()
        self.highlight_button.setChecked(False)
        self.sorted_seq_indices = []
        self.items = []

    def update_message(self, message):
        self.message.setText(message)

    def new_search(self):
        try:
            self.open_find_dialog()
        except Exception as err:
            error_msg = "An error occurred: cannot open the 'Find' dialog"
            error_occurred(self.open_find_dialog, 'open_find_dialog', err, error_msg)

    def add_to_selected(self):

        try:
            selected_indices = {}

            for item in self.seq_list.selectedIndexes():
                row_index = item.row()
                selected_indices[self.sorted_seq_indices[row_index]] = 1

            if len(selected_indices) > 0:

                if self.main_window_object.view_in_dimensions_num == 2 or self.main_window_object.mode == "selection":
                    dim_num = 2
                else:
                    dim_num = 3

                # Set the selected sequences as the selected subset
                try:
                    self.net_plot_object.select_subset(selected_indices, dim_num, self.main_window_object.z_indexing_mode,
                                                       self.main_window_object.color_by,
                                                       self.main_window_object.group_by)
                except Exception as err:
                    error_msg = "An error occurred: cannot add to the selected subset"
                    error_occurred(self.net_plot_object.select_subset, 'select_subset', err, error_msg)
                    return

                # Update the selected sequences window
                try:
                    self.main_window_object.selected_seq_window.update_sequences()
                except Exception as err:
                    error_msg = "An error occurred: cannot update the sequences list in the selected sequences window"
                    error_occurred(self.main_window_object.selected_seq_window.update_sequences, 'update_sequences',
                                   err, error_msg)

                # Enable all the controls that are related to selected items in the Main Window
                self.main_window_object.open_selected_button.setEnabled(True)
                self.main_window_object.show_selected_names_button.setEnabled(True)
                self.main_window_object.add_to_group_button.setEnabled(True)
                self.main_window_object.remove_selected_button.setEnabled(True)
                if len(self.net_plot_object.selected_points) >= 4:
                    self.main_window_object.data_mode_combo.setEnabled(True)

        except Exception as err:
            error_msg = "An error occurred: cannot add to the selected subset"
            error_occurred(self.add_to_selected, 'add_to_selected', err, error_msg)

    def set_as_selected(self):

        try:
            selected_indices = {}

            for item in self.seq_list.selectedIndexes():
                row_index = item.row()
                selected_indices[self.sorted_seq_indices[row_index]] = 1

            if len(selected_indices) > 0:

                if self.main_window_object.view_in_dimensions_num == 2 or self.main_window_object.mode == "selection":
                    dim_num = 2
                else:
                    dim_num = 3

                # Clear the current selection
                try:
                    self.net_plot_object.reset_selection(dim_num, self.main_window_object.z_indexing_mode,
                                                         self.main_window_object.color_by, self.main_window_object.group_by,
                                                         self.main_window_object.is_show_group_names,
                                                         self.main_window_object.group_names_display)
                except Exception as err:
                    error_msg = "An error occurred: cannot clear the selected subset"
                    error_occurred(self.net_plot_object.reset_selection, 'reset_selection', err, error_msg)
                    return

                # Set the selected sequences as the selected subset
                try:
                    self.net_plot_object.select_subset(selected_indices, dim_num, self.main_window_object.z_indexing_mode,
                                                       self.main_window_object.color_by, self.main_window_object.group_by)
                except Exception as err:
                    error_msg = "An error occurred: cannot set the sequences as the selected-subset"
                    error_occurred(self.net_plot_object.select_subset, 'select_subset', err, error_msg)
                    return

                # Update the selected sequences window
                try:
                    self.main_window_object.selected_seq_window.update_sequences()
                except Exception as err:
                    error_msg = "An error occurred: cannot update the sequences list in the selected sequences window"
                    error_occurred(self.main_window_object.selected_seq_window.update_sequences, 'update_sequences',
                                   err, error_msg)

                # Enable all the controls that are related to selected items in the Main Window
                self.main_window_object.open_selected_button.setEnabled(True)
                self.main_window_object.show_selected_names_button.setEnabled(True)
                self.main_window_object.add_to_group_button.setEnabled(True)
                self.main_window_object.remove_selected_button.setEnabled(True)
                if len(self.net_plot_object.selected_points) >= 4:
                    self.main_window_object.data_mode_combo.setEnabled(True)

        except Exception as err:
            error_msg = "An error occurred: cannot set the sequences as the selected-subset"
            error_occurred(self.set_as_selected, 'set_as_selected', err, error_msg)

