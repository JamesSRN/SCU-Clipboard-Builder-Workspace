import io
import os
import re
import sys
import tempfile
from datetime import datetime

import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics


# --- CONFIGURATION & CONSTANTS ---
TOP_SHEET_FILENAME = "top_sheet.pdf"
REQUIRED_FORMS = [
    "medical_consent.pdf",
    "vitals_sheet.pdf",
    "patient_synopsis.pdf",
    "post_visit_instructions.pdf",
]
PACKET_FORM_ORDER = [
    TOP_SHEET_FILENAME,
    "medical_consent.pdf",
    "initial_visit_intake.pdf",
    "annual_demographics.pdf",
    "caremessage_consent.pdf",
    "specialty_clinic_consent.pdf",
    "phq9.pdf",
    "gad7.pdf",
    "tb_form.pdf",
    "welcome_packet.pdf",
    "vitals_sheet.pdf",
    "patient_synopsis.pdf",
    "post_visit_instructions.pdf",
]

ANNUAL_FORMS_MAP = {
    "PHQ": "phq9.pdf",
    "GAD": "gad7.pdf",
    "Demographics": "annual_demographics.pdf",
    "Specialty Clinics Consent": "specialty_clinic_consent.pdf",
    "Care Message": "caremessage_consent.pdf",
    "TB": "tb_form.pdf",
}

EXCEPTION_FORMS_MAP = {
    "Initial Visit Intake": "initial_visit_intake.pdf",
    "Welcome Packet": "welcome_packet.pdf",
}

INPUT_GRID_HEADERS = [
    "Time",
    "Patient Name",
    "DOB",
    "Room",
    "Language",
    "Initial Visit Intake",
    "Annual Demographics",
    "Specialty Clinics Consent",
    "Care Message",
    "PHQ 2-9",
    "GAD 7",
    "TB",
    "Welcome Packet",
]


class PDFProcessor:
    @staticmethod
    def _included_form_label(filename, source_bucket, requested_language):
        stem = os.path.splitext(os.path.basename(filename))[0]
        lang = (requested_language or "english").strip().lower() or "english"

        if source_bucket == "requested":
            source_label = lang
        elif source_bucket == "english":
            source_label = "fallback english"
        elif source_bucket == "default":
            source_label = "default fallback"
        else:
            source_label = "missing"

        return f"{stem} ({source_label})"

    @staticmethod
    def _field_rects_from_first_page(reader):
        page = reader.pages[0]
        annots = page.get("/Annots", [])
        rects = {}
        for annot_ref in annots:
            try:
                annot = annot_ref.get_object()
                if str(annot.get("/Subtype")) != "/Widget":
                    continue
                name = annot.get("/T")
                rect = annot.get("/Rect")
                if not name or not rect or len(rect) != 4:
                    continue
                rects[str(name)] = [float(v) for v in rect]
            except Exception:
                continue
        return rects

    @staticmethod
    def _draw_text_in_rect(c, text, rect, font_name="Helvetica-Bold"):
        x1, y1, x2, y2 = rect
        width = max(1.0, x2 - x1)
        height = max(1.0, y2 - y1)
        value = str(text or "")
        if not value:
            return

        # Fit text size to the box width/height.
        size = min(28.0, max(10.0, height * 0.72))
        while size > 7.0 and pdfmetrics.stringWidth(value, font_name, size) > (width - 8.0):
            size -= 0.5

        c.setFont(font_name, size)
        tx = x1 + 4.0
        ty = y1 + max(1.0, (height - size) / 2.0)
        c.drawString(tx, ty, value)

    @staticmethod
    def _candidate_filenames(filename, language_label=None):
        """
        Build preferred filename variants for translated forms.
        Examples for phq9.pdf + mandarin/spanish:
        - phq9 (mandarin).pdf
        - phq9 (spanish).pdf
        - phq9_mandarin.pdf
        - phq9_spanish.pdf
        - phq9-mandarin.pdf
        - phq9-spanish.pdf
        - phq9.pdf
        """
        stem, ext = os.path.splitext(filename)
        candidates = []
        label = (language_label or "").strip().lower()
        if label:
            candidates.extend(
                [
                    f"{stem} ({label}){ext}",
                    f"{stem}_{label}{ext}",
                    f"{stem}-{label}{ext}",
                ]
            )
        candidates.append(filename)
        return candidates

    @staticmethod
    def resolve_form_path(base_dir, lang_code, filename):
        """
        Resolve a form path and report which language bucket was used.
        Returns: (path_or_none, source_bucket)
        source_bucket in {"requested", "default", "english", "missing"}.
        """
        lang = (lang_code or "").strip().lower()

        search_paths = []
        for candidate in PDFProcessor._candidate_filenames(filename, lang):
            search_paths.append((os.path.join(base_dir, lang, candidate), "requested"))

        for candidate in PDFProcessor._candidate_filenames(filename):
            search_paths.append((os.path.join(base_dir, "default", candidate), "default"))

        for candidate in PDFProcessor._candidate_filenames(filename, "english"):
            search_paths.append((os.path.join(base_dir, "english", candidate), "english"))

        for path, source in search_paths:
            if os.path.exists(path):
                return path, source
        return None, "missing"

    @staticmethod
    def get_form_path(base_dir, lang_code, filename):
        """Backwards-compatible path-only resolver."""
        path, _ = PDFProcessor.resolve_form_path(base_dir, lang_code, filename)
        return path

    @staticmethod
    def create_personalized_top_sheet(template_path, output_path, patient_data, included_forms=None):
        """
        Fill top sheet by drawing text into field rectangles.
        This avoids interactive-form quirks in merged/batch PDFs.
        """
        field_values = {
            "Patient Name": str(patient_data.get("name", "")),
            "Date of Birth": str(patient_data.get("dob", "")),
            "Room Number": str(patient_data.get("room", "")),
            "Language": str(patient_data.get("language", "")).title(),
        }
        included_forms = included_forms or []

        reader = PdfReader(template_path)
        if not reader.pages:
            raise ValueError("Top sheet template has no pages.")
        first_page = reader.pages[0]
        width = float(first_page.mediabox.width)
        height = float(first_page.mediabox.height)

        overlay_stream = io.BytesIO()
        c = canvas.Canvas(overlay_stream, pagesize=(width, height))

        rects = PDFProcessor._field_rects_from_first_page(reader)
        if rects:
            for key, value in field_values.items():
                rect = rects.get(key)
                if rect:
                    PDFProcessor._draw_text_in_rect(c, value, rect)

            # Add compact included-forms list below DOB area.
            dob_rect = rects.get("Date of Birth")
            name_rect = rects.get("Patient Name")
            if dob_rect and name_rect:
                list_x = max(36.0, name_rect[0])
                list_y = dob_rect[1] - 18.0
                c.setFont("Helvetica-Bold", 9)
                c.drawString(list_x, list_y, "Included Forms:")
                c.setFont("Helvetica", 8)
                y = list_y - 12.0
                for form in included_forms:
                    if form == TOP_SHEET_FILENAME:
                        continue
                    if y < 185.0:
                        c.drawString(list_x, y, "...")
                        break
                    c.drawString(list_x, y, f"- {form}")
                    y -= 10.0
        else:
            # Last-resort fallback if no widget rects are discoverable.
            c.setFont("Helvetica-Bold", 18)
            c.drawString(width * 0.81, height * 0.77, field_values["Room Number"])
            c.drawString(width * 0.24, height * 0.39, field_values["Patient Name"])
            c.drawString(width * 0.23, height * 0.23, field_values["Date of Birth"])
            c.drawString(width * 0.63, height * 0.23, field_values["Language"])
        c.save()
        overlay_stream.seek(0)

        overlay_page = PdfReader(overlay_stream).pages[0]
        first_page.merge_page(overlay_page)

        writer = PdfWriter()
        writer.add_page(first_page)
        for page in reader.pages[1:]:
            writer.add_page(page)
        with open(output_path, "wb") as out:
            writer.write(out)


class ClinicApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SCU Clipboard Builder")
        self.resize(1000, 700)

        self.forms_dir = self._default_forms_dir()
        self.patient_data = []
        self._suppress_auto_preview = False
        self.init_ui()

    @staticmethod
    def _resource_base_dir():
        """
        Resolve resource root for both dev runs and PyInstaller builds.
        """
        script_dir = os.path.dirname(os.path.abspath(__file__))
        if not getattr(sys, "frozen", False):
            return script_dir

        exe_dir = os.path.dirname(sys.executable)
        resource_candidates = [
            getattr(sys, "_MEIPASS", ""),
            os.path.normpath(os.path.join(exe_dir, "..", "Resources")),
            exe_dir,
            script_dir,
        ]
        for candidate in resource_candidates:
            if candidate and os.path.isdir(candidate):
                return candidate
        return exe_dir

    @staticmethod
    def _default_forms_dir():
        resource_base = ClinicApp._resource_base_dir()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        candidates = [
            os.path.join(resource_base, "ClinicForms"),
            os.path.join(resource_base, "APP SOURCE", "ClinicForms"),
            os.path.join(script_dir, "ClinicForms"),
            os.path.join(script_dir, "APP SOURCE", "ClinicForms"),
        ]
        for candidate in candidates:
            if os.path.isdir(candidate):
                return candidate
        return ""

    def init_ui(self):
        main_widget = QWidget()
        self.layout = QVBoxLayout(main_widget)
        self.setStyleSheet(
            """
            QMainWindow, QWidget { background-color: #03191a; color: #e9f2ee; }
            QPushButton {
                background-color: #06342b;
                color: #ffffff;
                border: 1px solid #0f604a;
                border-radius: 6px;
                padding: 6px 10px;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #084536; }
            QPushButton:disabled {
                background-color: #1a2a27;
                color: #7c9a90;
                border: 1px solid #2a3b37;
            }
            QHeaderView::section {
                background-color: #052823;
                color: #9ec7b9;
                font-weight: 700;
                border: 1px solid #0e342c;
                padding: 4px;
            }
            QTreeWidget, QTableWidget, QTextEdit {
                background-color: #03191a;
                border: 1px solid #0e342c;
            }
            """
        )

        title_label = QLabel("SCU Clipboard Builder")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(
            "font-size: 30px; font-weight: 800; color: #d9822b; letter-spacing: 0.5px;"
        )
        self.logo_label = QLabel()
        self.logo_label.setFixedSize(220, 180)
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setStyleSheet("background: transparent; border: none;")
        self._load_logo_image()

        title_row = QHBoxLayout()
        title_row.addStretch()
        title_row.addWidget(title_label)
        title_row.addStretch()
        title_row.addWidget(self.logo_label)
        self.layout.addLayout(title_row)

        top_bar = QHBoxLayout()
        self.btn_paste = QPushButton("Paste Into Spreadsheet")
        self.btn_paste.clicked.connect(self.paste_into_input_grid)
        self.btn_paste.setStyleSheet(
            "background-color: #06342b; border: 1px solid #0f604a; color: #ffffff;"
        )
        self.btn_build = QPushButton("Build Patient Preview")
        self.btn_build.clicked.connect(self.build_patients_from_input_grid)
        self.btn_build.setStyleSheet(
            "background-color: #052823; border: 1px solid #0f604a; color: #ffffff;"
        )
        self.btn_clear_grid = QPushButton("Clear Spreadsheet")
        self.btn_clear_grid.clicked.connect(self.clear_input_grid)

        self.btn_folder = QPushButton("Select Forms Folder")
        self.btn_folder.clicked.connect(self.select_forms_folder)
        self.lbl_folder = QLabel(
            os.path.basename(self.forms_dir) if self.forms_dir else "No folder selected"
        )

        top_bar.addWidget(self.btn_paste)
        top_bar.addWidget(self.btn_build)
        top_bar.addWidget(self.btn_clear_grid)
        top_bar.addWidget(self.btn_folder)
        top_bar.addWidget(self.lbl_folder)
        top_bar.addStretch()

        self.input_table = QTableWidget(60, len(INPUT_GRID_HEADERS))
        self.input_table.setHorizontalHeaderLabels(INPUT_GRID_HEADERS)
        self.input_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.input_table.setMinimumHeight(260)
        self.input_table.setToolTip(
            "Paste your schedule directly here (including header row). "
            "Click 'Build Patient Preview' when ready."
        )
        self.input_table.itemChanged.connect(self._on_input_table_changed)

        self.preview_tree = QTreeWidget()
        self.preview_tree.setHeaderLabels(["Patient", "Details"])
        self.preview_tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.preview_tree.header().setSectionResizeMode(1, QHeaderView.Stretch)
        self.preview_tree.setMinimumHeight(180)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setMaximumHeight(160)
        self.log_box.setPlaceholderText("System Log...")

        actions = QHBoxLayout()
        self.btn_generate = QPushButton("Generate Individual PDFs")
        self.btn_batch = QPushButton("Generate Batch Print File")
        self.btn_clear = QPushButton("Clear Session (Privacy)")
        self.btn_generate.clicked.connect(lambda: self.process_pdfs(batch=False))
        self.btn_batch.clicked.connect(lambda: self.process_pdfs(batch=True))
        self.btn_clear.clicked.connect(self.clear_session)

        actions.addWidget(self.btn_generate)
        actions.addWidget(self.btn_batch)
        actions.addStretch()
        actions.addWidget(self.btn_clear)

        input_label = QLabel("Input Spreadsheet (paste/edit here):")
        input_label.setStyleSheet("font-weight: 700; color: #178463;")
        preview_label = QLabel("Patient Preview (what forms each patient gets):")
        preview_label.setStyleSheet("font-weight: 700; color: #178463;")

        self.layout.addLayout(top_bar)
        self.layout.addWidget(input_label)
        self.layout.addWidget(self.input_table)
        self.layout.addWidget(preview_label)
        self.layout.addWidget(self.preview_tree)
        self.layout.addWidget(self.log_box)
        self.layout.addLayout(actions)
        self.setCentralWidget(main_widget)
        if self.forms_dir:
            self.log(f"Forms folder auto-selected: {self._display_forms_path(self.forms_dir)}")

    def _load_logo_image(self):
        resource_base = self._resource_base_dir()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        logo_candidates = [
            os.path.join(resource_base, "white_logo_ui.png"),
            os.path.join(script_dir, "white_logo_ui.png"),
            os.path.join(resource_base, "logo.png"),
            os.path.join(resource_base, "logo.jpg"),
            os.path.join(resource_base, "logo.jpeg"),
            os.path.join(resource_base, "logo.webp"),
            os.path.join(script_dir, "logo.png"),
            os.path.join(script_dir, "logo.jpg"),
            os.path.join(script_dir, "logo.jpeg"),
            os.path.join(script_dir, "logo.webp"),
        ]

        for path in logo_candidates:
            if not os.path.exists(path):
                continue
            pixmap = QPixmap(path)
            if pixmap.isNull():
                continue
            # Render logo at device pixel ratio for sharper Retina/HiDPI output.
            dpr = max(1.0, self.devicePixelRatioF())
            target_logical_px = 168
            target_physical_w = int(target_logical_px * dpr)
            target_physical_h = int(target_logical_px * dpr)
            hi_res = pixmap.scaled(
                target_physical_w,
                target_physical_h,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            hi_res.setDevicePixelRatio(dpr)
            self.logo_label.setPixmap(hi_res)
            self.logo_label.setToolTip(os.path.basename(path))
            self.logo_label.show()
            return

        # Hide the logo slot until a logo file is added.
        self.logo_label.hide()

    def log(self, msg, level="INFO"):
        self.log_box.append(f"[{level}] {msg}")

    @staticmethod
    def _display_forms_path(path):
        """
        Avoid showing user home paths in UI logs.
        """
        marker = "SCU_Clipboard_Builder.app/Contents/Frameworks/ClinicForms"
        if marker in path:
            return marker
        if path.endswith("/ClinicForms") or path.endswith("\\ClinicForms"):
            return "ClinicForms"
        return os.path.basename(path) or "ClinicForms"

    def select_forms_folder(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Forms Folder")
        if dir_path:
            self.forms_dir = dir_path
            self.lbl_folder.setText(os.path.basename(dir_path))
            self.log(f"Forms folder set: {self._display_forms_path(dir_path)}")
            if self.patient_data:
                self.preview_tree.clear()
                for patient in self.patient_data:
                    self.add_preview_item(patient)
                self.log("Patient preview refreshed with resolved form paths.")

    def paste_into_input_grid(self):
        text = QApplication.clipboard().text()
        if not text.strip():
            QMessageBox.warning(self, "Error", "Clipboard is empty! Copy your data first.")
            return

        rows = [r.split("\t") for r in text.replace("\r\n", "\n").strip("\n").split("\n")]
        while rows and not any(str(cell).strip() for cell in rows[0]):
            rows.pop(0)
        if not rows:
            QMessageBox.warning(self, "Error", "Clipboard only contained blank rows.")
            return
        start_row = max(self.input_table.currentRow(), 0)
        start_col = max(self.input_table.currentColumn(), 0)

        pasted_headers = rows[0] if rows and self._is_header_like_row(rows[0]) else None
        data_rows = rows[1:] if pasted_headers else rows

        target_headers = []
        for c in range(self.input_table.columnCount()):
            header_item = self.input_table.horizontalHeaderItem(c)
            target_headers.append(header_item.text() if header_item else "")

        source_to_target = []
        ignored_headers = []
        ignored_source_indices = []
        if pasted_headers:
            for source_idx, source_header in enumerate(pasted_headers):
                mapped_idx = self._target_col_for_pasted_header(source_header)
                if mapped_idx < 0:
                    ignored_headers.append(str(source_header).strip())
                    ignored_source_indices.append(source_idx)
                source_to_target.append(mapped_idx)

        self._suppress_auto_preview = True
        if pasted_headers and start_row == 0 and start_col == 0:
            self.input_table.clearContents()
        for r_idx, row_values in enumerate(data_rows):
            target_row = start_row + r_idx
            if target_row >= self.input_table.rowCount():
                self.input_table.insertRow(self.input_table.rowCount())
            for c_idx, value in enumerate(row_values):
                if pasted_headers:
                    if c_idx >= len(source_to_target):
                        continue
                    target_col = source_to_target[c_idx]
                else:
                    target_col = start_col + c_idx
                if target_col >= self.input_table.columnCount():
                    continue
                if target_col < 0:
                    continue
                self.input_table.setItem(target_row, target_col, QTableWidgetItem(value.strip()))
        self._suppress_auto_preview = False

        if pasted_headers:
            self.log("Pasted spreadsheet using detected header row to align columns.")
            swapped_headers = []
            for source_idx, source_header in enumerate(pasted_headers):
                if source_idx >= len(source_to_target):
                    continue
                target_idx = source_to_target[source_idx]
                if target_idx >= 0 and target_idx != source_idx:
                    swapped_headers.append(
                        f"{source_header} -> {target_headers[target_idx]}"
                    )

            column_check_lines = []
            if swapped_headers:
                column_check_lines.append(
                    "The app used the pasted header row to re-align the incoming data into the correct app columns."
                )
                column_check_lines.append(
                    "The following pasted columns were moved to match the expected clipboard layout:"
                )
                column_check_lines.append("")
                column_check_lines.extend(f"- {item}" for item in swapped_headers)
            else:
                column_check_lines.append("All recognized columns match the app layout.")
                column_check_lines.append("")
                column_check_lines.append(
                    "No column moves were needed. The pasted data already matches the expected clipboard columns."
                )

            QMessageBox.information(
                self,
                "Column Check",
                "\n".join(column_check_lines),
            )

            affected_names = []
            patient_name_source_idx = -1
            for idx, source_header in enumerate(pasted_headers):
                if self._target_col_for_pasted_header(source_header) == 1:
                    patient_name_source_idx = idx
                    break

            if patient_name_source_idx >= 0:
                for row_values in data_rows:
                    has_ignored_mark = any(
                        ignored_idx < len(row_values) and self._is_marked(row_values[ignored_idx])
                        for ignored_idx in ignored_source_indices
                    )
                    if not has_ignored_mark:
                        continue
                    if patient_name_source_idx < len(row_values):
                        patient_name = row_values[patient_name_source_idx].strip()
                        if patient_name and patient_name not in affected_names:
                            affected_names.append(patient_name)

            if ignored_headers:
                ignored_message = (
                    "Ignored pasted columns with no matching app column: "
                    + ", ".join(ignored_headers)
                )
                self.log(ignored_message, "WARNING")
                popup_lines = [ignored_message, "", "Those columns were not pasted into the app grid."]

                if affected_names:
                    if len(affected_names) == 1:
                        popup_lines.append("")
                        popup_lines.append(
                            f"Please add this form to the clipboard for {affected_names[0]}."
                        )
                    else:
                        popup_lines.append("")
                        popup_lines.append(
                            "Please add this form to the clipboard for: "
                            + ", ".join(affected_names)
                            + "."
                        )

                QMessageBox.information(
                    self,
                    "Ignored Columns",
                    "\n".join(popup_lines),
                )
        else:
            self.log("Pasted clipboard data into input spreadsheet.")
            QMessageBox.warning(
                self,
                "Include Headers",
                "Please copy and paste the spreadsheet including the top row column headers.\n\n"
                "The app uses the headers to confirm whether columns match the expected layout "
                "or need to be re-aligned.",
            )
        self._maybe_prompt_shifted_columns()
        self._refresh_preview_from_grid()

    def clear_input_grid(self):
        self._suppress_auto_preview = True
        self.input_table.clearContents()
        self._suppress_auto_preview = False
        self.patient_data = []
        self.preview_tree.clear()
        self.log("Input spreadsheet cleared.")

    def _collect_input_grid(self):
        rows = []
        for r in range(self.input_table.rowCount()):
            row_vals = []
            has_content = False
            for c in range(self.input_table.columnCount()):
                item = self.input_table.item(r, c)
                val = item.text().strip() if item else ""
                if val:
                    has_content = True
                row_vals.append(val)
            if has_content:
                rows.append(row_vals)
        return rows

    def _grid_headers_and_data_rows(self):
        rows = self._collect_input_grid()
        default_headers = []
        for c in range(self.input_table.columnCount()):
            header_item = self.input_table.horizontalHeaderItem(c)
            default_headers.append(header_item.text() if header_item else "")

        if rows and self._is_header_like_row(rows[0]):
            headers = [str(v).strip() for v in rows[0]]
            data_rows = rows[1:]
        else:
            headers = default_headers
            data_rows = rows
        return rows, headers, data_rows

    @staticmethod
    def _normalize(s):
        return (s or "").strip().lower()

    @staticmethod
    def _target_col_for_pasted_header(source_header):
        normalized_source = ClinicApp._normalize(source_header)
        header_aliases = [
            ["time"],
            ["patient name", "name"],
            ["date of birth", "dob"],
            ["room"],
            ["language"],
            ["initial visit intake"],
            ["annual demographics", "demographics"],
            ["specialty clinics consent", "specialty clinic"],
            ["care message", "caremessage"],
            ["phq 2-9", "phq-9", "phq"],
            ["gad 7", "gad-7", "gad"],
            ["tb"],
            ["welcome packet education", "welcome packet"],
        ]
        for idx, aliases in enumerate(header_aliases):
            if any(alias in normalized_source or normalized_source in alias for alias in aliases):
                return idx
        return -1

    @staticmethod
    def _is_marked(value):
        """
        Treat any non-blank cell as selected.
        This allows values like 'x', 'need', 'fill', etc. to count.
        """
        v = ClinicApp._normalize(value)
        return v not in {"", "nan"}

    @staticmethod
    def _find_col(headers, aliases):
        for i, header in enumerate(headers):
            h = ClinicApp._normalize(header)
            for alias in aliases:
                if alias in h:
                    return i
        return -1

    @staticmethod
    def _normalize_language(value):
        raw = str(value or "").strip()
        if not raw:
            return "english"

        lowered = raw.lower().strip()
        if lowered == "nan":
            return "english"

        # Split common multi-language separators: comma, slash, semicolon, pipe, &, "and"
        tokens = [
            t.strip()
            for t in re.split(r"[,\|;/]+|&|\band\b", lowered)
            if t and t.strip()
        ]
        if not tokens:
            tokens = [lowered]

        # Priority rule: if English appears anywhere, default to English.
        for token in tokens:
            if token in {"en", "eng", "english"} or "english" in token:
                return "english"

        # Next most common mapping.
        for token in tokens:
            if token in {"es", "spa", "spanish", "espanol", "español"} or "spanish" in token:
                return "spanish"
            if token in {"zh", "chi", "zho", "chinese", "mandarin"} or "mandarin" in token or "chinese" in token:
                return "mandarin"

        # Otherwise, keep first token normalized for folder lookup (fallback still works).
        normalized = re.sub(r"\s+", " ", tokens[0]).strip()
        return normalized or "english"

    @staticmethod
    def _ordered_packet_forms(selected_forms):
        selected_set = set(selected_forms)
        required_set = set(REQUIRED_FORMS)
        ordered = []
        for fname in PACKET_FORM_ORDER:
            if fname == TOP_SHEET_FILENAME:
                ordered.append(fname)
                continue
            if fname in required_set or fname in selected_set:
                ordered.append(fname)

        # Safety: include any newly-added required/selected forms not in PACKET_FORM_ORDER.
        for fname in REQUIRED_FORMS:
            if fname not in ordered:
                ordered.append(fname)

        # Any extra selected forms not explicitly mapped in PACKET_FORM_ORDER
        # are placed before vitals to match clinic workflow.
        extras = [fname for fname in selected_forms if fname not in ordered]
        if extras:
            vitals_idx = ordered.index("vitals_sheet.pdf") if "vitals_sheet.pdf" in ordered else len(ordered)
            for fname in extras:
                ordered.insert(vitals_idx, fname)
                vitals_idx += 1
        return ordered

    @staticmethod
    def _is_header_like_row(row_vals):
        normalized = [ClinicApp._normalize(v) for v in row_vals]
        header_markers = ["patient name", "name", "dob", "date of birth", "room", "language"]
        return any(any(marker in val for marker in header_markers) for val in normalized)

    @staticmethod
    def _looks_like_date(text):
        t = str(text or "").strip()
        if not t:
            return False
        # Very permissive date-like check used only for column-shift heuristics.
        return any(ch.isdigit() for ch in t) and ("/" in t or "-" in t)

    @staticmethod
    def _likely_left_shifted_input(data_rows, col_name):
        sample_rows = data_rows[: min(6, len(data_rows))]
        if not sample_rows or col_name <= 0:
            return False

        name_col_date_like = 0
        left_col_nonempty = 0
        for row_vals in sample_rows:
            v_name = row_vals[col_name] if col_name < len(row_vals) else ""
            v_left = row_vals[col_name - 1] if (col_name - 1) < len(row_vals) else ""
            if ClinicApp._looks_like_date(v_name):
                name_col_date_like += 1
            if str(v_left).strip():
                left_col_nonempty += 1

        return (
            name_col_date_like >= max(2, len(sample_rows) // 2)
            and left_col_nonempty >= max(2, len(sample_rows) // 2)
        )

    def _shift_input_grid_right(self):
        col_count = self.input_table.columnCount()
        headers = []
        logged_top_row = False
        self._suppress_auto_preview = True
        for c in range(col_count):
            header_item = self.input_table.horizontalHeaderItem(c)
            headers.append(header_item.text() if header_item else f"Column {c + 1}")

        for r in range(self.input_table.rowCount()):
            row_values = []
            for c in range(col_count):
                item = self.input_table.item(r, c)
                row_values.append(item.text().strip() if item else "")

            if not any(row_values):
                continue

            if not logged_top_row:
                dropped_value = row_values[-1]
                for c in range(col_count - 2, -1, -1):
                    value = row_values[c]
                    if value:
                        self.log(
                            f"{value} - was shifted Right 1 column to match - {headers[c + 1]}"
                        )
                if dropped_value:
                    self.log(
                        f"{dropped_value} - could not be shifted Right 1 column because it is already in the last column ({headers[-1]}).",
                        "WARNING",
                    )
                logged_top_row = True

            shifted = [""] + row_values[: col_count - 1]
            for c, value in enumerate(shifted):
                self.input_table.setItem(r, c, QTableWidgetItem(value))
        self._suppress_auto_preview = False

        self.log("Shifted spreadsheet one column to the right.")

    def _maybe_prompt_shifted_columns(self):
        rows, headers, data_rows = self._grid_headers_and_data_rows()
        if not rows or not data_rows:
            return
        if self._is_header_like_row(rows[0]):
            return

        col_name = self._find_col(headers, ["patient name", "name"])
        if col_name < 0 or not self._likely_left_shifted_input(data_rows, col_name):
            return

        choice = QMessageBox.question(
            self,
            "Shift Columns?",
            "The pasted spreadsheet looks shifted one column to the left, "
            "likely because the Time column was omitted.\n\n"
            "Would you like to shift the visible spreadsheet one column to "
            "the right now?\n\n"
            "Choose No to keep the grid exactly as pasted.",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
            QMessageBox.Yes,
        )
        if choice == QMessageBox.Yes:
            self._shift_input_grid_right()
            self._refresh_preview_from_grid()
            return
        if choice == QMessageBox.No:
            self.log(
                "Detected left-shifted spreadsheet after paste, but kept input unchanged because shift was declined.",
                "WARNING",
            )

    def _refresh_preview_from_grid(self):
        rows = self._collect_input_grid()
        if not rows:
            self.patient_data = []
            self.preview_tree.clear()
            return False
        return self.build_patients_from_input_grid()

    def _on_input_table_changed(self, _item):
        if self._suppress_auto_preview:
            return
        self._refresh_preview_from_grid()

    def build_patients_from_input_grid(self):
        try:
            rows, headers, data_rows = self._grid_headers_and_data_rows()
            if not rows:
                QMessageBox.warning(self, "Error", "Input spreadsheet is empty.")
                return False
            if not data_rows:
                QMessageBox.warning(self, "Error", "No patient rows found in spreadsheet.")
                return False

            col_name = self._find_col(headers, ["patient name", "name"])
            col_dob = self._find_col(headers, ["date of birth", "dob"])
            col_room = self._find_col(headers, ["room"])
            col_language = self._find_col(headers, ["language"])

            if col_name < 0:
                QMessageBox.warning(self, "Error", "Could not find a Name/Patient Name column.")
                return False

            form_col_aliases = {
                "Initial Visit Intake": ["initial visit intake"],
                "Demographics": ["annual demographics", "demographics"],
                "Specialty Clinics Consent": ["specialty clinics consent", "specialty clinic"],
                "Care Message": ["care message", "caremessage"],
                "PHQ": ["phq 2-9", "phq-9", "phq"],
                "GAD": ["gad 7", "gad-7", "gad"],
                "TB": ["tb"],
                "Welcome Packet": ["welcome packet education", "welcome packet"],
            }
            form_col_idxs = {
                key: self._find_col(headers, aliases)
                for key, aliases in form_col_aliases.items()
            }

            self.patient_data = []
            self.preview_tree.clear()

            for row_vals in data_rows:
                name_val = row_vals[col_name].strip() if col_name < len(row_vals) else ""
                if not name_val:
                    continue
                if self._normalize(name_val) == "al demo":
                    continue
                if "pts" in name_val.lower():
                    continue

                dob_val = row_vals[col_dob].strip() if 0 <= col_dob < len(row_vals) else ""
                room_val = row_vals[col_room].strip() if 0 <= col_room < len(row_vals) else ""
                lang_raw = row_vals[col_language].strip() if 0 <= col_language < len(row_vals) else ""

                p = {
                    "name": name_val,
                    "dob": "" if self._normalize(dob_val) == "nan" else dob_val,
                    "room": "" if self._normalize(room_val) == "nan" else room_val,
                    "language": self._normalize_language(lang_raw),
                    "selected_forms": [],
                }

                for form_key, filename in {**ANNUAL_FORMS_MAP, **EXCEPTION_FORMS_MAP}.items():
                    idx = form_col_idxs.get(form_key, -1)
                    if idx < 0 or idx >= len(row_vals):
                        continue
                    if self._is_marked(row_vals[idx]):
                        p["selected_forms"].append(filename)

                self.patient_data.append(p)
                self.add_preview_item(p)

            self.log(f"Built patient preview for {len(self.patient_data)} patients.")
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to build patient preview: {e}")
            return False

    def add_preview_item(self, p):
        ordered_forms = self._ordered_packet_forms(p["selected_forms"])
        total_forms = len(ordered_forms)

        patient_details = (
            f"DOB: {p['dob']} | Room: {p['room']} | "
            f"Language: {p['language'].title()} | Total Forms: {total_forms}"
        )
        patient_item = QTreeWidgetItem([p["name"], patient_details])
        patient_item.setForeground(0, QBrush(QColor("#d9822b")))
        self.preview_tree.addTopLevelItem(patient_item)

        for idx, form_name in enumerate(ordered_forms, start=1):
            if self.forms_dir:
                _, source = PDFProcessor.resolve_form_path(
                    self.forms_dir, p["language"], form_name
                )
                if source == "requested":
                    status = f"{p['language']}"
                elif source == "default":
                    status = "default fallback"
                elif source == "english":
                    status = "english fallback"
                else:
                    status = "missing"
                label = f"{idx}. {form_name} ({status})"
            else:
                label = f"{idx}. {form_name} (select forms folder to resolve)"
            child = QTreeWidgetItem([label, ""])
            patient_item.addChild(child)

        patient_item.setExpanded(True)

    def clear_session(self):
        self.patient_data = []
        self.preview_tree.clear()
        self.log_box.clear()
        self.log("Session cleared. All PHI removed from memory.")

    def process_pdfs(self, batch=False):
        if not self.forms_dir:
            QMessageBox.warning(self, "Error", "Please select a forms folder first.")
            return
        if not self.build_patients_from_input_grid():
            return
        if not self.patient_data:
            QMessageBox.warning(self, "Error", "No patients imported.")
            return

        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Save Location")
        if not output_dir:
            return

        batch_writer = PdfWriter() if batch else None

        for p in self.patient_data:
            temp_top_sheet = None
            try:
                template = PDFProcessor.get_form_path(
                    self.forms_dir, p["language"], TOP_SHEET_FILENAME
                )
                if not template:
                    self.log(
                        f"Missing {TOP_SHEET_FILENAME} for {p['name']} (Lang: {p['language']})",
                        "WARNING",
                    )
                    continue

                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
                    temp_top_sheet = temp.name
                ordered_forms = self._ordered_packet_forms(p["selected_forms"])
                included_form_labels = []
                for fname in ordered_forms:
                    if fname == TOP_SHEET_FILENAME:
                        continue
                    _, source = PDFProcessor.resolve_form_path(self.forms_dir, p["language"], fname)
                    included_form_labels.append(
                        PDFProcessor._included_form_label(fname, source, p["language"])
                    )
                PDFProcessor.create_personalized_top_sheet(
                    template, temp_top_sheet, p, included_forms=included_form_labels
                )

                packet_writer = PdfWriter()
                packet_writer.append(temp_top_sheet)

                for fname in ordered_forms:
                    if fname == TOP_SHEET_FILENAME:
                        continue
                    fpath = PDFProcessor.get_form_path(self.forms_dir, p["language"], fname)
                    if fpath:
                        packet_writer.append(fpath)
                    else:
                        self.log(
                            f"Missing {fname} for {p['name']} (Lang: {p['language']})",
                            "WARNING",
                        )

                safe_name = p["name"].replace(" ", "_").replace(",", "")
                safe_dob = p["dob"].replace("/", "-")
                filename = f"Room_{p['room']}__{safe_name}__DOB_{safe_dob}.pdf"
                final_path = os.path.join(output_dir, filename)

                if batch:
                    for page in packet_writer.pages:
                        batch_writer.add_page(page)
                else:
                    with open(final_path, "wb") as f:
                        packet_writer.write(f)
            except Exception as e:
                self.log(f"Error processing {p['name']}: {e}", "ERROR")
            finally:
                if temp_top_sheet and os.path.exists(temp_top_sheet):
                    os.remove(temp_top_sheet)

        if batch:
            batch_path = os.path.join(
                output_dir, f"Batch_Print_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            )
            with open(batch_path, "wb") as f:
                batch_writer.write(f)
            self.log(f"Batch file generated: {batch_path}")
        else:
            self.log("All individual PDFs generated.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ClinicApp()
    window.show()
    sys.exit(app.exec())
