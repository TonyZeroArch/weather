def convert_temperature(celsius, target_unit):
    """
    Convert temperature from Celsius to the target unit.

    Args:
        celsius: Temperature in Celsius
        target_unit: Target unit ("C" for Celsius, "F" for Fahrenheit)

    Returns:
        Converted temperature value
    """
    if target_unit == "C":
        return celsius
    elif target_unit == "F":
        return (celsius * 9 / 5) + 32
    else:
        raise ValueError(f"Unsupported temperature unit: {target_unit}")
