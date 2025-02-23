def check_for_month(date:str, start_month:int, end_month:int) -> bool:
    try:
        date_parts = date.split('.')
        if len(date_parts) < 2:
            exit("ERROR WITH CHECKING FOR MONTH")
        return int(date_parts[1]) >= start_month and int(date_parts[1]) <= end_month
    except ValueError:
            exit("ERROR WITH CHECKING FOR MONTH")