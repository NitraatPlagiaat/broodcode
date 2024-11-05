def get_max_widths(rows):
    """Calculate maximum column width based on longest string in each column."""
    return [max(len(str(item)) for item in col) for col in zip(*rows, strict=False)]


def format_row(row_items, col_widths):
    """Format a row with variable column width based on longest content."""
    return (
        "|"
        + "|".join(f"{str(item):<{col_widths[i]}}" for i, item in enumerate(row_items))
        + "|"
    )


def format_separator(col_widths):
    """Create a separator row based on column widths for Markdown table."""
    return "|" + "|".join("-" * col_width for col_width in col_widths) + "|"


def print_header(title):
    print(f"## {title}\n")