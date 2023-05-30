import time
import xlwings as xw

start_time = time.time()

# Open the Excel file
wb = xw.Book(r"C:\Users\zjin6\Documents\1 WORK\1 TVM Data Analysis\2 Weekly Report\2023 Weekly Report\TVM Report 1 Excel 2023H3.xlsb")

# Do some operations on the workbook here...

# Print all sheet names
for sheet in wb.sheets:
    print(sheet.name)

# Close the workbook
# wb.close()
wb.app.quit()


end_time = time.time()

# Calculate the total time taken
total_time = end_time - start_time

print(f"Total time taken: {total_time:.2f} seconds")


