# Google Sheets Data Methods - Complete Reference

## Problem
The original error was caused by improper data formatting when using `sheet.append_rows(data)`. The API expects the data structure to be properly formatted.

## Data Format
Always use a **list of lists** structure:
```python
data = [
    [col1_value, col2_value, col3_value],  # Row 1
    [col1_value, col2_value, col3_value],  # Row 2
]
```

NOT:
```python
data = [col1, col2, col3]  # This is WRONG - it's a single list, not list of lists
```

## Method 1: `sheet.append_rows(data)` ⭐ SIMPLEST
**Best for:** Appending multiple rows quickly at the end of the sheet

```python
data = [
    ["Job1", "Company1", "NYC"],
    ["Job2", "Company2", "LA"],
]
sheet.append_rows(data)
```

**Pros:**
- Simple and straightforward
- Automatically finds the next empty row
- Good for multiple rows

**Cons:**
- Can have formatting issues with certain data types
- Less control over placement

---

## Method 2: `sheet.append_row(row)` - SINGLE ROW
**Best for:** Appending one row at a time

```python
row = ["Job1", "Company1", "NYC"]
sheet.append_row(row)
```

**Pros:**
- Good for processing one row at a time
- Reliable for single rows

**Cons:**
- Slower for multiple rows (multiple API calls)
- Not ideal for batch operations

---

## Method 3: `sheet.update_cell(row, col, value)` - SINGLE CELL
**Best for:** Updating specific cells

```python
sheet.update_cell(2, 1, "Job Title")  # Row 2, Column 1
sheet.update_cell(2, 2, "Company Name")
```

**Pros:**
- Precise control
- Good for updates

**Cons:**
- Multiple API calls for multiple cells
- Not ideal for bulk data

---

## Method 4: `sheet.insert_row(values, index)` - INSERT AT SPECIFIC ROW
**Best for:** Inserting rows at specific positions (not at the end)

```python
sheet.insert_row(["New Job", "New Company"], index=2)  # Insert at row 2
```

**Pros:**
- Control over row position

**Cons:**
- Shifts existing data down
- Can be slow for large sheets

---

## Method 5: `sheet.batch_update(cell_list)` - ADVANCED BATCH
**Best for:** Complex updates with multiple cells and formatting

```python
from gspread.utils import a1_range_to_grid_range
import gspread

cell_list = [
    gspread.Cell(row=1, col=1, value="Job Title"),
    gspread.Cell(row=1, col=2, value="Company"),
    gspread.Cell(row=2, col=1, value="Job1"),
    gspread.Cell(row=2, col=2, value="Company1"),
]
sheet.batch_update(cell_list)
```

**Pros:**
- Most efficient for large batch operations
- Can include formatting
- Single API call

**Cons:**
- More complex syntax
- Need to construct Cell objects

---

## Method 6: `sheet.batch_clear(ranges)` + `sheet.append_rows()` - CLEAR THEN APPEND
**Best for:** Replacing all data in a sheet

```python
# Clear everything
sheet.batch_clear(['A:Z'])

# Then append new data
sheet.append_rows(data)
```

**Pros:**
- Clean slate approach

**Cons:**
- Deletes all existing data

---

## Recommended Solution for Your Code

**Use this approach with error handling:**

```python
def update_google_sheet(
        google_client: gspread.Client,
        google_sheet_url: str,
        data: list,
        tab_name: None | str = None) -> None:
    
    spreadsheet = google_client.open_by_url(google_sheet_url)
    if tab_name:
        sheet = spreadsheet.worksheet(tab_name)
    else:
        sheet = spreadsheet.get_worksheet(0)

    try:
        # Method A: Direct append_rows (simplest)
        sheet.append_rows(data)
        LOG.debug(f"Data appended to Google Sheet:\n {pprint(data)}")
    except Exception as e:
        LOG.error(f"Error with append_rows: {str(e)}")
        # Fallback: append one row at a time
        for row in data:
            sheet.append_row(row)
        LOG.debug(f"Data appended row by row:\n {pprint(data)}")
```

---

## Quick Comparison Table

| Method | Speed | Simplicity | Use Case |
|--------|-------|-----------|----------|
| `append_rows()` | Fast | Very Simple | Bulk append at end |
| `append_row()` | Slow | Simple | Single row |
| `update_cell()` | Very Slow | Simple | Single cell |
| `insert_row()` | Medium | Simple | Insert at position |
| `batch_update()` | Very Fast | Complex | Advanced batch ops |
| `batch_clear()` + append | Fast | Medium | Replace all data |

---

## Data Format Examples

### ✅ CORRECT - List of Lists
```python
field_data = [
    [
        "job_id_123",
        "Software Engineer",
        "Google",
        "NYC",
        "https://example.com",
        "job description text",
        "requirements",
        "nice to have",
        "02/12/2026",
        "No",
    ]
]
sheet.append_rows(field_data)
```

### ❌ WRONG - Single List
```python
field_data = [
    "job_id_123",
    "Software Engineer",
    "Google",
    # ... This is wrong!
]
```

### ✅ CORRECT - Multiple Rows
```python
field_data = [
    ["Job1", "Company1", "Location1"],  # Row 1
    ["Job2", "Company2", "Location2"],  # Row 2
    ["Job3", "Company3", "Location3"],  # Row 3
]
sheet.append_rows(field_data)
```

---

## Troubleshooting

### Issue: "Invalid value at 'data.values[0]'"
**Solution:** Make sure you're passing `[[data]]` (list of lists), not `[data]` (single list)

### Issue: API Rate Limiting
**Solution:** Use `batch_update()` instead of multiple `append_row()` calls

### Issue: Data appears on wrong rows
**Solution:** Remove manual row insertion (`sheet.insert_row([], index=2)`). Let `append_rows()` find the next empty row automatically.


