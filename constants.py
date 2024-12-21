import io
import os
import re
import textwrap
import tempfile
import tkinter as tk
from fpdf import FPDF
from docx import Document
from docx.oxml.ns import qn
from tkinter import filedialog
from docx.shared import Inches
from docx.oxml import parse_xml
from docx.oxml import OxmlElement
from reportlab.lib import colors
from docx.oxml.ns import nsdecls
from reportlab.pdfgen import canvas
import google.generativeai as genai
from abc import ABC, abstractmethod
from docx.shared import Pt, Inches, Cm, Mm
from reportlab.lib.pagesizes import letter
from PIL import Image, ImageDraw, ImageFont
from tkinter import messagebox, scrolledtext
from reportlab.platypus import Table, TableStyle
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from reportlab.lib.styles import getSampleStyleSheet
from docx.enum.table import WD_ROW_HEIGHT_RULE, WD_CELL_VERTICAL_ALIGNMENT

# LLM 
WINDOW_TITLE = "The Crossword Generator"
GOOGLE_API_KEY = 'AIzaSyBsnqVKjUqw3bB3KfvMidDpL1IDUCSvABU'
MODEL = genai.GenerativeModel('gemini-pro')
genai.configure(api_key=GOOGLE_API_KEY)

# Constants 
WIDGET = "widget"
SELECTED = "selected"
DIRECTION_VERTICAL = "vertical"
DIRECTION_HORIZONTAL = "horizontal"

TEXT_COLOR = "black"
DEFAULT_CELL_COLOR = "white"
CROSSWORD_FRAME_BG = "white"
INDEX_BG_COLOR = "lightyellow"
INDEX_OUTLINE_COLOR = "lightyellow"

AUTO_MODE_TEXT = "Auto"
CUSTOM_MODE_TEXT = "Custom"

PLUS = "+"
MINUS = "-"
SOLVE_BUTTON_TEXT = "Solve"
CLEAR_BUTTON_TEXT = "Clear"
THEME_LABEL_TEXT = "Topic:"
EXPORT_BUTTON_TEXT = "Export"
GENERATE_BUTTON_TEXT = "Generate"
WORD_COUNT_LABEL_TEXT = "Number of words:"

STICKY_N="n"
STICKY_EW="ew"
STICKY_NW="nw"
STICKY_NSEW="nsew"

CONTROLS_FRAME_WIDTH = 450
CROSSWORD_FRAME_WIDTH = 615
CROSSWORD_FRAME_HEIGHT = 615

FIRST_ROW = 0
FIRST_COLUMN = 0

SECOND_ROW = 1
SECOND_COLUMN = 1

SIX_COLUMN = 5
THIRD_COLUMN = 2
FIFTH_COLUMN = 4
FOURTH_COLUMN = 3

PADX = 10
WEIGHT = 1
PADX_W = 22
ROWSPAN = 2 
PARENT_PADDING = 15

CELL_TO_MIN = 20
RADIUS_TO_MIN = 2
BUTTON_HEIGHT = 3
GRID_SIZE_STEP = 1
MIN_GRID_SIZE = 15
MAX_GRID_SIZE = 25
DEFAULT_GRID_SIZE = 15

MIN_WORD_LENGTH = 2
SMALL_BUTTON_WIDTH = 2
SMALL_BUTTON_HEIGHT = 1
BUTTON_BORDER_WIDTH = 3  
SMALL_BUTTON_BORDER_WIDTH = 1

FIXED_WIDTH = 600
FIXED_HEIGHT = 600

WORD_COUNT_MIN = 1
WORD_COUNT_MAX = 15
WORD_COUNT_WIDTH = 7

FONT_COLOR = "red"
FONT_STYLE = "bold"
FONT_NAME = "Arial"
FONT_STYLE_SOLID = "solid"

RESULT_TEXT_WIDTH = 90
RESULT_TEXT_HEIGHT = 35

ENTRY_PADDING = 7
SPACER_HEIGHT = 18
RADIOBUTTON_PADDING = 5
ZOOM_BUTTON_PADDING = 1.5

LABEL_FONT = 12 
MIN_FONT_SIZE = 6

AUTO_WELCOME =  (
                "Welcome to Auto Mode!\n"
                "1. Enter a theme for your crossword in the 'Theme' field (20 letters max).\n"
                "2. Specify the number of words you want in the crossword.\n"
                "3. Click 'Generate' to automatically create the crossword.\n"
                "4. Click 'Solve' to solve the crossword puzzle.\n"
                "5. Click 'Clear' to reset the crossword grid and inputs.\n"
                "6. Click 'Export' to save the crossword for sharing or printing.\n"
                "7. Use the '+' button to increase the grid size for a larger crossword.\n"
                "8. Use the '-' button to decrease the grid size for a smaller crossword.\n"
                "Enjoy your crossword creation experience!"
            )
CUSTOM_WELCOME =  (
                "Welcome to Custom Mode!\n"
                "1. Enter a theme for your crossword in the 'Theme' field (20 letters max).\n"
                "2. Enter your own words related to the theme in the 'Words' field.\n"
                "2.1. Ensure that the words match the theme you selected.\n"
                "3. Click 'Generate' to create your custom crossword puzzle.\n"
                "4. Click 'Solve' to solve the crossword puzzle.\n"
                "5. Click 'Clear' to reset the crossword grid and inputs.\n"
                "6. Click 'Export' to save the crossword for sharing or printing.\n"
                "7. Use the '+' button to increase the grid size for a larger crossword.\n"
                "8. Use the '-' button to decrease the grid size for a smaller crossword.\n"
                "Enjoy creating your personalized crossword!\n\n"
                "Enter your own words separated by comma:"
            )