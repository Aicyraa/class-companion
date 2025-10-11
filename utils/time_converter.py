from datetime import datetime, timedelta

class Time_Converter():

    @staticmethod
    def convert_to_24(time: str) -> datetime: # for converting time into 24-hour format

        if ":" in time:
            return datetime.strptime(time, "%I:%M%p").time()
        else:
            return datetime.strptime(time, "%I%p").time()
    
    @staticmethod
    def convert_to_12(time: str) -> datetime: # func for converting 24-hour time into 12 hours format
        total_seconds = int(time.total_seconds())
        hours_24, remainder = divmod(total_seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        hours_12 = hours_24 % 12 or 12   # ensures always positive, converts correctly
        ampm = "AM" if hours_24 < 12 else "PM"
        format = f"{hours_12:2d}:{minutes:02d} {ampm}"
        return format
    
    @staticmethod
    def convert_to_expiry(duration: str) -> datetime:
        now = datetime.now()
        duration = duration.upper().strip()  # make case-insensitive

        # Find all number + unit patterns
        matches = re.findall(r"(\d+)([DHM])", duration)
        if not matches:
            return None

        expiry = now
        for value, unit in matches:
            value = int(value)
            if unit == "D":
                expiry += timedelta(days=value)
            elif unit == "H":
                expiry += timedelta(hours=value)
            elif unit == "M":
                expiry += timedelta(minutes=value)

        return expiry