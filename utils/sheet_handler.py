import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import SHEET_ID, CREDENTIALS_JSON, COMMENTS_LINK_COLUMN
import pandas as pd

def get_gspread_client():
    """Authorize and return the gspread client."""
    try:
        scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_JSON, scope)
        client = gspread.authorize(creds)
        return client
    except FileNotFoundError:
        print(f"Error: The credentials file '{CREDENTIALS_JSON}' was not found.")
        return None
    except Exception as e:
        print(f"An error occurred while connecting to Google Sheets: {e}")
        return None

def get_all_tabs(client):
    """Returns a list of all worksheet objects from the spreadsheet."""
    if not client:
        return []
    try:
        spreadsheet = client.open_by_key(SHEET_ID)
        return spreadsheet.worksheets()
    except Exception as e:
        print(f"Failed to get tabs from spreadsheet: {e}")
        return []

def get_all_posts(sheet):
    """Fetch all records from a given sheet."""
    if sheet:
        return sheet.get_all_records()
    return []

def update_status_for_post(sheet, row_index, status, comment_count=None, comments_link=None, analyzed_link=None, wordcloud_link=None):
    """Update the status and output links for a specific row in the sheet."""
    if not sheet:
        return
        
    try:
        # Find column numbers dynamically
        headers = sheet.row_values(1)
        status_col = headers.index('Status') + 1
        count_col = headers.index('Comments Count') + 1
        comments_link_col = headers.index(COMMENTS_LINK_COLUMN) + 1
        
        # Update cells
        sheet.update_cell(row_index, status_col, status)
        if comment_count is not None:
            sheet.update_cell(row_index, count_col, comment_count)
        if comments_link:
            sheet.update_cell(row_index, comments_link_col, comments_link)
            
        print(f"Updated sheet '{sheet.title}' for row {row_index}.")
            
    except Exception as e:
        print(f"Failed to update sheet '{sheet.title}' for row {row_index}: {e}")

def update_brand_report_links(sheet, bar_chart_link: str, word_cloud_link: str):
    """Updates the report links in a designated area (e.g., cell A1) of a sheet."""
    if not sheet:
        return
    try:
        # Assuming the links should be placed in a specific, known cell.
        # For example, in cell J1 for the bar chart and K1 for the word cloud.
        # This can be adjusted as needed.
        sheet.update('J1', 'Brand Bar Chart Link')
        sheet.update('K1', bar_chart_link)
        sheet.update('L1', 'Brand Word Cloud Link')
        sheet.update('M1', word_cloud_link)
        print(f"Updated brand report links for sheet '{sheet.title}'.")
    except Exception as e:
        print(f"Failed to update brand report links for sheet '{sheet.title}': {e}") 
